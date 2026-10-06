"""Load and validate the content tree into an in-memory ContentBundle.

Pure: reads files, never touches the database. Collects every error instead of stopping
at the first one so authors can fix a batch at a time.
"""

from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from pydantic import TypeAdapter, ValidationError

from app.content.schemas import (
    Achievement,
    Command,
    Exercise,
    LearningPath,
    Lesson,
    LessonMeta,
    Module,
    Quiz,
    Source,
    Track,
)


@dataclass(frozen=True)
class LoadError:
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


@dataclass
class ContentBundle:
    sources: dict[str, Source] = field(default_factory=dict)
    tracks: dict[str, Track] = field(default_factory=dict)
    modules: dict[str, Module] = field(default_factory=dict)
    lessons: dict[str, Lesson] = field(default_factory=dict)
    exercises: dict[str, Exercise] = field(default_factory=dict)
    commands: dict[str, Command] = field(default_factory=dict)
    quizzes: dict[str, Quiz] = field(default_factory=dict)
    paths: dict[str, LearningPath] = field(default_factory=dict)
    achievements: dict[str, Achievement] = field(default_factory=dict)
    # Where each object came from, for error messages: (kind, id) -> relative path.
    origins: dict[tuple[str, str], str] = field(default_factory=dict)


class ContentLoadError(Exception):
    def __init__(self, errors: list[LoadError]) -> None:
        self.errors = errors
        super().__init__("\n".join(str(e) for e in errors))


def _format_validation(exc: ValidationError) -> str:
    parts = []
    for err in exc.errors():
        loc = ".".join(str(x) for x in err["loc"]) or "<root>"
        parts.append(f"{loc}: {err['msg']}")
    return "; ".join(parts)


def split_front_matter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        raise ValueError("lesson must start with YAML front matter ('---')")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("front matter is not closed with '---'")
    meta = yaml.safe_load(text[4:end]) or {}
    if not isinstance(meta, dict):
        raise ValueError("front matter must be a mapping")
    return meta, text[end + 5 :].strip()


class _Loader:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.bundle = ContentBundle()
        self.errors: list[LoadError] = []

    def rel(self, path: Path) -> str:
        return str(path.relative_to(self.root))

    def read_yaml(self, path: Path) -> Any:
        try:
            return yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            self.errors.append(LoadError(self.rel(path), f"cannot read YAML: {exc}"))
            return None

    def add(self, kind: str, store: dict[str, Any], obj: Any, path: Path) -> None:
        if obj.id in store:
            first = self.bundle.origins[(kind, obj.id)]
            self.errors.append(
                LoadError(self.rel(path), f"duplicate {kind} id {obj.id!r} (first in {first})")
            )
            return
        store[obj.id] = obj
        self.bundle.origins[(kind, obj.id)] = self.rel(path)

    def validate(self, model: Any, data: Any, path: Path) -> Any | None:
        try:
            if isinstance(model, TypeAdapter):
                return model.validate_python(data)
            return model.model_validate(data)
        except ValidationError as exc:
            self.errors.append(LoadError(self.rel(path), _format_validation(exc)))
            return None

    def load_list(self, path: Path, model: Any, kind: str, store: dict[str, Any]) -> None:
        if not path.exists():
            return
        data = self.read_yaml(path)
        if data is None:
            return
        if not isinstance(data, list):
            self.errors.append(LoadError(self.rel(path), "expected a YAML list"))
            return
        for item in data:
            obj = self.validate(model, item, path)
            if obj is not None:
                self.add(kind, store, obj, path)

    def load_each(
        self, paths: Iterable[Path], model: Any, kind: str, store: dict[str, Any]
    ) -> None:
        for path in sorted(paths):
            data = self.read_yaml(path)
            if data is None:
                continue
            obj = self.validate(model, data, path)
            if obj is not None:
                self.add(kind, store, obj, path)

    def load_lessons(self, paths: Iterable[Path]) -> None:
        for path in sorted(paths):
            try:
                meta, body = split_front_matter(path.read_text(encoding="utf-8"))
            except (OSError, ValueError, yaml.YAMLError) as exc:
                self.errors.append(LoadError(self.rel(path), str(exc)))
                continue
            lesson_meta = self.validate(LessonMeta, meta, path)
            if lesson_meta is None:
                continue
            lesson = self.validate(Lesson, {"meta": lesson_meta, "body_md": body}, path)
            if lesson is not None:
                self.add("lesson", self.bundle.lessons, lesson, path)

    def load_quizzes(self, paths: Iterable[Path]) -> None:
        for path in sorted(paths):
            data = self.read_yaml(path)
            if data is None:
                continue
            if not isinstance(data, dict) or not isinstance(data.get("questions"), list):
                message = "quiz must be a mapping with a `questions` list"
                self.errors.append(LoadError(self.rel(path), message))
                continue
            quiz_id = data.get("id", "")
            defaults = {
                "level": data.get("level"),
                "cognitive_level": "recognize",
                "skills": [{"id": s} for s in data.get("skills") or []],
            }
            questions = [
                {**defaults, **q, "id": f"{quiz_id}.{q.get('id', '')}"}
                if isinstance(q, dict)
                else q
                for q in data["questions"]
            ]
            data = {**data, "questions": questions}
            quiz = self.validate(Quiz, data, path)
            if quiz is None:
                continue
            self.add("quiz", self.bundle.quizzes, quiz, path)
            for question in quiz.questions:
                self.add("exercise", self.bundle.exercises, question, path)

    def run(self) -> ContentBundle:
        b, root = self.bundle, self.root
        self.load_list(root / "sources.yaml", Source, "source", b.sources)
        self.load_list(root / "achievements.yaml", Achievement, "achievement", b.achievements)
        self.load_each(root.glob("tracks/*/track.yaml"), Track, "track", b.tracks)
        self.load_each(root.glob("tracks/*/modules/*/module.yaml"), Module, "module", b.modules)
        self.load_lessons(root.glob("tracks/*/modules/*/lessons/*.md"))
        self.load_quizzes(root.glob("tracks/*/quizzes/*.yaml"))
        self.load_each(root.glob("commands/**/*.yaml"), Command, "command", b.commands)
        self.load_each(root.glob("paths/*.yaml"), LearningPath, "path", b.paths)
        if self.errors:
            raise ContentLoadError(self.errors)
        return b


def load_content(root: str | Path) -> ContentBundle:
    root = Path(root)
    if not root.is_dir():
        raise ContentLoadError([LoadError(str(root), "content directory does not exist")])
    return _Loader(root).run()
