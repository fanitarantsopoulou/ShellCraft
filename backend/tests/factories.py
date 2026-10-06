"""Small builders for content objects used across tests (independent of the content/ tree)."""

from datetime import date
from typing import Any

from pydantic import TypeAdapter

from app.content.schemas import Command, Exercise

CITATION = {
    "source": "gnu-coreutils",
    "url": "https://www.gnu.org/software/coreutils/manual/html_node/cp-invocation.html",
    "doc_version": "9.7",
    "last_verified": date(2026, 10, 1),
}


def cp_command(**overrides: Any) -> Command:
    data = {
        "id": "cp",
        "name": "cp",
        "kind": "external_utility",
        "provider": "GNU coreutils",
        "platform": "debian-13",
        "category": "linux/file-management",
        "level": "beginner",
        "summary": "Copy files.",
        "synopsis": ["cp [OPTION]... SOURCE DEST"],
        "flag_grammar": "gnu_getopt",
        "options": [
            {"flags": ["-r", "-R", "--recursive"], "summary": "recursive"},
            {"flags": ["-i", "--interactive"], "summary": "prompt"},
            {"flags": ["-v", "--verbose"], "summary": "verbose"},
            {"flags": ["-s", "--symbolic-link"], "summary": "symlink"},
            {"flags": ["-t", "--target-directory"], "summary": "target", "value": "required"},
            {"flags": ["--backup"], "summary": "backup", "value": "optional"},
        ],
        "examples": [{"cmd": "cp a b", "explain": [{"token": "cp", "meaning": "command"}]}],
        "common_mistakes": [{"wrong": "mv a b", "why": "renames"}],
        "related": [{"id": "mv", "relation": "confused_with"}],
        "citations": [CITATION],
    }
    data.update(overrides)
    return Command.model_validate(data)


def mv_command() -> Command:
    return cp_command(
        id="mv",
        name="mv",
        options=[{"flags": ["-i", "--interactive"], "summary": "prompt"}],
        related=[{"id": "cp"}],
    )


_adapter: TypeAdapter[Exercise] = TypeAdapter(Exercise)

_BASE = {
    "level": "beginner",
    "cognitive_level": "apply",
    "skills": [{"id": "linux.files.copy"}],
    "prompt": "Do it.",
    "explanation": "Because.",
}


def exercise(type_: str, spec: dict[str, Any], **overrides: Any) -> Exercise:
    data = {
        "id": f"test.{type_.replace('_', '-')}",
        "type": type_,
        **_BASE,
        "spec": spec,
        **overrides,
    }
    return _adapter.validate_python(data)


def command_exercise(**spec: Any) -> Exercise:
    base = {
        "accepted": ["cp a.txt b.txt"],
        "test_cases": {"accept": ["cp a.txt b.txt"], "reject": ["mv a.txt b.txt"]},
    }
    return exercise("command_writing", {**base, **spec}, reference="cp")


def choice_spec(multi: bool = False) -> dict[str, Any]:
    return {
        "multi_select": multi,
        "options": [
            {"id": "a", "text": "cp a b", "correct": True},
            {"id": "b", "text": "mv a b", "why": "renames", "correct": multi},
            {
                "id": "c",
                "text": "copy a b",
                "why": "not linux",
                "distractor": {"existence": "platform_specific", "note": "Windows cmd"},
            },
        ],
    }
