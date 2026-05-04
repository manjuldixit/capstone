"""Feedback manager for Phase 7 adaptive behavior.

Stores feedback signals, extracts adaptation cues, and summarizes changes.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


FEEDBACK_TAG_PATTERNS = {
    "clarity": [
        r"unclear", r"confusing", r"vague", r"hard to understand", r"too complex"
    ],
    "conciseness": [
        r"too long", r"wordy", r"verbose", r"too much", r"too many words"
    ],
    "detail": [
        r"too general", r"missing details", r"not enough detail", r"need concrete", r"more specifics"
    ],
    "examples": [
        r"example", r"for example", r"illustrate", r"scenario", r"sample"
    ],
    "escalation": [
        r"specialist", r"human", r"agent", r"someone else", r"help from a person"
    ]
}


@dataclass
class FeedbackEntry:
    query: str
    response: str
    rating: int
    comments: str
    tags: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class FeedbackManager:
    """Collects feedback and exposes adaptation cues."""

    def __init__(self):
        self.entries: List[FeedbackEntry] = []
        self.cue_counts: Dict[str, int] = {key: 0 for key in FEEDBACK_TAG_PATTERNS.keys()}

    def add_feedback(
        self,
        query: str,
        response: str,
        rating: int,
        comments: str = ""
    ) -> FeedbackEntry:
        """Store a feedback entry and update adaptation cues."""
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5.")

        tags = self._extract_tags(comments)
        entry = FeedbackEntry(
            query=query,
            response=response,
            rating=rating,
            comments=comments.strip(),
            tags=tags
        )
        self.entries.append(entry)

        if rating <= 3:
            for tag in tags:
                self.cue_counts[tag] = self.cue_counts.get(tag, 0) + 1

        return entry

    def _extract_tags(self, comments: str) -> List[str]:
        tags: List[str] = []
        text = comments.lower()
        for tag, patterns in FEEDBACK_TAG_PATTERNS.items():
            if any(re.search(pattern, text) for pattern in patterns):
                tags.append(tag)
        if not tags:
            tags.append("general")
        return tags

    def get_top_cue(self) -> Optional[str]:
        if not self.entries:
            return None

        priority = ["detail", "examples", "clarity", "conciseness", "escalation"]
        sorted_cues = sorted(
            self.cue_counts.items(),
            key=lambda item: (item[1], -priority.index(item[0]) if item[0] in priority else 0),
            reverse=True
        )
        top_tag, top_count = sorted_cues[0]
        return top_tag if top_count > 0 else None

    def should_adjust_behavior(self) -> bool:
        return any(entry.rating <= 3 for entry in self.entries)

    def get_feedback_summary(self) -> Dict[str, object]:
        total = len(self.entries)
        if total == 0:
            return {
                "total_feedback": 0,
                "average_rating": None,
                "positive_count": 0,
                "negative_count": 0,
                "top_cue": None
            }

        average_rating = sum(entry.rating for entry in self.entries) / total
        positive_count = sum(1 for entry in self.entries if entry.rating >= 4)
        negative_count = sum(1 for entry in self.entries if entry.rating <= 3)
        top_cue = self.get_top_cue()

        return {
            "total_feedback": total,
            "average_rating": round(average_rating, 2),
            "positive_count": positive_count,
            "negative_count": negative_count,
            "top_cue": top_cue
        }

    def get_adaptation_explanation(self) -> str:
        summary = self.get_feedback_summary()
        if summary["total_feedback"] == 0:
            return "No feedback has been collected yet, so no adaptive changes have been applied."

        top = summary["top_cue"]
        explanation = (
            f"Collected {summary['total_feedback']} feedback entries with an average rating of "
            f"{summary['average_rating']}. "
        )

        if top == "clarity":
            explanation += (
                "The agent is adapting to provide clearer, simpler wording and more direct explanations."
            )
        elif top == "conciseness":
            explanation += (
                "The agent is adapting to deliver shorter, more concise responses and avoid verbosity."
            )
        elif top == "detail":
            explanation += (
                "The agent is adapting to include more concrete details, product names, and specific next steps."
            )
        elif top == "examples":
            explanation += (
                "The agent is adapting to include practical examples and scenario-based guidance."
            )
        elif top == "escalation":
            explanation += (
                "The agent is adapting to offer specialist escalation or human assistance when appropriate."
            )
        else:
            explanation += (
                "The agent is adapting based on general feedback to improve future responses."
            )

        return explanation
