"""
Equipment Financing AI Banking Support & Advisory Agent
Non-Transactional Agentic AI System for Equipment Financing Inquiries

This module implements a safe, compliant conversational AI agent for equipment financing
customers. It provides product education, eligibility assessment, documentation guidance,
and intelligent issue triage while maintaining strict safety guardrails.

Author: Manjul Dixit
Last Updated: April 21, 2026
"""

import json
import os
import logging
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

import anthropic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# DATA STRUCTURES & ENUMS
# ============================================================================

class IntentType(Enum):
    """Enumeration of possible user intents"""
    PRODUCT_INQUIRY = "product_inquiry"
    PRODUCT_COMPARISON = "product_comparison"
    ELIGIBILITY_ASSESSMENT = "eligibility_assessment"
    DOCUMENTATION_GUIDANCE = "documentation_guidance"
    APPLICATION_STATUS = "application_status"
    RATE_INQUIRY = "rate_inquiry"
    FINANCIAL_GUIDANCE = "financial_guidance"
    ISSUE_TRIAGE = "issue_triage"
    ESCALATION_REQUIRED = "escalation_required"
    UNKNOWN = "unknown"


class UserType(Enum):
    """User segment classification"""
    SME_MANUFACTURING = "sme_manufacturing"
    SME_CONSTRUCTION = "sme_construction"
    LARGE_CORPORATION = "large_corporation"
    EQUIPMENT_DEALER = "equipment_dealer"
    PROCUREMENT_MANAGER = "procurement_manager"
    UNKNOWN = "unknown"


class EscalationReason(Enum):
    """Reasons for escalation to human agent"""
    HIGH_VALUE_TRANSACTION = "high_value_transaction"
    COMPLEX_SCENARIO = "complex_scenario"
    POLICY_EXCEPTION = "policy_exception"
    FRAUD_SUSPECTED = "fraud_suspected"
    CUSTOMER_REQUEST = "customer_request"
    AMBIGUOUS_INTENT = "ambiguous_intent"
    SYSTEM_LIMITATION = "system_limitation"


@dataclass
class UserContext:
    """User session context information"""
    user_type: UserType = UserType.UNKNOWN
    business_type: Optional[str] = None
    annual_revenue: Optional[float] = None
    credit_score: Optional[int] = None
    customer_id: Optional[str] = None
    previous_products: List[str] = None
    location: Optional[str] = None
    interaction_count: int = 0
    session_start: datetime = None


@dataclass
class AgentResponse:
    """Structured agent response"""
    message: str
    intent: IntentType
    confidence: float
    requires_escalation: bool = False
    escalation_reason: Optional[EscalationReason] = None
    sources: List[str] = None
    follow_up_questions: List[str] = None
    metadata: Dict = None


# ============================================================================
# SAFETY GUARDRAILS
# ============================================================================

