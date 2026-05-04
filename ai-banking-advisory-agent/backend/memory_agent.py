"""Phase 6: Multi-turn memory and planning agent for equipment financing."""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from tool_agent import EquipmentFinancingToolAgent
from memory_manager import MemoryManager
from toolbox import ToolExecutionError

logger = logging.getLogger(__name__)


class EquipmentFinancingMemoryAgent(EquipmentFinancingToolAgent):
    """Agent that uses short-term and long-term memory plus planning."""

    MEMORY_RESET_KEYWORDS = [
        "forget", "reset memory", "clear memory", "start over", "erase previous", "forget details"
    ]
    PLAN_TRIGGERS = [
        "plan", "help me", "what should", "guide me", "next steps", "step-by-step", "roadmap"
    ]

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
            max_tool_calls=max_tool_calls
        )
        self.memory_manager = MemoryManager(short_term_capacity=short_term_capacity)
        self.memory_phase = "phase_6_planning_memory"
        logger.info("Memory-enabled agent initialized for Phase 6")

    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a query with planning and memory support."""
        query = query.strip()
        is_valid, validation_msg = self._validate_input(query)
        if not is_valid:
            return self._create_error_response(query, validation_msg)

        if self._should_reset_memory(query):
            return self._handle_memory_reset(query)

        if self.tool_manager.contains_pii(query):
            return self._create_error_response(
                query,
                "I cannot process requests that contain personal or sensitive data."
            )

        if self.tool_manager.is_out_of_scope(query):
            return self._create_error_response(
                query,
                "That request is out of scope for this equipment financing assistant."
            )

        tool = self.tool_manager.select_tool(query)
        if tool:
            result = self._run_tool_path(query, tool)
            self._update_memory(query, result)
            return result

        if self._is_planning_query(query):
            plan = self._plan_query(query)
            response = self._format_plan_response(query, plan)
            result = self._build_memory_response(query, response, "planning", 0.80)
            self._update_memory(query, result)
            return result

        return self._run_memory_augmented_query(query)

    def _is_planning_query(self, query: str) -> bool:
        """Detect whether the user is asking for planning help."""
        query_lower = query.lower()
        return any(trigger in query_lower for trigger in self.PLAN_TRIGGERS)

    def _run_memory_augmented_query(self, query: str) -> Dict[str, Any]:
        """Run a RAG-enabled query and augment with memory context."""
        base_result = super().process_query(query)
        memory_summary = self.memory_manager.summarize_relevant(query)

        if memory_summary:
            augmented_response = (
                f"As a reminder from our earlier conversation, {memory_summary}. "
                f"Here is the most relevant answer I can provide now:\n\n{base_result['response']}"
            )
            base_result["response"] = augmented_response
            base_result["metadata"] = base_result.get("metadata", {})
            base_result["metadata"]["memory_used"] = True
            base_result["metadata"]["memory_summary"] = memory_summary
            base_result["memory_used"] = True
            base_result["memory_summary"] = memory_summary
        else:
            base_result["memory_used"] = False
            base_result["memory_summary"] = None

        base_result["phase"] = self.memory_phase
        self._update_memory(query, base_result)
        return base_result

    def _plan_query(self, query: str) -> List[str]:
        """Create a simple planning sequence for multi-step queries."""
        steps = [
            "Understand the equipment financing goal and the type of equipment.",
            "Confirm the customer's credit profile and eligibility requirements.",
            "Estimate financing costs, payment schedule, and loan structure.",
            "Identify required documentation and the next application steps."
        ]

        if "manufacturing" in query.lower() or "construction" in query.lower():
            steps.insert(1, "Identify the business sector and asset use case for the financing.")

        if "credit score" in query.lower() or "eligible" in query.lower():
            steps.insert(2, "Verify the customer's credit score and documentation readiness.")

        return steps

    def _format_plan_response(self, query: str, plan: List[str]) -> str:
        """Render a planning response for the user."""
        plan_text = "\n".join(f"{idx + 1}. {step}" for idx, step in enumerate(plan))
        return (
            "I can help you plan your equipment financing in a few clear steps. "
            "Here is the recommended approach:\n\n" + plan_text +
            "\n\nIf you provide a few details like the equipment type, loan amount, "
            "and your credit score, I can give you a more tailored recommendation."
        )

    def _should_reset_memory(self, query: str) -> bool:
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.MEMORY_RESET_KEYWORDS)

    def _handle_memory_reset(self, query: str) -> Dict[str, Any]:
        self.memory_manager.clear_all_memory()
        response = (
            "I have forgotten earlier details from this session. "
            "We can start fresh with your new equipment financing question."
        )
        return self._build_memory_response(query, response, "memory_reset", 0.75)

    def _build_memory_response(self, query: str, response: str, category: str, confidence: float) -> Dict[str, Any]:
        state = self._build_state(query, response, category, confidence)
        state["metadata"]["phase"] = self.memory_phase
        self._log_interaction(state)
        return {
            "query": query,
            "response": response,
            "category": category,
            "confidence": confidence,
            "sources": [],
            "phase": self.memory_phase,
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "memory_used": False,
            "memory_summary": None
        }

    def _build_state(self, query: str, response: str, category: str, confidence: float) -> Dict[str, Any]:
        return {
            "query": query,
            "response": response,
            "category": category,
            "confidence": confidence,
            "sources": [],
            "session_id": self.session_id,
            "turn_number": self.turn_number,
            "conversation_history": self.conversation_history,
            "timestamp": datetime.now().isoformat(),
            "metadata": {}
        }

    def _update_memory(self, query: str, result: Dict[str, Any]) -> None:
        """Update memory after each interaction."""
        self.turn_number += 1
        self.conversation_history.append({"role": "user", "content": query})
        self.conversation_history.append({"role": "assistant", "content": result["response"]})

        self.memory_manager.add_memory(
            content=query,
            summary=query,
            memory_type="short_term",
            tags=[result.get("category", "unknown")],
            source="user"
        )

        self.memory_manager.promote_profile_memory(query)

    def export_memory_logs(self, output_dir: str = "outputs") -> str:
        output_path = Path(output_dir) / f"memory_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        export_data = {
            "phase": self.memory_phase,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "memory": self.memory_manager.get_memory_snapshot(),
            "interactions": self.interactions
        }
        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2)
        logger.info(f"Exported memory logs to {output_path}")
        return str(output_path)
