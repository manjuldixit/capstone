"""Phase 7: Adaptive equipment financing agent.

Uses user feedback to change behavior and improve future responses.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from feedback_manager import FeedbackManager
from memory_agent import EquipmentFinancingMemoryAgent

logger = logging.getLogger(__name__)


class EquipmentFinancingAdaptiveAgent(EquipmentFinancingMemoryAgent):
    """Feedback-aware agent that adapts response style over time."""

    def __init__(
        self,
        kb_path: str = "data/knowledge_base.json",
        retriever_db_path: str = "data/chroma_db",
        max_tool_calls: int = 2,
        short_term_capacity: int = 5
    ):
        super().__init__(
            kb_path=kb_path,
            retriever_db_path=retriever_db_path,
            max_tool_calls=max_tool_calls,
            short_term_capacity=short_term_capacity
        )
        self.feedback_manager = FeedbackManager()
        self.adaptation_phase = "phase_7_adaptive_behavior"
        logger.info("Adaptive agent initialized for Phase 7")

    def process_query(self, query: str) -> Dict[str, Any]:
        """Process the query and apply adaptive adjustments when feedback exists."""
        result = super().process_query(query)
        adjusted = self._apply_feedback_adjustments(query, result)
        return adjusted

    def collect_feedback(self, query: str, response: str, rating: int, comments: str = "") -> Dict[str, Any]:
        """Store feedback about a previous interaction for future adaptation."""
        feedback_entry = self.feedback_manager.add_feedback(query, response, rating, comments)
        self._store_feedback_memory(feedback_entry)
        return {
            "query": query,
            "response": response,
            "rating": rating,
            "comments": comments,
            "tags": feedback_entry.tags,
            "timestamp": feedback_entry.timestamp
        }

    def explain_adaptation(self) -> str:
        """Return a human-readable explanation of the current adaptive behavior."""
        return self.feedback_manager.get_adaptation_explanation()

    def _store_feedback_memory(self, entry: Any) -> None:
        """Persist feedback as long-term memory for future session awareness."""
        if not self.memory_manager._contains_pii(entry.comments):
            self.memory_manager.add_memory(
                content=f"Feedback: {entry.comments}",
                summary=f"Feedback rating {entry.rating}",
                memory_type="long_term",
                tags=["feedback", "ignore_retrieval"]
            )

    def _apply_feedback_adjustments(self, query: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """Adjust responses based on accumulated feedback signals."""
        if not self.feedback_manager.should_adjust_behavior():
            return result

        if result.get("tool_used"):
            return result

        top_cue = self.feedback_manager.get_top_cue()
        if not top_cue:
            return result

        original_response = result["response"]
        adjusted_response = original_response

        if top_cue == "clarity":
            adjusted_response = self._simplify_response(adjusted_response)
        elif top_cue == "conciseness":
            adjusted_response = self._shorten_response(adjusted_response)
        elif top_cue == "detail":
            adjusted_response = self._add_specific_details(adjusted_response, query)
        elif top_cue == "examples":
            adjusted_response = self._add_example(adjusted_response, query)
        elif top_cue == "escalation":
            adjusted_response = self._offer_escalation(adjusted_response)

        if adjusted_response != original_response:
            result["response"] = adjusted_response
            result["metadata"] = result.get("metadata", {})
            result["metadata"]["adaptive_applied"] = top_cue
            result["metadata"]["adaptive_explanation"] = self.explain_adaptation()
            result["metadata"]["adaptive_action"] = top_cue
            result["adaptive_applied"] = True
            result["adaptive_action"] = top_cue
            result["phase"] = self.adaptation_phase
            self._log_interaction(self._build_state(query, adjusted_response, result.get("category", "unknown"), result.get("confidence", 0.0)))

        return result

    def _simplify_response(self, response: str) -> str:
        sentences = response.split(". ")
        summary = ". ".join(sentences[:2]).strip()
        if not summary.endswith("."):
            summary += "."
        return summary + " Please let me know if you'd like this explained in simpler terms."

    def _shorten_response(self, response: str) -> str:
        sentences = response.split(". ")
        excerpt = ". ".join(sentences[:2]).strip()
        if not excerpt.endswith("."):
            excerpt += "."
        return excerpt + " If you'd like more detail, I can provide it."

    def _add_specific_details(self, response: str, query: str) -> str:
        details = "\n\nHere are some concrete options you can consider:\n"
        details += "• Equipment Term Loan: fixed-rate financing for machinery and vehicles.\n"
        details += "• Equipment Lease: lower upfront cost and flexible term structure.\n"
        details += "• Vendor Financing: dealer-supported financing for certified equipment.\n"

        if "documents" in query.lower() or "application" in query.lower():
            details = "\n\nHere are the key documents to prepare:\n"
            details += "• Business registration and GST/Tax documents.\n"
            details += "• Equipment quote, invoice, and valuation report.\n"
            details += "• Financial statements and credit details.\n"

        return response + details + "\nPlease tell me if you want one of these options explained in more detail."

    def _add_example(self, response: str, query: str) -> str:
        example = "\n\nFor example, if you finance a CNC machine for manufacturing, "
        example += "you may choose an Equipment Term Loan with a 60-month schedule and a fixed-rate repayment plan."
        return response + example

    def _offer_escalation(self, response: str) -> str:
        return response + "\n\nIf you'd like, I can also connect you with a specialist for a more detailed review." 

    def export_adaptive_logs(self, output_dir: str = "outputs") -> str:
        output_path = Path(output_dir) / f"adaptive_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        export_data = {
            "phase": self.adaptation_phase,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "feedback_summary": self.feedback_manager.get_feedback_summary(),
            "feedback_entries": [entry.__dict__ for entry in self.feedback_manager.entries],
            "memory": self.memory_manager.get_memory_snapshot(),
            "interactions": self.interactions
        }
        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2)
        logger.info(f"Exported adaptive logs to {output_path}")
        return str(output_path)
