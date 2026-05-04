"""
Run Phase 5 tool usage demonstrations for the equipment financing agent.
"""

import logging
from pathlib import Path
import json

from tool_agent import EquipmentFinancingToolAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_demo():
    agent = EquipmentFinancingToolAgent(
        kb_path="../data/knowledge_base.json",
        retriever_db_path="../data/chroma_db",
        max_tool_calls=2
    )

    demo_queries = [
        # Correct tool usage: credit score assessment
        "Am I eligible for equipment financing with a 680 credit score?",
        # Correct tool usage: loan payment calculation
        "Calculate the monthly payment for $120,000 over 60 months at 7.5% APR.",
        # Incorrect / failed tool call: missing amount or term
        "What will my payment be?",
        # Out-of-scope request blocked by guardrails
        "Transfer $5,000 to my savings account."
    ]

    results = []
    for query in demo_queries:
        print("\n" + "=" * 80)
        print(f"Query: {query}")
        result = agent.process_query(query)
        print(f"Response: {result['response']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Phase: {result.get('phase')}")
        print(f"Tool used: {result.get('tool_used', 'none')}")
        if result.get('tool_error'):
            print(f"Tool error: {result['tool_error']}")
        results.append(result)

    output_path = Path("outputs")
    output_path.mkdir(parents=True, exist_ok=True)
    demo_file = output_path / "phase5_tool_demo_results.json"
    with open(demo_file, 'w') as f:
        json.dump({"results": results}, f, indent=2)

    print("\nDemo output exported to:", demo_file)
    agent.export_tool_logs(output_dir="outputs")


if __name__ == "__main__":
    run_demo()
