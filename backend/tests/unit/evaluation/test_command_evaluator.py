import pytest

from app.evaluation.context import EvalContext
from app.evaluation.registry import evaluate
from app.evaluation.result import FeedbackKind, Outcome
from tests.factories import command_exercise, cp_command, mv_command

CTX = EvalContext(commands={"cp": cp_command(), "mv": mv_command()})

EX = command_exercise(
    accepted=["cp a.txt b.txt", "cp -i a.txt b.txt"],
    known_mistakes=[
        {"id": "mv", "match": "mv a.txt b.txt", "feedback": "mv renames"},
        {"id": "reversed", "match": "cp b.txt a.txt", "feedback": "order"},
    ],
    optional_flags={"cp": ["-v"]},
)


def run(command: str, ex=EX):
    return evaluate(ex, {"command": command}, CTX)


def kinds(result):
    return [f.kind for f in result.feedback]


@pytest.mark.parametrize(
    ("command", "rule"),
    [
        ("cp a.txt b.txt", "accepted[0]"),
        ("cp ./a.txt b.txt", "accepted[0]"),
        ("cp -v a.txt b.txt", "accepted[0]"),
        ("cp a.txt b.txt --verbose", "accepted[0]"),
        ("cp --interactive a.txt b.txt", "accepted[1]"),
        ("cp -vi a.txt b.txt", "accepted[1]"),
    ],
)
def test_accepts_declared_answers_and_equivalents(command, rule):
    result = run(command)
    assert result.outcome is Outcome.CORRECT
    assert result.score == 1
    assert result.matched_rule == rule


def test_alternative_answer_still_shows_canonical_form():
    assert FeedbackKind.CORRECT_ANSWER in kinds(run("cp -i a.txt b.txt"))
    assert FeedbackKind.CORRECT_ANSWER not in kinds(run("cp a.txt b.txt"))


@pytest.mark.parametrize(
    ("command", "rule"), [("mv a.txt b.txt", "mistake:mv"), ("cp b.txt a.txt", "mistake:reversed")]
)
def test_known_mistakes_get_targeted_feedback(command, rule):
    result = run(command)
    assert result.outcome is Outcome.INCORRECT
    assert result.matched_rule == rule
    mistake = next(f for f in result.feedback if f.kind is FeedbackKind.MISTAKE)
    assert mistake.code == [command]


@pytest.mark.parametrize(
    ("command", "fragment"),
    [
        ("copy a.txt b.txt", "`copy`"),
        ("cp -z a.txt b.txt", "`-z`"),
        ("cp a.txt", "2 ορίσματα"),
        ("cp a.txt c.txt", "όρισμα"),
        ("cp -s a.txt b.txt", "επιλογές"),
        ("cp a.txt -t", "τιμή"),
    ],
)
def test_unmatched_answers_get_a_specific_diagnosis(command, fragment):
    result = run(command)
    assert result.outcome is Outcome.INCORRECT
    mistake = next(f for f in result.feedback if f.kind is FeedbackKind.MISTAKE)
    assert fragment in mistake.text


@pytest.mark.parametrize(
    ("command", "rule"),
    [
        ("", "syntax_error"),
        ("cp 'a.txt b.txt", "syntax_error"),
        ("cp $(ls) b.txt", "unsupported:expansion"),
        ("cp a.txt b.txt && ls", "disallowed:sequence"),
        ("cp a.txt b.txt; rm a.txt", "disallowed:sequence"),
        ("cat a.txt | cp b.txt", "disallowed:pipe"),
        ("cp a.txt b.txt > log", "disallowed:redirect"),
    ],
)
def test_invalid_or_disallowed_input_is_not_graded_as_wrong(command, rule):
    result = run(command)
    assert result.outcome is Outcome.INVALID
    assert result.matched_rule == rule
    assert result.score == 0


def test_allowed_features_are_evaluated():
    ex = command_exercise(
        accepted=["ls | sort"],
        allow=["pipe"],
        test_cases={"accept": ["ls | sort"], "reject": ["ls"]},
    )
    assert run("ls|sort", ex).outcome is Outcome.CORRECT
    assert run("sort | ls", ex).outcome is Outcome.INCORRECT


def test_feedback_is_enriched_from_the_command_reference():
    result = run("cp a.txt b.txt")
    assert {
        FeedbackKind.SYNTAX,
        FeedbackKind.BREAKDOWN,
        FeedbackKind.RELATED,
        FeedbackKind.SOURCE,
    } <= set(kinds(result))


def test_oversized_input_is_invalid():
    assert run("cp " + "a" * 2000).outcome is Outcome.INVALID


def test_diagnosis_compares_with_accepted_answer_using_same_command():
    ex = command_exercise(
        accepted=["cp a.txt b.txt", "mv -i a.txt b.txt"],
        test_cases={"accept": ["cp a.txt b.txt"], "reject": ["mv a.txt c.txt"]},
    )
    result = run("mv -i a.txt c.txt", ex)
    mistake = next(f for f in result.feedback if f.kind is FeedbackKind.MISTAKE)
    # `mv` is a valid command here (second accepted answer): point at the argument instead.
    assert "άλλη εντολή" not in mistake.text
    assert "όρισμα" in mistake.text


def test_obsolete_shorthand_is_accepted_with_a_note():
    head = cp_command(
        id="head",
        name="head",
        numeric_shorthand="-n",
        options=[{"flags": ["-n", "--lines"], "summary": "lines", "value": "required"}],
        related=[],
    )
    ctx = EvalContext(commands={"head": head})
    ex = command_exercise(
        accepted=["head -n 3 data.csv"],
        test_cases={"accept": ["head -3 data.csv"], "reject": ["head data.csv"]},
    )
    short = evaluate(ex, {"command": "head -3 data.csv"}, ctx)
    assert short.outcome is Outcome.CORRECT
    note = next(f for f in short.feedback if f.kind is FeedbackKind.NOTE)
    assert "`-3`" in note.text and "`-n 3`" in note.text
    standard = evaluate(ex, {"command": "head -n 3 data.csv"}, ctx)
    assert FeedbackKind.NOTE not in kinds(standard)
