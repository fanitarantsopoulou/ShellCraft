import pytest

from app.content.schemas import Exercise
from app.evaluation.context import EvalContext
from app.evaluation.registry import evaluate, supported_types
from app.evaluation.result import FeedbackKind, Outcome
from tests.factories import choice_spec, exercise

CTX = EvalContext()


def test_every_exercise_type_has_an_evaluator():
    from typing import get_args

    union = get_args(Exercise)[0]
    schema_types = {get_args(m.model_fields["type"].annotation)[0] for m in get_args(union)}
    assert schema_types == supported_types()


class TestChoice:
    ex = exercise("multiple_choice", choice_spec())

    def test_correct(self):
        r = evaluate(self.ex, {"selected": ["a"]}, CTX)
        assert r.outcome is Outcome.CORRECT and r.score == 1

    def test_wrong_option_explains_itself_and_distractor(self):
        r = evaluate(self.ex, {"selected": ["c"]}, CTX)
        assert r.outcome is Outcome.INCORRECT
        option = next(f for f in r.feedback if f.kind is FeedbackKind.OPTION)
        assert "not linux" in option.text and "Windows cmd" in option.text
        assert option.code == ["copy a b"]

    @pytest.mark.parametrize("selected", [["zzz"], ["a", "b"]])
    def test_invalid_selection(self, selected):
        assert evaluate(self.ex, {"selected": selected}, CTX).outcome is Outcome.INVALID

    def test_malformed_submission(self):
        assert evaluate(self.ex, {"command": "cp"}, CTX).outcome is Outcome.INVALID
        assert evaluate(self.ex, {"selected": []}, CTX).outcome is Outcome.INVALID

    def test_multi_select_partial_credit(self):
        ex = exercise("multiple_choice", choice_spec(multi=True))
        assert evaluate(ex, {"selected": ["a", "b"]}, CTX).outcome is Outcome.CORRECT
        partial = evaluate(ex, {"selected": ["a"]}, CTX)
        assert partial.outcome is Outcome.PARTIAL and partial.score == 0.5
        # A wrong pick cancels a right one: guessing everything is not rewarded.
        assert evaluate(ex, {"selected": ["a", "c"]}, CTX).score == 0
        assert evaluate(ex, {"selected": ["a", "b", "c"]}, CTX).outcome is Outcome.PARTIAL


class TestFillIn:
    ex = exercise(
        "fill_in_command",
        {
            "template": "____ old.txt ____",
            "blanks": [
                {
                    "accepted": ["cp"],
                    "known_mistakes": [{"id": "mv", "match": "mv", "feedback": "renames"}],
                },
                {"accepted": ["new.txt", "./new.txt"]},
            ],
        },
    )

    def test_correct_with_whitespace(self):
        assert evaluate(self.ex, {"blanks": [" cp ", "./new.txt"]}, CTX).outcome is Outcome.CORRECT

    def test_partial_with_known_mistake(self):
        r = evaluate(self.ex, {"blanks": ["mv", "new.txt"]}, CTX)
        assert r.outcome is Outcome.PARTIAL and r.score == 0.5
        assert any(f.kind is FeedbackKind.MISTAKE and f.text == "renames" for f in r.feedback)
        assert next(f for f in r.feedback if f.kind is FeedbackKind.CORRECT_ANSWER).code == [
            "cp old.txt new.txt"
        ]

    def test_case_sensitive(self):
        assert evaluate(self.ex, {"blanks": ["CP", "new.txt"]}, CTX).outcome is Outcome.PARTIAL

    def test_case_insensitive_blank(self):
        blank = {"accepted": ["SaaS"], "case_sensitive": False}
        ex = exercise("fill_in_command", {"template": "Model: ____", "blanks": [blank]})
        assert evaluate(ex, {"blanks": ["saas"]}, CTX).outcome is Outcome.CORRECT
        assert evaluate(ex, {"blanks": ["PaaS"]}, CTX).outcome is Outcome.INCORRECT

    def test_wrong_blank_count(self):
        assert evaluate(self.ex, {"blanks": ["cp"]}, CTX).outcome is Outcome.INVALID


class TestOrdering:
    ex = exercise(
        "ordering",
        {"steps": [{"id": "a", "text": "A"}, {"id": "b", "text": "B"}, {"id": "c", "text": "C"}]},
    )

    def test_correct(self):
        assert evaluate(self.ex, {"order": ["a", "b", "c"]}, CTX).outcome is Outcome.CORRECT

    def test_partial_points_at_first_divergence(self):
        r = evaluate(self.ex, {"order": ["a", "c", "b"]}, CTX)
        assert r.outcome is Outcome.PARTIAL
        assert "2" in next(f for f in r.feedback if f.kind is FeedbackKind.MISTAKE).text

    def test_fully_wrong(self):
        assert evaluate(self.ex, {"order": ["c", "a", "b"]}, CTX).outcome is Outcome.INCORRECT

    @pytest.mark.parametrize("order", [["a", "b"], ["a", "a", "b"], ["a", "b", "x"]])
    def test_must_place_every_step_once(self, order):
        assert evaluate(self.ex, {"order": order}, CTX).outcome is Outcome.INVALID
