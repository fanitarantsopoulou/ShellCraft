"""multiple_choice, command_selection and output_analysis share one evaluator."""

from app.content.schemas.exercise import (
    CommandSelectionExercise,
    MultipleChoiceExercise,
    OutputAnalysisExercise,
)
from app.evaluation.context import EvalContext
from app.evaluation.feedback import option_feedback, reference_feedback, reference_for, verdict
from app.evaluation.result import EvaluationResult, FeedbackItem, FeedbackKind, Outcome
from app.evaluation.submission import ChoiceSubmission

ChoiceExercise = MultipleChoiceExercise | CommandSelectionExercise | OutputAnalysisExercise


def evaluate_choice(
    ex: ChoiceExercise, sub: ChoiceSubmission, ctx: EvalContext
) -> EvaluationResult:
    options = {o.id: o for o in ex.spec.options}
    selected = list(dict.fromkeys(sub.selected))  # de-duplicate, keep order
    unknown = [s for s in selected if s not in options]
    if unknown or (not ex.spec.multi_select and len(selected) != 1):
        return EvaluationResult(
            outcome=Outcome.INVALID,
            score=0,
            feedback=[verdict(Outcome.INVALID, "Διάλεξε μία από τις διαθέσιμες επιλογές.")],
        )

    correct = {o.id for o in ex.spec.options if o.correct}
    chosen = set(selected)
    hits, wrong = len(chosen & correct), len(chosen - correct)
    score = max(0.0, (hits - wrong) / len(correct))
    if chosen == correct:
        outcome = Outcome.CORRECT
    elif score > 0:
        outcome = Outcome.PARTIAL
    else:
        outcome = Outcome.INCORRECT

    feedback = [verdict(outcome)]
    feedback.append(
        FeedbackItem(
            kind=FeedbackKind.CORRECT_ANSWER,
            code=[o.text for o in ex.spec.options if o.correct],
        )
    )
    feedback.append(FeedbackItem(kind=FeedbackKind.WHY, text=ex.explanation))
    feedback.extend(option_feedback(options[s]) for s in selected if s not in correct)
    feedback.extend(reference_feedback(reference_for(ctx, ex.reference)))
    return EvaluationResult(
        outcome=outcome, score=score, matched_rule=",".join(sorted(chosen)), feedback=feedback
    )
