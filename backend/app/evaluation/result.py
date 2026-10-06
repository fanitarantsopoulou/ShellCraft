"""Evaluation results: structured so the frontend can render rich, educational feedback.

Learner-facing text is Greek.
"""

from enum import StrEnum

from pydantic import BaseModel, Field


class Outcome(StrEnum):
    CORRECT = "correct"
    PARTIAL = "partial"
    INCORRECT = "incorrect"
    INVALID = "invalid"  # the submission could not be evaluated (malformed, unsupported syntax)


class FeedbackKind(StrEnum):
    VERDICT = "verdict"
    CORRECT_ANSWER = "correct_answer"
    WHY = "why"
    MISTAKE = "mistake"  # specific to what the learner submitted
    OPTION = "option"  # explanation of a chosen (wrong) option
    SYNTAX = "syntax"
    BREAKDOWN = "breakdown"
    COMMON_MISTAKE = "common_mistake"
    RELATED = "related"
    SOURCE = "source"


class FeedbackItem(BaseModel):
    kind: FeedbackKind
    text: str = ""
    code: list[str] = []  # code lines shown as a block
    pairs: list[tuple[str, str]] = []  # e.g. token -> meaning
    url: str | None = None


class EvaluationResult(BaseModel):
    outcome: Outcome
    score: float = Field(ge=0, le=1)
    matched_rule: str | None = None
    feedback: list[FeedbackItem] = []

    @property
    def is_correct(self) -> bool:
        return self.outcome is Outcome.CORRECT
