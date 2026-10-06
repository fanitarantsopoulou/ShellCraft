"""Shared building blocks for every content schema.

Content is authored as YAML/Markdown and validated with these models before it ever
reaches the database. Learner-facing strings are Greek; identifiers are ASCII slugs.
"""

from datetime import date
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, StringConstraints

Slug = Annotated[str, StringConstraints(pattern=r"^[a-z0-9]+(?:[.\-_][a-z0-9]+)*$", max_length=120)]
NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class ContentModel(BaseModel):
    """Strict base: unknown keys are authoring mistakes, not extensions."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=False)


class Level(StrEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class CognitiveLevel(StrEnum):
    """What the exercise asks the learner to do, from recall to real-world reasoning."""

    RECOGNIZE = "recognize"
    APPLY = "apply"
    COMBINE = "combine"
    TROUBLESHOOT = "troubleshoot"
    SCENARIO = "scenario"


class SourceKind(StrEnum):
    OFFICIAL_MANUAL = "official_manual"
    MAN_PAGE = "man_page"
    STANDARD = "standard"
    PROJECT_DOCS = "project_docs"


class Source(ContentModel):
    """A documentation source we accept as authoritative (registered in sources.yaml)."""

    id: Slug
    name: NonEmptyStr
    publisher: NonEmptyStr
    kind: SourceKind
    url: HttpUrl
    allowed_domains: list[NonEmptyStr] = Field(min_length=1)


class Citation(ContentModel):
    source: Slug
    url: HttpUrl
    section: str | None = None
    doc_version: NonEmptyStr
    last_verified: date
