"""fill_in_command: each blank is compared (whitespace-collapsed, case-sensitive)."""

import re

from app.content.schemas.exercise import BLANK, FillInCommandExercise
from app.evaluation.context import EvalContext
from app.evaluation.feedback import reference_feedback, reference_for, verdict
from app.evaluation.result import EvaluationResult, FeedbackItem, FeedbackKind, Outcome
from app.evaluation.submission import FillInSubmission

_WS = re.compile(r"\s+")


def _clean(text: str) -> str:
    return _WS.sub(" ", text.strip())


def fill(template: str, values: list[str]) -> str:
    out = template
    for value in values:
        out = out.replace(BLANK, value, 1)
    return out


def evaluate_fill_in(
    ex: FillInCommandExercise, sub: FillInSubmission, ctx: EvalContext
) -> EvaluationResult:
    blanks = ex.spec.blanks
    if len(sub.blanks) != len(blanks):
        return EvaluationResult(
            outcome=Outcome.INVALID,
            score=0,
            feedback=[verdict(Outcome.INVALID, f"Συμπλήρωσε και τα {len(blanks)} κενά.")],
        )

    answers = [_clean(a) for a in sub.blanks]
    mistakes: list[FeedbackItem] = []
    rules: list[str] = []
    right = 0
    for i, (answer, blank) in enumerate(zip(answers, blanks, strict=True)):

        def same(a: str, b: str, blank=blank) -> bool:
            return a == b if blank.case_sensitive else a.casefold() == b.casefold()

        if any(same(answer, _clean(a)) for a in blank.accepted):
            right += 1
            rules.append(f"{i}:ok")
            continue
        rules.append(f"{i}:wrong")
        for mistake in blank.known_mistakes:
            if same(answer, _clean(mistake.match)):
                mistakes.append(
                    FeedbackItem(kind=FeedbackKind.MISTAKE, text=mistake.feedback, code=[answer])
                )
                rules[-1] = f"{i}:mistake:{mistake.id}"
                break

    score = right / len(blanks)
    outcome = (
        Outcome.CORRECT if right == len(blanks) else Outcome.PARTIAL if right else Outcome.INCORRECT
    )
    expected = fill(ex.spec.template, [b.accepted[0] for b in blanks])
    feedback = [
        verdict(outcome),
        *mistakes,
        FeedbackItem(kind=FeedbackKind.CORRECT_ANSWER, code=[expected]),
        FeedbackItem(kind=FeedbackKind.WHY, text=ex.explanation),
        *reference_feedback(
            reference_for(ctx, ex.reference), submitted=fill(ex.spec.template, answers)
        ),
    ]
    return EvaluationResult(
        outcome=outcome, score=score, matched_rule=",".join(rules), feedback=feedback
    )
