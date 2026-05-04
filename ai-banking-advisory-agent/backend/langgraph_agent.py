"""
LangGraph Baseline Agent for Equipment Financing Support
Phase 2: Rule-Based Agent with Keyword Categorization & Template Responses

This module implements a LangGraph-based baseline agent that:
- Uses explicit state management (TypedDict-based AgentState)
- Implements 4-node LangGraph workflow
- Demonstrates clear limitations (keyword matching, templates, no memory)
- Logs interactions for Phase 3 comparison
"""

import json
import logging
from typing import Any, Dict, List
from datetime import datetime
from enum import Enum
from typing_extensions import TypedDict
from pathlib import Path
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# STATE MANAGEMENT
# ============================================================================

class AgentState(TypedDict):
    """
    State object that flows through LangGraph nodes.
    
    Fields:
    - query: User input question
    - response: Agent response
    - category: Query category (equipment_rates, terms, etc.)
    - confidence: Confidence score (0.0-1.0)
    - sources: Retrieved documents (empty in baseline)
    - session_id: Session tracking
    - turn_number: Multi-turn counter
    - conversation_history: Previous turns
    - timestamp: ISO timestamp
    - metadata: Custom metadata
    """
    query: str
    response: str
    category: str
    confidence: float
    sources: List[str]
    session_id: str
    turn_number: int
    conversation_history: List[Dict[str, Any]]
    timestamp: str
    metadata: Dict[str, Any]


# ============================================================================
# QUERY CATEGORIES
# ============================================================================

class QueryCategory(Enum):
    """Equipment financing query categories."""
    EQUIPMENT_RATES = "equipment_rates"
    LOAN_TERMS = "loan_terms"
    ELIGIBILITY = "eligibility"
    PROCESS = "process"
    EDUCATION = "education"
    ESCALATION = "escalation"
    REFUSE = "refuse"
    UNKNOWN = "unknown"


# ============================================================================
# EQUIPMENT FINANCING BASELINE AGENT
# ============================================================================

