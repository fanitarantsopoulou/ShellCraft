"""The real content/ tree must load, lint cleanly and pass every authored test case."""

from pathlib import Path

import pytest

from app.content.lint import lint
from app.content.loader import load_content
from app.core.config import get_settings
from app.evaluation.content_checks import check_command_exercises


def content_dir() -> Path:
    for candidate in (Path(get_settings().content_dir), Path(__file__).parents[3] / "content"):
        if (candidate / "sources.yaml").exists():
            return candidate
    pytest.skip("content directory not available")


def test_content_is_valid_and_lint_clean():
    bundle = load_content(content_dir())
    issues = lint(bundle, extra=[check_command_exercises])
    assert [str(i) for i in issues] == []
    assert bundle.lessons and bundle.exercises and bundle.commands
