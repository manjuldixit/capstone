"""Run Phase 7 adaptive behavior demonstrations."""

import logging
import json
from pathlib import Path

from adaptive_agent import EquipmentFinancingAdaptiveAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_demo():
    agent = EquipmentFinancingAdaptiveAgent(
        kb_path="../data/knowledge_base.json",
        retriever_db_path="../data/chroma_db",
        max_tool_calls=2,
        short_term_capacity=5
    )

    query = "What equipment financing options do you offer?"
    print("\n" + "=" * 80)
    print("BEFORE feedback")
    before_result = agent.process_query(query)
    print(f"Query: {query}")
    print(f"Response: {before_result['response']}")
    print(f"Phase: {before_result.get('phase')}")
    print(f"Adaptive applied: {before_result.get('adaptive_applied', False)}")

    feedback = agent.collect_feedback(
        query=query,
        response=before_result["response"],
        rating=2,
        comments="Too vague and general; I need specific financing options with concrete examples."
    )
    print("\nFeedback collected:")
    print(feedback)

    print("\n" + "=" * 80)
    print("AFTER feedback")
    after_result = agent.process_query(query)
    print(f"Query: {query}")
    print(f"Response: {after_result['response']}")
    print(f"Phase: {after_result.get('phase')}")
    print(f"Adaptive applied: {after_result.get('adaptive_applied', False)}")
    print(f"Memory used: {after_result.get('memory_used', False)}")

    print("\n" + "=" * 80)
    print("ADAPTATION EXPLANATION")
    print(agent.explain_adaptation())

    print("\n" + "=" * 80)
    follow_up = "What documents do I need to prepare for the loan application?"
    print(f"Follow-up query: {follow_up}")
    follow_up_result = agent.process_query(follow_up)
    print(f"Response: {follow_up_result['response']}")
    print(f"Adaptive applied: {follow_up_result.get('adaptive_applied', False)}")

    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    demo_file = output_dir / "phase7_adaptive_demo_results.json"
    with open(demo_file, "w") as f:
        json.dump({
            "before": before_result,
            "after": after_result,
            "feedback": feedback,
            "follow_up": follow_up_result,
            "adaptation_explanation": agent.explain_adaptation()
        }, f, indent=2)

    print("\nDemo output exported to:", demo_file)
    agent.export_adaptive_logs(output_dir="outputs")


if __name__ == "__main__":
    run_demo()
