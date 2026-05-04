"""
Phase 5 Tool Agent for equipment financing.
Supports tool selection, execution, guardrails, and loop prevention.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from rag_agent import EquipmentFinancingRAG
from toolbox import ToolManager, ToolExecutionError

logger = logging.getLogger(__name__)


class EquipmentFinancingToolAgent(EquipmentFinancingRAG):
    """Agent that can choose and use tools safely."""

    def __init__(
        self,
        kb_path: str = "data/knowledge_base.json",
        retriever_db_path: str = "data/chroma_db",
        max_tool_calls: int = 2
    ):
        super().__init__(kb_path=kb_path, retriever_db_path=retriever_db_path)
        self.tool_manager = ToolManager()
        self.max_tool_calls = max_tool_calls
        self.tool_call_log = []

    def process_query(self, query: str) -> Dict[str, Any]:
        """Process query with optional tool invocation."""
        is_valid, validation_msg = self._validate_input(query)
        if not is_valid:
            return self._create_error_response(query, validation_msg)

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
            return self._run_tool_path(query, tool)

        # No tool needed; fall back to RAG behavior
        return super().process_query(query)

    def _run_tool_path(self, query: str, tool: Any) -> Dict[str, Any]:
        """Execute tool and handle success or failure."""
        if len(self.tool_call_log) >= self.max_tool_calls:
            return self._create_error_response(
                query,
                "Tool usage limit reached for this session. Please ask a simpler question."
            )

        try:
            tool_result = self.tool_manager.execute_tool(tool, query)
            self.tool_call_log.append(tool.name)
            return self._format_tool_response(query, tool_result)
        except ToolExecutionError as exc:
            logger.warning(f"Tool execution failed: {exc}")
            return self._handle_tool_failure(query, tool.name, str(exc))

    def _format_tool_response(self, query: str, tool_result: Dict[str, Any]) -> Dict[str, Any]:
        """Format a user-facing response from tool output."""
        response = tool_result.get("response", "Tool executed successfully.")
        category_state = self._categorize_query(self._build_state(query, response, "", 0.0))
        category = category_state["category"]
        state = self._build_state(query, response, category, confidence=0.85)
        state["metadata"]["tool_used"] = tool_result.get("tool_name")
        state["metadata"]["tool_output"] = {k: v for k, v in tool_result.items() if k != "response"}
        state["metadata"]["phase"] = "phase_5_tool_usage"
        self._log_interaction(state)

        return {
            "query": query,
            "response": response,
            "category": category,
            "confidence": 0.85,
            "sources": [],
            "phase": "phase_5_tool_usage",
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "tool_used": tool_result.get("tool_name"),
            "tool_output": tool_result
        }

    def _handle_tool_failure(self, query: str, tool_name: str, error_message: str) -> Dict[str, Any]:
        """Safe fallback for failed tool invocations."""
        response = (
            "I attempted to use a tool to answer that request, but the tool could not complete it. "
            "Please provide more details or ask a different question."
        )
        category_state = self._categorize_query(self._build_state(query, response, "", 0.0))
        category = category_state["category"]
        state = self._build_state(query, response, category, confidence=0.45)
        state["metadata"]["tool_used"] = tool_name
        state["metadata"]["tool_error"] = error_message
        state["metadata"]["phase"] = "phase_5_tool_failure"
        self._log_interaction(state)

        return {
            "query": query,
            "response": response,
            "category": category,
            "confidence": 0.45,
            "sources": [],
            "phase": "phase_5_tool_failure",
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "tool_used": tool_name,
            "tool_error": error_message
        }

    def _build_state(self, query: str, response: str, category: str, confidence: float) -> Dict[str, Any]:
        """Build a state dict for logging and response generation."""
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

    def export_tool_logs(self, output_dir: str = "outputs") -> str:
        """Export tool agent logs and tool usage metadata."""
        output_path = Path(output_dir) / f"tool_agent_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        export_data = {
            "phase": "phase_5_tool_usage",
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "interactions": self.interactions,
            "tool_history": self.tool_call_log
        }
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        logger.info(f"Exported tool logs to {output_path}")
        return str(output_path)
