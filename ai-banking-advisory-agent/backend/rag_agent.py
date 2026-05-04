"""
Retrieval-Augmented Agent for Phase 4
Extends baseline agent with semantic search and document retrieval
"""

import json
import logging
from typing import Any, Dict, List
from datetime import datetime
from pathlib import Path

from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

from langgraph_agent import (
    EquipmentFinancingBaseline,
    AgentState,
    QueryCategory
)
from vector_store import RetrieverManager

logger = logging.getLogger(__name__)


class EquipmentFinancingRAG(EquipmentFinancingBaseline):
    """
    Phase 4: Retrieval-Augmented Generation Agent

    Extends baseline with semantic search:
    - Retrieves relevant documents from vector store
    - Augments template/LLM responses with retrieved context
    - Tracks retrieval performance and coverage

    Improvements over baseline:
    - Better answer relevance (uses semantic search vs keyword matching)
    - Lower hallucination risk (grounds in retrieved documents)
    - Transparency (shows sources and confidence)
    """
    
    def __init__(
        self,
        kb_path: str = "data/knowledge_base.json",
        retriever_db_path: str = "data/chroma_db"
    ):
        """Initialize RAG agent with retriever"""
        # Initialize baseline (only passes kb_path)
        super().__init__(kb_path=kb_path)
        
        # Initialize retriever
        logger.info("Initializing retriever...")
        try:
            self.retriever = RetrieverManager(kb_path=kb_path, db_path=retriever_db_path)
        except Exception as exc:
            logger.warning(f"Retriever disabled: {exc}")
            self.retriever = None
        
        # Retrieval performance tracking
        self.retrieval_performance = {
            "total_queries": 0,
            "successful_retrievals": 0,
            "average_similarity": 0.0,
            "sources_used": {},
            "queries_without_results": 0
        }
        
        logger.info("RAG Agent initialized with retrieval capability")
    
    def _retrieve_context(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Retrieve relevant documents for query.
        
        Returns:
            Dict with retrieved documents, similarity scores, and metadata
        """
        if self.retriever is None:
            return {
                "retrieved_documents": [],
                "retrieval_count": 0,
                "success": False
            }

        retrieved_docs = self.retriever.retrieve(query, top_k=top_k)
        
        # Track retrieval performance
        self.retrieval_performance["total_queries"] += 1
        
        if retrieved_docs:
            self.retrieval_performance["successful_retrievals"] += 1
            similarities = [doc["similarity_score"] for doc in retrieved_docs]
            self.retrieval_performance["average_similarity"] = (
                sum(similarities) / len(similarities)
            )
            
            # Track source usage
            for doc in retrieved_docs:
                source = doc["metadata"].get("source", "unknown")
                self.retrieval_performance["sources_used"][source] = \
                    self.retrieval_performance["sources_used"].get(source, 0) + 1
        else:
            self.retrieval_performance["queries_without_results"] += 1
        
        return {
            "retrieved_documents": retrieved_docs,
            "retrieval_count": len(retrieved_docs),
            "success": len(retrieved_docs) > 0
        }
    
    def _generate_augmented_response(
        self,
        query: str,
        category: str,
        retrieved_context: Dict[str, Any]
    ) -> str:
        """
        Generate response augmented with retrieved context.
        
        Strategy:
        1. Use baseline categorization
        2. Augment with retrieved documents
        3. Enhance confidence based on retrieval success
        """
        # Get base template response by constructing a temporary state
        temp_state = {
            "query": query,
            "response": "",
            "category": category,
            "confidence": 0.0,
            "sources": [],
            "session_id": self.session_id,
            "turn_number": self.turn_number,
            "conversation_history": self.conversation_history,
            "timestamp": datetime.now().isoformat(),
            "metadata": {}
        }
        generated_state = self._generate_response(temp_state)
        base_response = generated_state["response"]
        
        retrieved_docs = retrieved_context.get("retrieved_documents", [])
        
        if not retrieved_docs:
            # Fallback to base response if no retrieval
            return base_response
        
        # Build augmented response
        augmented = f"{base_response}\n\n[CONTEXT FROM KNOWLEDGE BASE]"
        
        for doc in retrieved_docs[:2]:  # Use top 2 for brevity
            content_preview = doc["content"][:150]
            similarity = doc["similarity_score"]
            source = doc["metadata"].get("source", "unknown")
            
            augmented += f"\n\n• From {source} (relevance: {similarity:.2%}):\n  {content_preview}..."
        
        augmented += "\n\n[For complete details, please ask for more information about specific topics]"
        
        return augmented
    
    def _process_input_with_retrieval(self, query: str) -> Dict[str, Any]:
        """
        Process input with both baseline pipeline and retrieval.
        
        Returns augmented state with retrieval results.
        """
        # Build initial state for input processing
        state = {
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
        processed = self._process_input(state)

        # Retrieve context
        context = self._retrieve_context(query, top_k=3)

        # Categorize (baseline)
        category_state = self._categorize_query(processed)
        category = category_state["category"]

        # Generate augmented response
        if context["success"]:
            response = self._generate_augmented_response(query, category, context)
            confidence = min(0.95, processed["confidence"] + 0.1)  # Boost confidence
        else:
            response = self._generate_response(query, category)
            confidence = processed["confidence"]
        
        return {
            "query": query,
            "category": category,
            "response": response,
            "confidence": confidence,
            "sources": [doc["metadata"] for doc in context.get("retrieved_documents", [])],
            "retrieval_context": context
        }
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process query through RAG agent.
        
        Returns:
            Response with retrieved sources and confidence
        """
        session_id = self.session_id
        
        # Validate input
        is_valid, validation_msg = self._validate_input(query)
        if not is_valid:
            return self._create_error_response(query, validation_msg)
        
        # Process with retrieval
        result = self._process_input_with_retrieval(query)
        
        # Log interaction
        interaction_state = {
            "query": result["query"],
            "response": result["response"],
            "category": result["category"],
            "confidence": result["confidence"],
            "sources": result.get("sources", []),
            "session_id": self.session_id,
            "turn_number": self.turn_number,
            "conversation_history": self.conversation_history,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "phase": "phase_4_rag",
                "retrieval_success": result["retrieval_context"]["success"],
                "sources_used": len(result.get("sources", [])),
                "retrieval_count": result["retrieval_context"]["retrieval_count"]
            }
        }
        self._log_interaction(interaction_state)
        
        return {
            "query": result["query"],
            "response": result["response"],
            "category": result["category"],
            "confidence": result["confidence"],
            "sources": result.get("sources", []),
            "phase": "phase_4_rag",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_retrieval_stats(self) -> Dict[str, Any]:
        """Get retrieval performance statistics"""
        total_queries = max(self.retrieval_performance["total_queries"], 1)
        return {
            "total_queries": total_queries,
            "successful_retrievals": self.retrieval_performance["successful_retrievals"],
            "success_rate": round(
                self.retrieval_performance["successful_retrievals"] / total_queries,
                3
            ),
            "average_similarity": round(
                self.retrieval_performance["average_similarity"],
                3
            ),
            "sources_used": self.retrieval_performance["sources_used"],
            "queries_without_results": self.retrieval_performance["queries_without_results"],
            "retriever_available": self.retriever is not None
        }
    
    def export_rag_logs(self, output_dir: str = "outputs") -> str:
        """
        Export RAG logs with retrieval statistics.
        
        Returns:
            Path to exported log file
        """
        output_path = Path(output_dir) / f"rag_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        export_data = {
            "phase": "phase_4_rag",
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "interactions": self.interaction_log,
            "retrieval_stats": self.get_retrieval_stats(),
            "vector_store_stats": self.retriever.get_stats()
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Exported RAG logs to {output_path}")
        return str(output_path)


def create_rag_agent(
    kb_path: str = "data/knowledge_base.json",
    retriever_db_path: str = "data/chroma_db",
    force_reinit_retriever: bool = False
) -> EquipmentFinancingRAG:
    """
    Factory function to create RAG agent with retriever setup.
    
    Args:
        kb_path: Path to knowledge base
        retriever_db_path: Path to vector store
        force_reinit_retriever: Rebuild vector store
    
    Returns:
        Initialized RAG agent
    """
    # Ensure retriever is set up
    logger.info("Setting up retriever for RAG agent...")
    manager = RetrieverManager(kb_path, retriever_db_path)
    manager.setup(force_reinit=force_reinit_retriever)
    
    # Create agent
    agent = EquipmentFinancingRAG(kb_path, retriever_db_path)
    
    logger.info("RAG agent ready for queries")
    return agent


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Quick test
    print("Initializing RAG agent...")
    agent = create_rag_agent(force_reinit_retriever=True)
    
    test_queries = [
        "What equipment financing options do you offer?",
        "What credit score do I need for a loan?",
        "Tell me about the application process"
    ]
    
    print("\n" + "="*80)
    for query in test_queries:
        result = agent.process_query(query)
        print(f"\nQuery: {query}")
        print(f"Response: {result['response'][:300]}...")
        print(f"Confidence: {result['confidence']}")
        print(f"Sources used: {len(result.get('sources', []))}")
    
    print("\n" + "="*80)
    print("\nRetrieval Statistics:")
    import pprint
    pprint.pprint(agent.get_retrieval_stats())
