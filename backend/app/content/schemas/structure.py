"""Tracks, skills, modules, lessons, learning paths and achievements."""

from typing import Any

from pydantic import Field, model_validator

from app.content.schemas.common import Citation, ContentModel, Level, NonEmptyStr, Slug
from app.content.schemas.exercise import Exercise


class Skill(ContentModel):
    id: Slug
    title: NonEmptyStr
    description: str = ""
    requires: list[Slug] = []


class Track(ContentModel):
    id: Slug
    title: NonEmptyStr
    biome: Slug
    order: int
    summary: str = ""
    skills: list[Skill] = []


class MapPosition(ContentModel):
    x: int = Field(ge=0)
    y: int = Field(ge=0)


class Module(ContentModel):
    id: Slug
    track: Slug
    title: NonEmptyStr
    summary: NonEmptyStr
    order: int
    level: Level
    prerequisites: list[Slug] = []
    map: MapPosition
    lessons: list[Slug] = Field(min_length=1)


class LessonMeta(ContentModel):
    """YAML front matter of a lesson Markdown file."""

    id: Slug
    title: NonEmptyStr
    level: Level
    objective: NonEmptyStr
    est_minutes: int = Field(ge=1, le=20)
    skills: list[Slug] = Field(min_length=1)
    commands: list[Slug] = []
    citations: list[Citation] = Field(min_length=1)


class Lesson(ContentModel):
    meta: LessonMeta
    body_md: NonEmptyStr

    @property
    def id(self) -> str:
        return self.meta.id


class Quiz(ContentModel):
    """An ordered set of questions, independent of the theory lessons.

    Authored as one YAML file; questions inherit `level`/`skills` from the quiz unless they
    override them, and their ids are prefixed with the quiz id by the loader.
    """

    id: Slug
    track: Slug
    title: NonEmptyStr
    description: NonEmptyStr
    level: Level
    order: int
    skills: list[Slug] = Field(min_length=1)
    related_lessons: list[Slug] = []
    questions: list[Exercise] = Field(min_length=5)

    @model_validator(mode="after")
    def _unique_questions(self) -> "Quiz":
        ids = [q.id for q in self.questions]
        if len(ids) != len(set(ids)):
            raise ValueError("question ids must be unique within a quiz")
        return self


class TrackIntroMeta(ContentModel):
    """Front matter of content/tracks/<track>/intro.md."""

    track: Slug
    title: NonEmptyStr
    citations: list[Citation] = Field(min_length=1)


class TrackIntro(ContentModel):
    meta: TrackIntroMeta
    body_md: NonEmptyStr

    @property
    def id(self) -> str:
        return self.meta.track


class LearningPath(ContentModel):
    id: Slug
    title: NonEmptyStr
    description: NonEmptyStr
    order: int
    modules: list[Slug] = Field(min_length=1)


class Achievement(ContentModel):
    id: Slug
    title: NonEmptyStr
    description: NonEmptyStr
    icon: Slug
    rule: dict[str, Any]