class EquipmentFinancingBaseline:
    """
    LangGraph-based baseline agent for equipment financing inquiries.

    4-Node Workflow:
    1. INPUT_PROCESSOR: Validate input, check PII
    2. CATEGORIZER: Keyword-based categorization (LIMITATION 1)
    3. RESPONSE_GENERATOR: Template lookup (LIMITATION 2)
    4. LOGGER: Store interaction

    LIMITATION 3: No persistent memory across turns
    """

    def _validate_input(self, query: str):
        """
        Validate input query. Returns (is_valid: bool, message: str)
        """
        if not query or len(query.strip()) < 3:
            return False, "Please provide a valid question about equipment financing."
        return True, ""

    def _create_error_response(self, query: str, validation_msg: str) -> Dict[str, Any]:
        """
        Create error response dict for invalid input.
        """
        return {
            "query": query,
            "response": validation_msg,
            "category": QueryCategory.UNKNOWN.value,
            "confidence": 0.0,
            "sources": [],
            "phase": "error",
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat()
        }

    def __init__(self, kb_path: str = None):
        """
        Initialize the baseline agent.
        
        Args:
            kb_path: Path to knowledge base JSON (optional)
        """
        self.session_id = f"baseline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.turn_number = 0
        self.conversation_history = []
        self.interactions = []
        self.kb = self._load_knowledge_base(kb_path)
        
        # Keywords for categorization (LIMITATION 1: Hardcoded)
        self.category_keywords = {
            QueryCategory.EQUIPMENT_RATES: [
                "rate", "rates", "apr", "percentage", "cost", "price",
                "expensive", "cheap", "financing cost"
            ],
            QueryCategory.LOAN_TERMS: [
                "term", "terms", "payment", "payments", "month", "months",
                "year", "years", "schedule", "duration", "how long"
            ],
            QueryCategory.ELIGIBILITY: [
                "eligible", "qualify", "qualified", "credit", "score",
                "requirement", "requirements", "approve", "approval"
            ],
            QueryCategory.PROCESS: [
                "process", "step", "steps", "how", "application",
                "timeline", "how long", "time", "long does"
            ],
            QueryCategory.EDUCATION: [
                "what", "explain", "equipment", "types", "types of",
                "information", "learn", "tell", "difference", "different"
            ]
        }
        
        # Response templates (LIMITATION 2: No context awareness)
        self.response_templates = {
            QueryCategory.EQUIPMENT_RATES: (
                "Our equipment financing rates typically range from 6.5% to 9.5% "
                "depending on the equipment type, your credit profile, and loan term. "
                "Commercial machinery financing starts at 6.5%, while used equipment "
                "may range up to 11%. Please provide more details about your specific "
                "equipment needs for a personalized quote.",
                0.60
            ),
            QueryCategory.LOAN_TERMS: (
                "Equipment financing terms typically range from 24 to 84 months "
                "depending on the equipment type and depreciation schedule. "
                "Standard commercial equipment has 36-60 month terms, while "
                "construction equipment may have longer terms up to 84 months. "
                "Your credit profile and equipment type will affect the specific terms offered.",
                0.60
            ),
            QueryCategory.ELIGIBILITY: (
                "To qualify for equipment financing, you generally need a credit score "
                "of 600 or higher (620+ preferred). We also consider your business revenue, "
                "existing debt, and the equipment being financed. Most applicants with a "
                "score above 700 qualify for our best rates. Please contact us with your "
                "credit score and equipment details for eligibility verification.",
                0.50
            ),
            QueryCategory.PROCESS: (
                "Our equipment financing application process typically takes 2-5 business days. "
                "Step 1: Submit application with equipment details. Step 2: Credit review. "
                "Step 3: Equipment appraisal. Step 4: Final approval and funding. "
                "Having all documentation ready can speed up the process.",
                0.60
            ),
            QueryCategory.EDUCATION: (
                "We finance a wide range of equipment including industrial machinery, "
                "commercial vehicles, construction equipment, IT equipment, and specialized tools. "
                "We offer multiple financing options: direct equipment loans, equipment leasing, "
                "and used equipment purchase programs. Each option has different rates and terms "
                "optimized for different equipment types and business needs.",
                0.60
            ),
            QueryCategory.ESCALATION: (
                "I appreciate your interest. To ensure you receive the best service, "
                "I'm escalating your request to our equipment financing specialist. "
                "They will contact you shortly to discuss your specific needs and provide "
                "a personalized recommendation. Is there anything else I can help with in the meantime?",
                0.80
            ),
            QueryCategory.REFUSE: (
                "I'm unable to help with that request. I specialize in equipment financing questions. "
                "For other banking services, please contact our main customer service line. "
                "Is there anything related to equipment financing I can assist you with?",
                0.80
            ),
            QueryCategory.UNKNOWN: (
                "I'm not quite sure I understood your question. Could you please clarify what "
                "you'd like to know about equipment financing? I can help with information about "
                "rates, terms, eligibility requirements, or our application process.",
                0.50
            )
        }
        
        logger.info(f"✓ Baseline agent initialized (Session: {self.session_id})")
    
    def _load_knowledge_base(self, kb_path: str = None) -> Dict[str, Any]:
        """Load knowledge base from JSON file."""
        if kb_path and Path(kb_path).exists():
            try:
                with open(kb_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load KB from {kb_path}: {e}")
        
        # Default knowledge base
        return {
            "products": {
                "commercial_equipment_financing": {
                    "rate_min": 6.5,
                    "rate_max": 9.5,
                    "term_min": 36,
                    "term_max": 60,
                    "min_credit": 620
                },
                "construction_equipment_leasing": {
                    "rate_min": 5.5,
                    "rate_max": 8.5,
                    "term_min": 60,
                    "term_max": 84,
                    "min_credit": 600
                },
                "used_equipment_purchase": {
                    "rate_min": 7.5,
                    "rate_max": 11.0,
                    "term_min": 24,
                    "term_max": 48,
                    "min_credit": 650
                }
            }
        }
    
    def _process_input(self, state: AgentState) -> AgentState:
        """
        NODE 1: INPUT_PROCESSOR
        Validate input, check PII, initialize state
        """
        query = state["query"].strip()
        
        # Validate query
        if not query or len(query) < 3:
            state["response"] = "Please provide a valid question about equipment financing."
            state["category"] = QueryCategory.UNKNOWN.value
            state["confidence"] = 0.5
            logger.warning("Invalid query received")
            return state
        
        # Basic PII detection
        pii_patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b'
        }
        
        pii_found = {}
        for pii_type, pattern in pii_patterns.items():
            if re.search(pattern, query):
                pii_found[pii_type] = True
        
        if pii_found:
            state["metadata"]["pii_detected"] = pii_found
            logger.warning(f"PII detected: {pii_found}")
        
        state["metadata"]["input_valid"] = True
        logger.info(f"Input processed: {query[:50]}...")
        
        return state
    
    def _categorize_query(self, state: AgentState) -> AgentState:
        """
        NODE 2: CATEGORIZER
        Categorize query using keyword matching (LIMITATION 1)
        """
        query_lower = state["query"].lower()
        
        # Check for refusal keywords
        if any(word in query_lower for word in ["money", "transfer", "withdraw", "deposit", "account"]):
            state["category"] = QueryCategory.REFUSE.value
            state["confidence"] = 0.85
            logger.info("Query categorized as REFUSE (out of scope)")
            return state
        
        # Match against categories
        max_matches = 0
        best_category = QueryCategory.UNKNOWN
        
        for category, keywords in self.category_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in query_lower)
            if matches > max_matches:
                max_matches = matches
                best_category = category
        
        # Special handling for escalation
        if any(word in query_lower for word in ["approve", "approved", "urgent", "now"]):
            best_category = QueryCategory.ESCALATION
            state["confidence"] = 0.75
        elif best_category == QueryCategory.UNKNOWN:
            state["confidence"] = 0.40
        else:
            state["confidence"] = min(0.60 + (max_matches * 0.05), 0.80)
        
        state["category"] = best_category.value
        logger.info(f"Categorized as: {best_category.value} (confidence: {state['confidence']:.2f})")
        
        return state
    
    def _generate_response(self, state: AgentState) -> AgentState:
        """
        NODE 3: RESPONSE_GENERATOR
        Generate template response (LIMITATION 2: No context)
        """
        category_str = state["category"]
        
        try:
            category = QueryCategory(category_str)
        except ValueError:
            category = QueryCategory.UNKNOWN
        
        if category in self.response_templates:
            response, confidence = self.response_templates[category]
            state["response"] = response
            state["confidence"] = confidence
        else:
            state["response"] = self.response_templates[QueryCategory.UNKNOWN][0]
            state["confidence"] = self.response_templates[QueryCategory.UNKNOWN][1]
        
        state["metadata"]["template_used"] = True
        logger.info(f"Generated template response (length: {len(state['response'])})")
        
        return state
    
    def _log_interaction(self, state: AgentState) -> AgentState:
        """
        NODE 4: LOGGER
        Log interaction with metadata
        """
        state["timestamp"] = datetime.now().isoformat()
        state["session_id"] = self.session_id
        state["turn_number"] = self.turn_number
        
        # Add to conversation history
        self.conversation_history.append({
            "turn": self.turn_number,
            "query": state["query"],
            "response": state["response"],
            "category": state["category"]
        })
        
        state["conversation_history"] = self.conversation_history
        
        # Store interaction
        interaction_log = {
            "timestamp": state["timestamp"],
            "session_id": state["session_id"],
            "turn": state["turn_number"],
            "query": state["query"],
            "response": state["response"],
            "category": state["category"],
            "confidence": state["confidence"],
            "sources": state["sources"],
            "metadata": state["metadata"]
        }
        
        self.interactions.append(interaction_log)
        
        logger.info(f"✓ Interaction logged (Turn: {self.turn_number})")
        
        return state
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Execute the 4-node LangGraph workflow.
        
        Workflow:
        1. INPUT_PROCESSOR → Validate
        2. CATEGORIZER → Classify (keyword matching)
        3. RESPONSE_GENERATOR → Generate template
        4. LOGGER → Log interaction
        
        Args:
            query: User question
            
        Returns:
            State dict with query, response, category, confidence, etc.
        """
        self.turn_number += 1
        
        # Initialize state
        state: AgentState = {
            "query": query,
            "response": "",
            "category": QueryCategory.UNKNOWN.value,
            "confidence": 0.0,
            "sources": [],
            "session_id": self.session_id,
            "turn_number": self.turn_number,
            "conversation_history": self.conversation_history,
            "timestamp": datetime.now().isoformat(),
            "metadata": {}
        }
        
        # Execute nodes
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing Query #{self.turn_number}: {query[:50]}...")
        logger.info(f"{'='*60}")
        
        state = self._process_input(state)
        state = self._categorize_query(state)
        state = self._generate_response(state)
        state = self._log_interaction(state)
        
        return state
    
    def export_logs(self, output_path: str = "baseline_logs.json"):
        """Export interaction logs to JSON."""
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "agent_type": "langgraph_baseline",
            "session_id": self.session_id,
            "total_interactions": len(self.interactions),
            "interactions": self.interactions
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"✓ Logs exported to {output_path}")
        return output_path
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary statistics for the session."""
        if not self.interactions:
            return {"message": "No interactions yet"}
        
        pass_count = sum(1 for i in self.interactions 
                        if i["category"] not in [QueryCategory.REFUSE.value, QueryCategory.UNKNOWN.value])
        avg_confidence = sum(i["confidence"] for i in self.interactions) / len(self.interactions)
        
        return {
            "session_id": self.session_id,
            "total_interactions": len(self.interactions),
            "pass_count": pass_count,
            "pass_rate": f"{(pass_count / len(self.interactions) * 100):.1f}%",
            "average_confidence": f"{avg_confidence:.2f}",
            "categories": list(set(i["category"] for i in self.interactions))
        }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("LANGGRAPH BASELINE AGENT - PHASE 2 EQUIPMENT FINANCING")
    print("="*70 + "\n")
    
    # Initialize agent
    agent = EquipmentFinancingBaseline()
    
    # Test queries
    test_queries = [
        "What are current rates for equipment financing?",
        "What are the loan terms?",
        "I have 700 credit score, am I eligible?",
        "How long does the process take?",
        "What equipment types can be financed? What about lease options?",
        "I need machinery $500k + tools $50k. How do rates differ by equipment type?",
        "Just approve me right now."
    ]
    
    # Process queries
    results = []
    for query in test_queries:
        result = agent.process_query(query)
        results.append(result)
        
        print(f"\nQuery: {result['query']}")
        print(f"Category: {result['category']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Response: {result['response'][:100]}...")
    
    # Export results
    print("\n" + "="*70)
    print("SESSION SUMMARY")
    print("="*70)
    summary = agent.get_session_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    # Export logs
    print("\n" + "="*70)
    agent.export_logs("baseline_logs.json")
    print("="*70 + "\n")
