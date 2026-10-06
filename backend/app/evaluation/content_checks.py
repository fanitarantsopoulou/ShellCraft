"""Content checks that need the evaluator: every authored test case must behave as declared.

Plugged into content lint so a broken exercise can never be merged.
"""

from app.content.lint import Issue, Severity
from app.content.loader import ContentBundle
from app.content.schemas.exercise import CommandWritingExercise
from app.evaluation.context import EvalContext
from app.evaluation.evaluators.command import disallowed_features, to_canonical
from app.evaluation.registry import evaluate
from app.evaluation.result import Outcome
from app.evaluation.shell.parser import ShellSyntaxError, UnsupportedSyntax, parse


def check_command_exercises(bundle: ContentBundle) -> list[Issue]:
    ctx = EvalContext(commands=bundle.commands)
    issues: list[Issue] = []
    for ex in bundle.exercises.values():
        if not isinstance(ex, CommandWritingExercise):
            continue
        loc = bundle.origins.get(("exercise", ex.id), ex.id)

        def err(msg: str, loc: str = loc) -> None:
            issues.append(Issue(Severity.ERROR, loc, msg))

        # Every accepted answer and known mistake must itself be parseable and allowed.
        patterns = [("accepted", a) for a in ex.spec.accepted] + [
            ("known_mistake", m.match) for m in ex.spec.known_mistakes
        ]
        canon = {}
        for label, text in patterns:
            try:
                line = parse(text)
            except (ShellSyntaxError, UnsupportedSyntax) as exc:
                err(f"{label} {text!r} cannot be parsed: {exc}")
                continue
            if blocked := disallowed_features(line, ex.spec.allow):
                err(f"{label} {text!r} uses {blocked[0]} which the exercise does not allow")
            canon[(label, text)] = to_canonical(text, ex, ctx)

        for name, flags in ex.spec.optional_flags.items():
            spec = ctx.command_by_name(name)
            if spec is None:
                err(f"optional_flags names {name!r}, which is not in the command reference")
                continue
            for flag in flags:
                if spec.option_for(flag) is None:
                    err(f"optional flag {flag!r} is not an option of {name!r}")

        accepted = {canon[k] for k in canon if k[0] == "accepted"}
        for (label, text), form in canon.items():
            if label == "known_mistake" and form in accepted:
                err(f"known_mistake {text!r} is equivalent to an accepted answer")

        for case in ex.spec.test_cases.accept:
            result = evaluate(ex, {"command": case}, ctx)
            if result.outcome is not Outcome.CORRECT:
                err(f"test case should be accepted but was {result.outcome}: {case!r}")
        for case in ex.spec.test_cases.reject:
            result = evaluate(ex, {"command": case}, ctx)
            if result.outcome is Outcome.CORRECT:
                rule = result.matched_rule
                err(f"test case should be rejected but was accepted ({rule}): {case!r}")
    return issues