class SafetyGuardrails:
    """Implements safety checks and guardrails for the agent"""

    # Patterns for detecting prohibited actions
    TRANSACTION_KEYWORDS = [
        r'\btransfer\b', r'\bpay\b', r'\bsend\b', r'\bmove\s+funds\b',
        r'\bapprove\b', r'\bprocess\b', r'\bauthorize\b', r'\bwithdraw\b',
        r'\bdebit\b', r'\bcharge\b'
    ]

    # PII detection patterns
    PII_PATTERNS = {
        'SSN': r'\b\d{3}-\d{2}-\d{4}\b',
        'PAN': r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b',
        'ACCOUNT_NUMBER': r'\b\d{10,16}\b(?![0-9])',
        'PHONE': r'\b(?:\+91|0)?[6-9]\d{9}\b',
        'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    }

    # AML/Compliance red flags
    SANCTION_KEYWORDS = [
        'iran', 'north korea', 'syria', 'cuba', 'crimea',
        'structured payment', 'split transfer', 'cash payment',
        'wire to third party', 'beneficial ownership hidden'
    ]

    @staticmethod
    def check_financial_action_attempt(text: str) -> Tuple[bool, str]:
        """
        Detect and block attempts at financial transactions
        
        Returns:
            (is_transaction, reason)
        """
        text_lower = text.lower()
        for pattern in SafetyGuardrails.TRANSACTION_KEYWORDS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True, f"Transaction keyword detected: {pattern}"
        return False, ""

    @staticmethod
    def detect_pii(text: str) -> Tuple[bool, List[str]]:
        """
        Detect PII in text
        
        Returns:
            (contains_pii, list_of_pii_types_found)
        """
        detected = []
        for pii_type, pattern in SafetyGuardrails.PII_PATTERNS.items():
            if re.search(pattern, text):
                detected.append(pii_type)
        return len(detected) > 0, detected

    @staticmethod
    def redact_pii(text: str) -> str:
        """Redact PII from text for logging"""
        redacted = text
        redacted = re.sub(r'\d{3}-\d{2}-\d{4}', 'XXX-XX-XXXX', redacted)
        redacted = re.sub(r'\d{10,16}(?!\d)', '****REDACTED****', redacted)
        redacted = re.sub(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', 'XXXXXX', redacted)
        return redacted

    @staticmethod
    def check_aml_compliance(text: str) -> Tuple[bool, str]:
        """
        Check for AML/Compliance red flags
        
        Returns:
            (is_suspicious, reason)
        """
        text_lower = text.lower()
        for keyword in SafetyGuardrails.SANCTION_KEYWORDS:
            if keyword in text_lower:
                return True, f"AML red flag detected: {keyword}"
        return False, ""


# ============================================================================
# KNOWLEDGE BASE
# ============================================================================

class EquipmentFinancingKB:
    """Equipment Financing Knowledge Base"""

    def __init__(self, kb_path: str = "mockdata"):
        """Initialize knowledge base from JSON files"""
        self.kb_path = kb_path
        self.products = self._load_json("mock_products.json").get("products", {})
        self.customers = self._load_json("mock_customers.json").get("customers", [])
        self.faqs = self._load_json("faqs.json").get("faqs", {})
        self.last_updated = datetime.now().isoformat()
        logger.info(f"KB loaded: {len(self.products)} products, {len(self.customers)} customers")

    def _load_json(self, filename: str) -> Dict:
        """Safely load JSON file"""
        try:
            file_path = os.path.join(self.kb_path, filename)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {filename}: {str(e)}")
        return {}

    def get_product_info(self, product_key: str) -> Optional[Dict]:
        """Get product information from KB"""
        return self.products.get(product_key)

    def get_all_products(self) -> Dict:
        """Get all products"""
        return self.products

    def get_customer_eligibility(self, customer_id: str) -> Optional[Dict]:
        """Get customer eligibility information"""
        for customer in self.customers:
            if customer.get('customer_id') == customer_id:
                return customer
        return None

    def search_faqs(self, query: str) -> List[Dict]:
        """Search FAQs for relevant answers"""
        results = []
        query_lower = query.lower()
        for faq_key, faq_item in self.faqs.items():
            question_lower = faq_item.get('question', '').lower()
            if any(word in question_lower for word in query_lower.split()):
                results.append(faq_item)
        return results[:3]  # Return top 3 matches


# ============================================================================
# INTENT CLASSIFICATION
# ============================================================================

class IntentClassifier:
    """Classifies user intent from query text"""

    INTENT_PATTERNS = {
        IntentType.PRODUCT_INQUIRY: [
            r'(what|how much|cost|rate|interest)',
            r'(equipment loan|lease|line of credit|financing)',
            r'(price|charge|fee)'
        ],
        IntentType.ELIGIBILITY_ASSESSMENT: [
            r'(eligible|qualify|criteria|requirement)',
            r'(can we|are we|am i)',
            r'(apply|get|obtain)'
        ],
        IntentType.DOCUMENTATION_GUIDANCE: [
            r'(document|proof|certificate|paper)',
            r'(need|require|submit)',
            r'(application|form|process)'
        ],
        IntentType.RATE_INQUIRY: [
            r'(interest rate|rate|per annum|p\.a|percentage)',
            r'(calculate|emi|payment)',
            r'(compare|difference|tier)'
        ],
        IntentType.FINANCIAL_GUIDANCE: [
            r'(recommend|suggest|should i|best)',
            r'(option|choice|decision)',
            r'(financial|investment|strategy)'
        ],
        IntentType.APPLICATION_STATUS: [
            r'(status|approval|pending|decision)',
            r'(application|submitted|approved)',
            r'(when|how long|timeline)'
        ],
    }

    @staticmethod
    def classify(query: str, context: UserContext = None) -> Tuple[IntentType, float]:
        """
        Classify intent with confidence score
        
        Returns:
            (intent, confidence_score)
        """
        query_lower = query.lower()
        scores = {}

        for intent, patterns in IntentClassifier.INTENT_PATTERNS.items():
            pattern_matches = 0
            for pattern in patterns:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    pattern_matches += 1

            if pattern_matches > 0:
                scores[intent] = pattern_matches / len(patterns)

        if scores:
            best_intent = max(scores.items(), key=lambda x: x[1])
            return best_intent[0], best_intent[1]

        return IntentType.UNKNOWN, 0.0


# ============================================================================
# MAIN AGENT
# ============================================================================

class EquipmentFinancingAgent:
    """Main Equipment Financing AI Agent"""

    def __init__(self, kb_path: str = "mockdata"):
        """Initialize the agent"""
        self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.kb = EquipmentFinancingKB(kb_path)
        self.model = "claude-3-5-sonnet-20241022"
        self.user_context = UserContext()
        self.conversation_history = []
        self.interaction_count = 0

    def process_query(self, user_query: str) -> AgentResponse:
        """
        Process a user query and generate response
        
        Args:
            user_query: User's question or statement
            
        Returns:
            AgentResponse object with structured output
        """
        self.interaction_count += 1
        self.user_context.interaction_count = self.interaction_count

        # ========== SAFETY CHECKS ==========
        
        # Check for financial transactions
        is_transaction, reason = SafetyGuardrails.check_financial_action_attempt(user_query)
        if is_transaction:
            logger.warning(f"Transaction blocked: {reason}")
            return self._block_transaction_response()

        # Check for PII exposure
        contains_pii, pii_types = SafetyGuardrails.detect_pii(user_query)
        if contains_pii:
            logger.warning(f"PII detected: {pii_types}")
            return self._handle_pii_exposure(user_query, pii_types)

        # Check for AML/Compliance issues
        is_suspicious, aml_reason = SafetyGuardrails.check_aml_compliance(user_query)
        if is_suspicious:
            logger.warning(f"AML flag: {aml_reason}")
            return self._escalate_to_compliance(aml_reason)

        # ========== INTENT CLASSIFICATION ==========
        intent, confidence = IntentClassifier.classify(user_query, self.user_context)
        logger.info(f"Intent: {intent.value}, Confidence: {confidence:.2f}")

        # ========== RESPONSE GENERATION ==========
        if confidence < 0.3 or intent == IntentType.UNKNOWN:
            response = self._clarification_response(user_query)
        else:
            response = self._generate_response(user_query, intent)

        # ========== LOGGING & AUDIT TRAIL ==========
        self._log_interaction(user_query, response)

        return response

    def _generate_response(self, query: str, intent: IntentType) -> AgentResponse:
        """Generate response based on intent"""

        # Build system prompt
        system_prompt = self._build_system_prompt()

        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": query
        })

        # Get response from Claude
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=self.conversation_history
            )

            assistant_message = response.content[0].text

            # Add to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            # Determine if escalation is needed
            requires_escalation = self._should_escalate(query, intent)
            escalation_reason = self._get_escalation_reason(query, intent) if requires_escalation else None

            return AgentResponse(
                message=assistant_message,
                intent=intent,
                confidence=0.85,
                requires_escalation=requires_escalation,
                escalation_reason=escalation_reason,
                sources=["Equipment Financing KB v1.0 (April 21, 2026)"],
                follow_up_questions=[
                    "Would you like more details about this product?",
                    "Do you have any other equipment financing questions?",
                    "Would you like to speak with a specialist?"
                ],
                metadata={
                    "interaction_id": f"INT_{self.interaction_count}",
                    "user_type": self.user_context.user_type.value,
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return self._error_response(str(e))

    def _build_system_prompt(self) -> str:
        """Build comprehensive system prompt"""
        return """You are the Equipment Financing AI Banking Support & Advisory Agent - a professional,
knowledgeable assistant specializing in equipment financing for businesses.

ROLE & RESPONSIBILITIES:
- Provide expert guidance on equipment financing products
- Assess customer eligibility based on business profile
- Guide customers through the application process
- Educate customers about product features, rates, and terms
- Safely escalate complex or high-risk scenarios

PRODUCT PORTFOLIO:
1. Equipment Term Loan (7.5-11.5% p.a., ₹1L-₹5Cr, 24-180 months)
2. Equipment Lease (6.5-10.5% p.a., finance/operating/hire purchase)
3. Equipment Line of Credit (8-12% p.a., ₹1L-₹2.5Cr)
4. Vendor Financing Program (6.5-10% p.a., dealer-sponsored)
5. Equipment Refinance Loan (6-10% p.a.)
6. Working Capital Against Equipment (8.5-12.5% p.a.)

SAFETY & COMPLIANCE REQUIREMENTS:
- NEVER process or promise any financial transactions
- NEVER request or store PII (SSN, account numbers, etc.)
- ALWAYS cite sources and use current rates from KB
- ALWAYS escalate ambiguous or high-risk cases
- NEVER provide binding investment/legal/tax advice
- ALWAYS include appropriate disclaimers

COMMUNICATION STYLE:
- Professional yet friendly and approachable
- Clear, jargon-free explanations
- Use examples and calculations when relevant
- Ask clarifying questions to understand needs
- Proactive in offering specialist consultations

ESCALATION TRIGGERS:
- Query involves money movement (BLOCK)
- Customer requests approval or authorization
- Ambiguity >30% or confidence <70%
- Customer emotionally distressed
- High-value transactions (>₹2Cr)
- Legal/tax/compliance questions
- Explicit customer request for human agent"""

    def _should_escalate(self, query: str, intent: IntentType) -> bool:
        """Determine if escalation to human is needed"""
        escalation_triggers = [
            "approve" in query.lower(),
            "authorize" in query.lower(),
            "guarantee" in query.lower(),
            intent == IntentType.FINANCIAL_GUIDANCE,
            intent == IntentType.ESCALATION_REQUIRED,
            "complex" in query.lower(),
            "exception" in query.lower(),
        ]
        return any(escalation_triggers)

    def _get_escalation_reason(self, query: str, intent: IntentType) -> Optional[EscalationReason]:
        """Determine escalation reason"""
        if "approve" in query.lower() or "authorize" in query.lower():
            return EscalationReason.COMPLEX_SCENARIO
        if "guarantee" in query.lower():
            return EscalationReason.POLICY_EXCEPTION
        if intent == IntentType.FINANCIAL_GUIDANCE:
            return EscalationReason.SYSTEM_LIMITATION
        return None

    def _clarification_response(self, query: str) -> AgentResponse:
        """Response when intent is unclear"""
        return AgentResponse(
            message=f"""I appreciate your question! To help you better, could you provide a bit more detail?

Your question: "{query}"

Are you interested in:
1. **Product Information** - Learn about equipment financing options
2. **Eligibility Assessment** - Check if your business qualifies
3. **Application Process** - Understand the steps to apply
4. **Rates & Terms** - Compare pricing and features
5. **Something Else** - Feel free to clarify!

Please let me know, and I'll provide expert guidance tailored to your needs.""",
            intent=IntentType.UNKNOWN,
            confidence=0.3,
            requires_escalation=False,
            follow_up_questions=[
                "What aspect of equipment financing interests you most?",
                "What type of equipment are you looking to finance?",
                "What's your business type and approximate revenue?"
            ]
        )

    def _block_transaction_response(self) -> AgentResponse:
        """Response when transaction is blocked"""
        return AgentResponse(
            message="""I cannot process financial transactions directly. For security reasons, all fund movements 
must be done through secure banking channels.

**Safe Alternatives:**
✓ Use our Mobile Banking App for transfers
✓ Visit your nearest branch
✓ Call our dedicated Finance Team (1-800-EQUIPMENT)
✓ Use ATM or online banking portal

**If you need equipment financing:**
I'm here to help you understand your options. Tell me about your equipment needs and 
I can guide you through the application process!""",
            intent=IntentType.ISSUE_TRIAGE,
            confidence=1.0,
            requires_escalation=True,
            escalation_reason=EscalationReason.HIGH_VALUE_TRANSACTION
        )

    def _handle_pii_exposure(self, query: str, pii_types: List[str]) -> AgentResponse:
        """Response when PII is detected"""
        redacted_query = SafetyGuardrails.redact_pii(query)
        logger.warning(f"PII redacted in log: {pii_types}")

        return AgentResponse(
            message=f"""⚠️ **Security Notice:**

I noticed you shared sensitive information ({', '.join(pii_types)}). For your safety:
- **NEVER share SSN, account numbers, or passwords in chat**
- **NEVER paste full PII in any messaging platform**
- Our secure systems never ask for PII via chat

To protect your data:
✓ Use our secure app for authenticated transactions
✓ Verify you're on our official website/app before entering sensitive data
✓ Contact us at our official number: 1-800-EQUIPMENT

**How can I help safely?**
I can still assist with:
- Product information
- General eligibility criteria
- Process steps and timeline
- Documentation guidance (without sharing actual documents)

What would you like to know?""",
            intent=IntentType.ISSUE_TRIAGE,
            confidence=1.0,
            requires_escalation=True,
            escalation_reason=EscalationReason.SYSTEM_LIMITATION,
            metadata={"security_flag": True, "pii_detected": pii_types}
        )

    def _escalate_to_compliance(self, reason: str) -> AgentResponse:
        """Escalate to compliance team"""
        return AgentResponse(
            message="""**Compliance Alert - Escalating to Specialist**

Your inquiry requires review by our compliance team to ensure regulatory adherence.

We take AML/KYC compliance seriously. A specialist will contact you within 2 hours.

**Case Details:**
- Case ID: COMP_{self.interaction_count}
- Priority: HIGH
- Specialist Team: Compliance & AML

Thank you for your patience!""",
            intent=IntentType.ESCALATION_REQUIRED,
            confidence=1.0,
            requires_escalation=True,
            escalation_reason=EscalationReason.FRAUD_SUSPECTED,
            metadata={"compliance_flag": True, "reason": reason}
        )

    def _error_response(self, error_msg: str) -> AgentResponse:
        """Response when system encounters error"""
        logger.error(f"System error: {error_msg}")
        return AgentResponse(
            message="""I'm experiencing a technical issue at the moment. 

**Don't worry! Here's what you can do:**
1. Try rephrasing your question
2. Call our specialist team: 1-800-EQUIPMENT
3. Visit our website: www.bank.com/equipment-financing

Our team is standing by to assist you!""",
            intent=IntentType.ISSUE_TRIAGE,
            confidence=0.0,
            requires_escalation=True,
            escalation_reason=EscalationReason.SYSTEM_LIMITATION
        )

    def _log_interaction(self, query: str, response: AgentResponse) -> None:
        """Log interaction for audit trail"""
        # Redact PII before logging
        redacted_query = SafetyGuardrails.redact_pii(query)
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "interaction_id": f"INT_{self.interaction_count}",
            "user_intent": response.intent.value,
            "confidence": response.confidence,
            "escalation": response.requires_escalation,
            "escalation_reason": response.escalation_reason.value if response.escalation_reason else None,
            "user_type": self.user_context.user_type.value,
        }
        
        logger.info(f"Interaction Log: {json.dumps(log_entry)}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main function to demonstrate agent"""
    print("=" * 70)
    print("Equipment Financing AI Banking Support & Advisory Agent")
    print("=" * 70)
    print("\nWelcome! I'm here to help with all your equipment financing questions.")
    print("Type 'quit' to exit.\n")

    agent = EquipmentFinancingAgent()

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("\nThank you for using our service. Goodbye!")
            break

        if not user_input:
            continue

        response = agent.process_query(user_input)

        print(f"\nAgent: {response.message}")
        if response.requires_escalation:
            print(f"[Escalation: {response.escalation_reason.value}]")
        print()


if __name__ == "__main__":
    main()
