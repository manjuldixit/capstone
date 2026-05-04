"""Run Phase 6 memory and multi-turn planning demonstrations."""

import logging
import json
from pathlib import Path

from memory_agent import EquipmentFinancingMemoryAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_demo():
    agent = EquipmentFinancingMemoryAgent(
        kb_path="../data/knowledge_base.json",
        retriever_db_path="../data/chroma_db",
        max_tool_calls=2,
        short_term_capacity=5
    )

    demo_queries = [
        # Multi-step planning query
        "We're planning to finance a CNC machine for our manufacturing business. Could you help us plan the financing?",
        # Follow-up query that uses remembered business profile
        "Our credit score is 710 and we'd like a 60-month loan. What does that mean for eligibility and monthly payments?",
        # Context-aware follow-up question
        "What documents should we prepare for the application?",
        # Explicit memory reset test
        "Please forget the earlier details and start over.",
        # Fresh question after reset
        "What equipment financing options do you offer?"
    ]

    results = []
    for query in demo_queries:
        print("\n" + "=" * 80)
        print(f"Query: {query}")
        result = agent.process_query(query)
        print(f"Response: {result['response']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Phase: {result.get('phase')}")
        print(f"Memory used: {result.get('memory_used', False)}")
        if result.get('memory_summary'):
            print(f"Memory summary: {result['memory_summary']}")
        results.append(result)

    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    demo_file = output_dir / "phase6_memory_demo_results.json"
    with open(demo_file, "w") as f:
        json.dump({"results": results}, f, indent=2)

    print("\nDemo output exported to:", demo_file)
    agent.export_memory_logs(output_dir="outputs")


if __name__ == "__main__":
    run_demo()
