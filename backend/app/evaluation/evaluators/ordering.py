"""ordering: the learner arranges steps; authored order is the correct one."""

from app.content.schemas.exercise import OrderingExercise
from app.evaluation.context import EvalContext
from app.evaluation.feedback import verdict
from app.evaluation.result import EvaluationResult, FeedbackItem, FeedbackKind, Outcome
from app.evaluation.submission import OrderingSubmission


def evaluate_ordering(
    ex: OrderingExercise, sub: OrderingSubmission, ctx: EvalContext
) -> EvaluationResult:
    steps = ex.spec.steps
    expected = [s.id for s in steps]
    if sorted(sub.order) != sorted(expected):
        return EvaluationResult(
            outcome=Outcome.INVALID,
            score=0,
            feedback=[
                verdict(Outcome.INVALID, "Τοποθέτησε όλα τα βήματα, από μία φορά το καθένα.")
            ],
        )

    in_place = sum(a == b for a, b in zip(sub.order, expected, strict=True))
    score = in_place / len(expected)
    outcome = (
        Outcome.CORRECT
        if in_place == len(expected)
        else Outcome.PARTIAL
        if in_place
        else Outcome.INCORRECT
    )

    feedback = [verdict(outcome)]
    if outcome is not Outcome.CORRECT:
        first_wrong = next(
            i for i, (a, b) in enumerate(zip(sub.order, expected, strict=True)) if a != b
        )
        feedback.append(
            FeedbackItem(
                kind=FeedbackKind.MISTAKE,
                text=f"Η πρώτη απόκλιση είναι στο βήμα {first_wrong + 1}.",
            )
        )
    feedback.append(
        FeedbackItem(
            kind=FeedbackKind.CORRECT_ANSWER,
            code=[f"{i}. {s.text}" for i, s in enumerate(steps, 1)],
        )
    )
    feedback.append(FeedbackItem(kind=FeedbackKind.WHY, text=ex.explanation))
    return EvaluationResult(outcome=outcome, score=score, matched_rule=None, feedback=feedback)
