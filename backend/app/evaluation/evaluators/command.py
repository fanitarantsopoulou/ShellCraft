"""command_writing: command-aware comparison against declared accepted answers."""

from app.content.schemas.exercise import CommandWritingExercise, ShellFeature
from app.evaluation.context import EvalContext
from app.evaluation.feedback import reference_feedback, reference_for, verdict
from app.evaluation.result import EvaluationResult, FeedbackItem, FeedbackKind, Outcome
from app.evaluation.shell.normalize import CanonicalCommand, CanonicalLine, canonicalize
from app.evaluation.shell.parser import CommandLine, ShellSyntaxError, UnsupportedSyntax, parse
from app.evaluation.submission import CommandSubmission

FEATURE_MESSAGES = {
    ShellFeature.PIPE: "Σε αυτή την άσκηση δεν χρειάζεται pipe (`|`).",
    ShellFeature.SEQUENCE: "Σε αυτή την άσκηση γράψε μία μόνο εντολή (χωρίς `;`, `&&`, `||`).",
    ShellFeature.REDIRECT: "Σε αυτή την άσκηση δεν χρειάζεται ανακατεύθυνση (`>`, `>>`, `<`).",
}


def disallowed_features(line: CommandLine, allowed: list[ShellFeature]) -> list[ShellFeature]:
    used = {
        ShellFeature.PIPE: line.uses_pipe,
        ShellFeature.SEQUENCE: line.uses_sequence,
        ShellFeature.REDIRECT: line.uses_redirect,
    }
    return [f for f, is_used in used.items() if is_used and f not in allowed]


def _canon(line: CommandLine, ex: CommandWritingExercise, ctx: EvalContext) -> CanonicalLine:
    return canonicalize(
        line,
        ctx,
        strip_dot_slash=ex.spec.normalization.strip_dot_slash,
        optional_flags=ex.spec.optional_flags,
    )


def to_canonical(text: str, ex: CommandWritingExercise, ctx: EvalContext) -> CanonicalLine:
    return _canon(parse(text), ex, ctx)


def _diagnose(sub: CanonicalCommand, expected: CanonicalCommand) -> str | None:
    """A specific, non-misleading hint about the first difference from the expected answer."""
    if sub.name != expected.name:
        return f"Χρησιμοποίησες την εντολή `{sub.name}`, αλλά εδώ χρειάζεται άλλη εντολή."
    if sub.unknown_options:
        flags = ", ".join(f"`{f}`" for f in sub.unknown_options)
        return f"Το {flags} δεν είναι γνωστή επιλογή του `{sub.name}`."
    if sub.missing_values:
        flags = ", ".join(f"`{f}`" for f in sub.missing_values)
        return f"Η επιλογή {flags} χρειάζεται τιμή."
    if len(sub.operands) != len(expected.operands):
        return f"Η εντολή χρειάζεται {len(expected.operands)} ορίσματα, έδωσες {len(sub.operands)}."
    if sorted(sub.operands) == sorted(expected.operands) and sub.operands != expected.operands:
        return "Τα ορίσματα είναι σωστά αλλά σε λάθος σειρά: η σειρά έχει σημασία."
    if sub.options != expected.options:
        return "Οι επιλογές (flags) δεν είναι αυτές που χρειάζονται εδώ."
    if sub.operands != expected.operands:
        return "Κάποιο όρισμα (αρχείο ή διαδρομή) δεν είναι αυτό που ζητήθηκε."
    return None


def _shorthand_notes(submitted: CanonicalLine) -> list[FeedbackItem]:
    return [
        FeedbackItem(
            kind=FeedbackKind.NOTE,
            text=(
                f"Έγραψες τη σύντομη μορφή `{written}`. Δουλεύει στο GNU `{cmd.name}` του Debian, "
                f"αλλά δεν ανήκει πια στο πρότυπο POSIX: η τυπική μορφή είναι `{standard}`, "
                "που δουλεύει παντού."
            ),
        )
        for cmd in submitted.commands
        for written, standard in cmd.shorthands
    ]


def _closest_accepted(
    submitted: CanonicalLine, ex: CommandWritingExercise, ctx: EvalContext
) -> CanonicalLine:
    """The accepted answer to diagnose against: prefer one using the same command names.

    Otherwise `rm -rf old` would be told "use another command" even though `rm -d old`
    is an accepted answer.
    """
    candidates = [to_canonical(a, ex, ctx) for a in ex.spec.accepted]
    names = [c.name for c in submitted.commands]
    return next((c for c in candidates if [x.name for x in c.commands] == names), candidates[0])


def evaluate_command(
    ex: CommandWritingExercise, sub: CommandSubmission, ctx: EvalContext
) -> EvaluationResult:
    text = sub.command.strip()
    reference = reference_for(ctx, ex.reference)

    def invalid(message: str, rule: str) -> EvaluationResult:
        return EvaluationResult(
            outcome=Outcome.INVALID,
            score=0,
            matched_rule=rule,
            feedback=[verdict(Outcome.INVALID, message)],
        )

    try:
        line = parse(text)
    except ShellSyntaxError as exc:
        return invalid(str(exc), "syntax_error")
    except UnsupportedSyntax as exc:
        return invalid(str(exc), f"unsupported:{exc.feature}")
    if blocked := disallowed_features(line, ex.spec.allow):
        return invalid(FEATURE_MESSAGES[blocked[0]], f"disallowed:{blocked[0]}")

    submitted = _canon(line, ex, ctx)
    correct_answer = FeedbackItem(kind=FeedbackKind.CORRECT_ANSWER, code=[ex.spec.accepted[0]])
    why = FeedbackItem(kind=FeedbackKind.WHY, text=ex.explanation)

    for i, accepted in enumerate(ex.spec.accepted):
        if submitted == to_canonical(accepted, ex, ctx):
            feedback = [verdict(Outcome.CORRECT), *_shorthand_notes(submitted)]
            if i > 0:  # accepted alternative: show the canonical form too
                feedback.append(correct_answer)
            feedback.append(why)
            feedback.extend(reference_feedback(reference, submitted=text))
            return EvaluationResult(
                outcome=Outcome.CORRECT, score=1, matched_rule=f"accepted[{i}]", feedback=feedback
            )

    for mistake in ex.spec.known_mistakes:
        if submitted == to_canonical(mistake.match, ex, ctx):
            feedback = [
                verdict(Outcome.INCORRECT),
                FeedbackItem(kind=FeedbackKind.MISTAKE, text=mistake.feedback, code=[text]),
                correct_answer,
                why,
                *reference_feedback(reference, submitted=text),
            ]
            return EvaluationResult(
                outcome=Outcome.INCORRECT,
                score=0,
                matched_rule=f"mistake:{mistake.id}",
                feedback=feedback,
            )

    feedback = [verdict(Outcome.INCORRECT)]
    expected = _closest_accepted(submitted, ex, ctx)
    if len(submitted.commands) == len(expected.commands):
        for got, want in zip(submitted.commands, expected.commands, strict=True):
            if (hint := _diagnose(got, want)) is not None:
                feedback.append(FeedbackItem(kind=FeedbackKind.MISTAKE, text=hint, code=[text]))
                break
    feedback += [correct_answer, why, *reference_feedback(reference, submitted=text)]
    return EvaluationResult(
        outcome=Outcome.INCORRECT, score=0, matched_rule=None, feedback=feedback
    )
