"""Single entry point: route an exercise + submission to the right evaluator."""

from collections.abc import Callable
from typing import Any

from pydantic import TypeAdapter, ValidationError

from app.content.schemas import Exercise
from app.evaluation.context import EvalContext
from app.evaluation.evaluators.choice import evaluate_choice
from app.evaluation.evaluators.command import evaluate_command
from app.evaluation.evaluators.fill_in import evaluate_fill_in
from app.evaluation.evaluators.ordering import evaluate_ordering
from app.evaluation.feedback import verdict
from app.evaluation.result import EvaluationResult, Outcome
from app.evaluation.submission import (
    ChoiceSubmission,
    CommandSubmission,
    FillInSubmission,
    OrderingSubmission,
)

_EVALUATORS: dict[str, tuple[type, Callable[[Any, Any, EvalContext], EvaluationResult]]] = {
    "multiple_choice": (ChoiceSubmission, evaluate_choice),
    "command_selection": (ChoiceSubmission, evaluate_choice),
    "output_analysis": (ChoiceSubmission, evaluate_choice),
    "fill_in_command": (FillInSubmission, evaluate_fill_in),
    "command_writing": (CommandSubmission, evaluate_command),
    "ordering": (OrderingSubmission, evaluate_ordering),
}


def submission_model(exercise_type: str) -> type:
    return _EVALUATORS[exercise_type][0]


def evaluate(exercise: Exercise, submission: dict[str, Any], ctx: EvalContext) -> EvaluationResult:
    """Validate the raw submission for this exercise type, then evaluate it."""
    model, evaluator = _EVALUATORS[exercise.type]
    try:
        parsed = TypeAdapter(model).validate_python(submission)
    except ValidationError:
        return EvaluationResult(
            outcome=Outcome.INVALID,
            score=0,
            feedback=[verdict(Outcome.INVALID, "Μη έγκυρη μορφή απάντησης.")],
        )
    return evaluator(exercise, parsed, ctx)


def supported_types() -> frozenset[str]:
    return frozenset(_EVALUATORS)
