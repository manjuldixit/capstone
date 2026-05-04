"""Memory manager for Phase 6.

Handles short-term and long-term memory, relevance retrieval, and reset rules.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

MEMORY_PII_PATTERNS = [
    r'\b\d{3}-\d{2}-\d{4}\b',
    r'\b\d{10,16}(?!\d)\b',
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
]

PROFILE_PATTERNS = {
    "credit_score": r'(?P<credit_score>\d{3})\s*(?:credit score|score)',
    "business_type": r'\b(manufacturing|construction|dealer|procurement|logistics|services)\b',
    "equipment_type": r'\b(CNC machine|excavator|forklift|printer|compressor|generator|machinery|equipment)\b',
    "loan_term": r'(?P<loan_term>\d{1,3})\s*(months|month|years|year|term)',
    "loan_amount": r'\$?([0-9,]+(?:\.[0-9]+)?)'
}


@dataclass
class MemoryEntry:
    memory_type: str
    content: str
    summary: str
    timestamp: str
    tags: List[str] = field(default_factory=list)
    source: str = "user"


class MemoryManager:
    """Stores and retrieves memory for multi-turn conversations."""

    def __init__(self, short_term_capacity: int = 5):
        self.short_term_capacity = short_term_capacity
        self.short_term_memory: List[MemoryEntry] = []
        self.long_term_memory: List[MemoryEntry] = []

    @staticmethod
    def _contains_pii(text: str) -> bool:
        return any(re.search(pattern, text) for pattern in MEMORY_PII_PATTERNS)

    def add_memory(
        self,
        content: str,
        summary: str,
        memory_type: str = "short_term",
        tags: Optional[List[str]] = None,
        source: str = "user"
    ) -> bool:
        """Add a memory entry if it does not contain PII."""
        if self._contains_pii(content):
            return False

        entry = MemoryEntry(
            memory_type=memory_type,
            content=content,
            summary=summary,
            timestamp=datetime.now().isoformat(),
            tags=tags or [],
            source=source
        )

        if memory_type == "long_term":
            self.long_term_memory.append(entry)
        else:
            self.short_term_memory.append(entry)
            self._enforce_short_term_limit()

        return True

    def _enforce_short_term_limit(self) -> None:
        """Keep the short-term memory within the configured capacity."""
        while len(self.short_term_memory) > self.short_term_capacity:
            self.short_term_memory.pop(0)

    def retrieve_relevant(self, query: str, top_k: int = 3) -> List[MemoryEntry]:
        """Return the most relevant memories for a query."""
        query_tokens = set(re.findall(r"\w+", query.lower()))

        def score(entry: MemoryEntry) -> int:
            text = " ".join([entry.content, entry.summary, " ".join(entry.tags)]).lower()
            tokens = set(re.findall(r"\w+", text))
            return len(query_tokens & tokens) + (2 if entry.memory_type == "long_term" else 0)

        all_memory = [entry for entry in self.long_term_memory + self.short_term_memory if "ignore_retrieval" not in entry.tags]
        scored = sorted(all_memory, key=score, reverse=True)
        return [entry for entry in scored if score(entry) > 0][:top_k]

    def summarize_relevant(self, query: str, top_k: int = 3) -> str:
        """Build a short summary from relevant memories."""
        relevant = self.retrieve_relevant(query, top_k=top_k)
        if not relevant:
            return ""

        summaries = [entry.summary for entry in relevant]
        if len(summaries) == 1:
            return summaries[0]
        return "; ".join(summaries)

    def clear_short_term_memory(self) -> None:
        self.short_term_memory = []

    def clear_long_term_memory(self) -> None:
        self.long_term_memory = []

    def clear_all_memory(self) -> None:
        self.clear_short_term_memory()
        self.clear_long_term_memory()

    def extract_profile_facts(self, query: str) -> List[Dict[str, Any]]:
        """Extract profile-style facts from the user query."""
        facts = []

        query_lower = query.lower()
        for fact_type, pattern in PROFILE_PATTERNS.items():
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                if fact_type == "credit_score":
                    facts.append({
                        "type": "credit_score",
                        "value": int(match.group("credit_score")),
                        "summary": f"credit score {match.group('credit_score')}"
                    })
                elif fact_type == "loan_term":
                    facts.append({
                        "type": "loan_term",
                        "value": int(match.group("loan_term")),
                        "summary": f"loan term {match.group('loan_term')} months"
                    })
                elif fact_type == "loan_amount":
                    amount = float(match.group(1).replace(",", ""))
                    facts.append({
                        "type": "loan_amount",
                        "value": amount,
                        "summary": f"loan amount ${amount:,.2f}"
                    })
                else:
                    facts.append({
                        "type": fact_type,
                        "value": match.group(0).strip(),
                        "summary": match.group(0).strip()
                    })

        return facts

    def promote_profile_memory(self, query: str) -> None:
        """Promote detected user profile facts to long-term memory."""
        facts = self.extract_profile_facts(query)
        if not facts:
            return

        for fact in facts:
            self.add_memory(
                content=fact["summary"],
                summary=fact["summary"],
                memory_type="long_term",
                tags=[fact["type"]],
                source="profile"
            )

    def get_memory_snapshot(self) -> Dict[str, Any]:
        """Return a structured snapshot of current memory."""
        return {
            "short_term_memory": [entry.__dict__ for entry in self.short_term_memory],
            "long_term_memory": [entry.__dict__ for entry in self.long_term_memory]
        }
