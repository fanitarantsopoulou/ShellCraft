import pytest
from pydantic import ValidationError

from tests.factories import choice_spec, cp_command, exercise


def test_wrong_option_requires_why():
    spec = choice_spec()
    spec["options"][1].pop("why")
    with pytest.raises(ValidationError, match="must have a `why`"):
        exercise("multiple_choice", spec)


def test_non_existing_distractor_requires_note():
    spec = choice_spec()
    spec["options"][2]["distractor"] = {"existence": "nonexistent"}
    with pytest.raises(ValidationError, match="explain itself"):
        exercise("multiple_choice", spec)


def test_single_select_needs_exactly_one_correct():
    spec = choice_spec()
    spec["options"][1]["correct"] = True
    with pytest.raises(ValidationError, match="exactly one correct"):
        exercise("multiple_choice", spec)


def test_option_ids_unique():
    spec = choice_spec()
    spec["options"][1]["id"] = "a"
    with pytest.raises(ValidationError, match="unique"):
        exercise("multiple_choice", spec)


def test_fill_in_blank_count_must_match_template():
    with pytest.raises(ValidationError, match="blanks"):
        exercise("fill_in_command", {"template": "____ a ____", "blanks": [{"accepted": ["cp"]}]})


def test_unknown_keys_are_rejected():
    with pytest.raises(ValidationError, match="Extra inputs"):
        exercise(
            "ordering",
            {"steps": [{"id": "a", "text": "A"}, {"id": "b", "text": "B"}]},
            difficulty="easy",
        )


def test_unknown_exercise_type_is_rejected():
    with pytest.raises(ValidationError):
        exercise("essay", {})


def test_duplicate_flags_rejected():
    with pytest.raises(ValidationError, match="declared twice"):
        cp_command(
            options=[{"flags": ["-r"], "summary": "x"}, {"flags": ["-r", "-R"], "summary": "y"}]
        )


def test_flag_syntax_validated():
    with pytest.raises(ValidationError):
        cp_command(options=[{"flags": ["r"], "summary": "x"}])
