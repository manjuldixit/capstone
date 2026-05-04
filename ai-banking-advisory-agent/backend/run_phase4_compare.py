"""
Phase 4 Comparison Runner
Compares baseline agent responses with RAG-augmented responses
Shows improvement from retrieval-augmented generation
"""

import json
import logging
import sys
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path
import argparse

from langgraph_agent import EquipmentFinancingBaseline
from rag_agent import EquipmentFinancingRAG
from vector_store import RetrieverManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_test_queries(test_set_path: str = "../data/evaluation_test_set.json") -> List[str]:
    """Load test queries for comparison"""
    try:
        with open(test_set_path, 'r') as f:
            data = json.load(f)
        
        # Extract queries from structure
        queries = []
        if "basic_test_queries" in data:
            queries.extend(data["basic_test_queries"])
        if "extended_test_queries" in data:
            # Use first few extended queries to avoid redundancy
            queries.extend(data["extended_test_queries"][:3])
        
        return queries[:10]  # Limit to 10 for manageability
    except Exception as e:
        logger.error(f"Failed to load test queries: {e}")
        return [
            "What are the equipment financing rates?",
            "What credit score do I need?",
            "How do I apply for a loan?",
            "What types of equipment can I finance?",
            "What is the application timeline?"
        ]


def run_comparison(
    test_queries: List[str] = None,
    output_dir: str = "outputs",
    force_reinit_retriever: bool = False
) -> Dict[str, Any]:
    """
    Run side-by-side comparison of baseline vs RAG agent.
    
    Args:
        test_queries: List of queries to test
        output_dir: Directory for output files
        force_reinit_retriever: Rebuild vector store
    
    Returns:
        Comparison results
    """
    if test_queries is None:
        test_queries = load_test_queries()
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Running Phase 4 comparison on {len(test_queries)} queries...")
    
    # Initialize agents
    logger.info("Initializing baseline agent...")
    baseline_agent = EquipmentFinancingBaseline()
    
    logger.info("Initializing RAG agent...")
    # Setup retriever first
    retriever_manager = RetrieverManager(kb_path="../data/knowledge_base.json", db_path="../data/chroma_db")
    retriever_manager.setup(force_reinit=force_reinit_retriever)
    
    rag_agent = EquipmentFinancingRAG(kb_path="../data/knowledge_base.json", retriever_db_path="../data/chroma_db")
    
    # Run comparisons
    comparisons = []
    
    for i, query in enumerate(test_queries, 1):
        logger.info(f"\n[{i}/{len(test_queries)}] Processing: {query[:50]}...")
        
        try:
            # Baseline response
            baseline_result = baseline_agent.process_query(query)
            
            # RAG response
            rag_result = rag_agent.process_query(query)
            
            comparison = {
                "query_number": i,
                "query": query,
                "baseline": {
                    "response": baseline_result["response"],
                    "category": baseline_result["category"],
                    "confidence": baseline_result["confidence"],
                    "phase": "phase_2_baseline"
                },
                "rag": {
                    "response": rag_result["response"],
                    "category": rag_result["category"],
                    "confidence": rag_result["confidence"],
                    "phase": "phase_4_rag",
                    "sources_used": len(rag_result.get("sources", []))
                },
                "improvement": {
                    "confidence_delta": round(
                        rag_result["confidence"] - baseline_result["confidence"],
                        3
                    ),
                    "source_coverage": len(rag_result.get("sources", [])) > 0
                }
            }
            
            comparisons.append(comparison)
            
            # Print summary
            print(f"\n  Baseline confidence: {baseline_result['confidence']:.3f}")
            print(f"  RAG confidence: {rag_result['confidence']:.3f}")
            print(f"  Confidence delta: {comparison['improvement']['confidence_delta']:+.3f}")
            print(f"  Sources retrieved: {len(rag_result.get('sources', []))}")
        
        except Exception as e:
            logger.error(f"Error processing query {i}: {e}")
            comparisons.append({
                "query_number": i,
                "query": query,
                "error": str(e)
            })
    
    # Calculate aggregate metrics
    successful_comparisons = [c for c in comparisons if "baseline" in c]
    
    avg_baseline_confidence = (
        sum(c["baseline"]["confidence"] for c in successful_comparisons) 
        / len(successful_comparisons)
    ) if successful_comparisons else 0
    
    avg_rag_confidence = (
        sum(c["rag"]["confidence"] for c in successful_comparisons)
        / len(successful_comparisons)
    ) if successful_comparisons else 0
    
    avg_confidence_improvement = (
        sum(c["improvement"]["confidence_delta"] for c in successful_comparisons)
        / len(successful_comparisons)
    ) if successful_comparisons else 0
    
    source_coverage = (
        sum(1 for c in successful_comparisons if c["improvement"]["source_coverage"])
        / len(successful_comparisons)
    ) if successful_comparisons else 0
    
    # Export results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_path / f"phase4_comparison_{timestamp}.json"
    
    export_data = {
        "metadata": {
            "phase": "phase_4_rag_comparison",
            "timestamp": datetime.now().isoformat(),
            "total_queries": len(test_queries),
            "successful_comparisons": len(successful_comparisons)
        },
        "comparisons": comparisons,
        "aggregate_metrics": {
            "baseline": {
                "average_confidence": round(avg_baseline_confidence, 3),
                "agent": "EquipmentFinancingBaseline"
            },
            "rag": {
                "average_confidence": round(avg_rag_confidence, 3),
                "average_sources": round(
                    sum(c["rag"]["sources_used"] for c in successful_comparisons)
                    / len(successful_comparisons),
                    2
                ) if successful_comparisons else 0,
                "source_coverage": round(source_coverage, 3),
                "agent": "EquipmentFinancingRAG"
            },
            "improvement": {
                "average_confidence_delta": round(avg_confidence_improvement, 3),
                "improvement_percentage": round(
                    (avg_confidence_improvement / avg_baseline_confidence * 100)
                    if avg_baseline_confidence > 0 else 0,
                    1
                ),
                "source_enhanced_queries": sum(
                    1 for c in successful_comparisons
                    if c["improvement"]["source_coverage"]
                )
            }
        },
        "retriever_stats": rag_agent.get_retrieval_stats(),
        "vector_store_stats": rag_agent.retriever.get_stats()
    }
    
    with open(output_file, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    logger.info(f"\nComparison complete!")
    logger.info(f"Results exported to: {output_file}")
    
    # Print summary
    print("\n" + "="*80)
    print("PHASE 4 RAG COMPARISON SUMMARY")
    print("="*80)
    print(f"\nBaseline Average Confidence: {avg_baseline_confidence:.3f}")
    print(f"RAG Average Confidence:      {avg_rag_confidence:.3f}")
    print(f"Confidence Improvement:      {avg_confidence_improvement:+.3f} ({avg_confidence_improvement/avg_baseline_confidence*100 if avg_baseline_confidence else 0:+.1f}%)")
    print(f"Queries with Source Coverage: {sum(1 for c in successful_comparisons if c['improvement']['source_coverage'])}/{len(successful_comparisons)}")
    print(f"Average Sources per Query:   {sum(c['rag']['sources_used'] for c in successful_comparisons)/len(successful_comparisons) if successful_comparisons else 0:.2f}")
    print("\n" + "="*80)
    
    return export_data


def main():
    parser = argparse.ArgumentParser(
        description="Phase 4 RAG Comparison Runner"
    )
    parser.add_argument(
        "--force-reinit",
        action="store_true",
        help="Rebuild vector store from scratch"
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Output directory for results"
    )
    parser.add_argument(
        "--test-set",
        default="data/evaluation_test_set.json",
        help="Path to test queries JSON"
    )
    
    args = parser.parse_args()
    
    # Load test queries
    test_queries = load_test_queries(args.test_set)
    
    # Run comparison
    results = run_comparison(
        test_queries=test_queries,
        output_dir=args.output_dir,
        force_reinit_retriever=args.force_reinit
    )
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
