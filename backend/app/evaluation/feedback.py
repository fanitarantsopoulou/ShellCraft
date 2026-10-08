"""Builds the educational part of feedback from the exercise and the command reference.

Evaluators decide *what happened*; this module adds *what to learn from it*, so the same
syntax/related/common-mistake material is not copy-pasted into every exercise.
"""

from app.content.schemas import Command
from app.content.schemas.exercise import Existence, Option
from app.evaluation.context import EvalContext
from app.evaluation.result import FeedbackItem, FeedbackKind, Outcome

VERDICTS = {
    Outcome.CORRECT: "Σωστό!",
    Outcome.PARTIAL: "Σχεδόν, μέρος της απάντησης είναι σωστό.",
    Outcome.INCORRECT: "Όχι ακριβώς.",
    Outcome.INVALID: "Η απάντηση δεν μπόρεσε να αξιολογηθεί.",
}

EXISTENCE_LABEL = {
    Existence.NONEXISTENT: "Αυτή η εντολή δεν υπάρχει.",
    Existence.NOT_INSTALLED: "Αυτή η εντολή δεν είναι εγκατεστημένη από προεπιλογή στο Debian.",
    Existence.PLATFORM_SPECIFIC: "Αυτή η εντολή υπάρχει σε άλλο σύστημα, όχι σε Linux.",
}


def verdict(outcome: Outcome, detail: str = "") -> FeedbackItem:
    text = VERDICTS[outcome] + (f" {detail}" if detail else "")
    return FeedbackItem(kind=FeedbackKind.VERDICT, text=text)


def option_feedback(option: Option) -> FeedbackItem:
    lines = [option.why or ""]
    if option.distractor and option.distractor.existence is not Existence.EXISTS:
        lines.append(EXISTENCE_LABEL[option.distractor.existence])
    if option.distractor and option.distractor.note:
        lines.append(option.distractor.note)
    return FeedbackItem(
        kind=FeedbackKind.OPTION, text=" ".join(x for x in lines if x), code=[option.text]
    )


def reference_feedback(
    command: Command | None, *, submitted: str | None = None
) -> list[FeedbackItem]:
    """Syntax, breakdown, a relevant common mistake, related commands and the source."""
    if command is None:
        return []
    items = [
        FeedbackItem(kind=FeedbackKind.SYNTAX, text=command.summary, code=list(command.synopsis))
    ]
    if command.examples and command.examples[0].explain:
        example = command.examples[0]
        items.append(
            FeedbackItem(
                kind=FeedbackKind.BREAKDOWN,
                code=[example.cmd],
                pairs=[(e.token, e.meaning) for e in example.explain],
            )
        )
    if command.common_mistakes:
        mistake = next(
            (m for m in command.common_mistakes if submitted and m.wrong == submitted),
            command.common_mistakes[0],
        )
        items.append(
            FeedbackItem(kind=FeedbackKind.COMMON_MISTAKE, text=mistake.why, code=[mistake.wrong])
        )
    if command.related:
        items.append(FeedbackItem(kind=FeedbackKind.RELATED, code=[r.id for r in command.related]))
    citation = command.citations[0]
    items.append(
        FeedbackItem(
            kind=FeedbackKind.SOURCE,
            text=f"{command.provider} · {citation.doc_version}",
            url=str(citation.url),
        )
    )
    return items


def reference_for(ctx: EvalContext, command_id: str | None) -> Command | None:
    return ctx.commands.get(command_id) if command_id else None
