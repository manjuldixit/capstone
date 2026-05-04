"""
Toolbox for Phase 5: Enable tool usage for the equipment financing agent.
"""

import logging
import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

PII_PATTERNS = [
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
    r'\b\d{3}-\d{2}-\d{4}\b',
    r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
]

OUT_OF_SCOPE_KEYWORDS = [
    "transfer", "withdraw", "deposit", "account", "balance", "payment method"
]

@dataclass
class ToolSchema:
    name: str
    description: str
    parameters: Dict[str, str]
    function: Callable[..., Dict[str, Any]]


class ToolExecutionError(Exception):
    pass


def credit_score_assessment_tool(credit_score: int) -> Dict[str, Any]:
    """Assess financing eligibility based on credit score."""
    if credit_score < 300 or credit_score > 850:
        raise ToolExecutionError("Credit score must be between 300 and 850.")

    if credit_score >= 750:
        tier = "excellent"
        recommendation = (
            "Your credit score is excellent. You should qualify for the best rates "
            "and more favorable financing terms."
        )
    elif credit_score >= 700:
        tier = "good"
        recommendation = (
            "Your credit score is good. You are likely eligible for competitive rates, "
            "but the exact offer may depend on your business profile."
        )
    elif credit_score >= 620:
        tier = "standard"
        recommendation = (
            "Your credit score is standard. You may qualify for financing, "
            "though rates may be higher and additional documentation may be required."
        )
    else:
        tier = "subprime"
        recommendation = (
            "With a lower credit score, financing may still be possible, "
            "but you should expect higher rates and stricter eligibility checks."
        )

    return {
        "tool_name": "credit_score_assessment",
        "success": True,
        "credit_score": credit_score,
        "tier": tier,
        "recommendation": recommendation,
        "response": (
            f"Credit score {credit_score} maps to the {tier} tier. {recommendation}"
        )
    }


def loan_calculator_tool(amount: float, term_months: int, apr: float = 8.0) -> Dict[str, Any]:
    """Estimate monthly payments for equipment financing."""
    if amount <= 0:
        raise ToolExecutionError("Loan amount must be greater than zero.")
    if term_months <= 0:
        raise ToolExecutionError("Loan term must be greater than zero months.")
    if apr <= 0:
        raise ToolExecutionError("APR must be greater than zero.")

    monthly_rate = apr / 100 / 12
    payment = amount * monthly_rate / (1 - (1 + monthly_rate) ** -term_months)

    return {
        "tool_name": "loan_payment_calculator",
        "success": True,
        "amount": amount,
        "term_months": term_months,
        "apr": apr,
        "monthly_payment": round(payment, 2),
        "response": (
            f"Estimated monthly payment for ${amount:,.2f} over {term_months} months "
            f"at {apr:.2f}% APR is ${payment:,.2f}."
        )
    }


class ToolManager:
    """Selects and executes tools with guardrails."""

    def __init__(self):
        self.tools: List[ToolSchema] = [
            ToolSchema(
                name="loan_payment_calculator",
                description="Estimate monthly equipment financing payments.",
                parameters={
                    "amount": "Loan amount in USD",
                    "term_months": "Loan term in months",
                    "apr": "Annual percentage rate"
                },
                function=loan_calculator_tool
            ),
            ToolSchema(
                name="credit_score_assessment",
                description="Assess credit-based eligibility for financing.",
                parameters={
                    "credit_score": "Numeric credit score value between 300 and 850"
                },
                function=credit_score_assessment_tool
            )
        ]

    def contains_pii(self, query: str) -> bool:
        return any(re.search(pattern, query) for pattern in PII_PATTERNS)

    def is_out_of_scope(self, query: str) -> bool:
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in OUT_OF_SCOPE_KEYWORDS)

    def is_safe(self, query: str) -> bool:
        if self.contains_pii(query):
            logger.warning("Query contains PII; tool usage blocked.")
            return False
        if self.is_out_of_scope(query):
            logger.warning("Query is out of scope; tool usage blocked.")
            return False
        return True

    def select_tool(self, query: str) -> Optional[ToolSchema]:
        query_lower = query.lower()
        # Specific credit score requests
        if any(keyword in query_lower for keyword in ["credit score", "qualify", "eligible", "eligible", "approval", "creditworthiness"]):
            return self._get_tool("credit_score_assessment")

        # Payment and amount-based requests
        if any(keyword in query_lower for keyword in ["payment", "monthly", "calculate", "cost", "amount", "term", "apr"]):
            return self._get_tool("loan_payment_calculator")

        return None

    def _get_tool(self, tool_name: str) -> Optional[ToolSchema]:
        for tool in self.tools:
            if tool.name == tool_name:
                return tool
        return None

    def parse_tool_inputs(self, tool: ToolSchema, query: str) -> Dict[str, Any]:
        if tool.name == "credit_score_assessment":
            match = re.search(r"(\d{3})", query)
            if not match:
                raise ToolExecutionError("Could not detect a credit score in the query.")
            score = int(match.group(1))
            return {"credit_score": score}

        if tool.name == "loan_payment_calculator":
            amount_match = re.search(r"\$?([0-9,]+(?:\.[0-9]+)?)", query.replace(",", ""))
            term_match = re.search(r"(\d{1,3})\s*(months|month|years|year|term)", query.lower())
            apr_match = re.search(r"(\d+(?:\.\d+)?)\s*%\s*apr", query.lower())

            if not amount_match or not term_match:
                raise ToolExecutionError(
                    "Missing loan amount or term. Please ask with both amount and months."
                )

            amount = float(amount_match.group(1))
            term_value = int(term_match.group(1))
            term_unit = term_match.group(2)
            term_months = term_value * 12 if "year" in term_unit else term_value
            apr = float(apr_match.group(1)) if apr_match else 8.0
            return {"amount": amount, "term_months": term_months, "apr": apr}

        raise ToolExecutionError(f"No parser available for tool {tool.name}.")

    def execute_tool(self, tool: ToolSchema, query: str) -> Dict[str, Any]:
        if not self.is_safe(query):
            raise ToolExecutionError("Tool execution blocked by safety guardrails.")

        inputs = self.parse_tool_inputs(tool, query)
        logger.info(f"Executing tool {tool.name} with inputs {inputs}")
        return tool.function(**inputs)
