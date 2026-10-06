"""Exercise definitions: common metadata plus a type-specific `spec`.

Each type is a member of a discriminated union keyed on `type`, so a YAML file is
validated against exactly one shape and evaluators receive fully typed data.
"""

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field, model_validator

from app.content.schemas.common import (
    Citation,
    CognitiveLevel,
    ContentModel,
    Level,
    NonEmptyStr,
    Slug,
)

# ---------------------------------------------------------------- shared pieces


class SkillRef(ContentModel):
    id: Slug
    weight: float = Field(default=1.0, gt=0, le=3)


class Existence(StrEnum):
    EXISTS = "exists"
    NONEXISTENT = "nonexistent"
    NOT_INSTALLED = "not_installed"  # real tool, absent from the target platform by default
    PLATFORM_SPECIFIC = "platform_specific"  # exists, but on another platform (e.g. Windows)


class DistractorIssue(StrEnum):
    WRONG_SEMANTICS = "wrong_semantics"
    WRONG_SYNTAX = "wrong_syntax"
    WRONG_FLAG = "wrong_flag"
    WRONG_ORDER = "wrong_order"
    DANGEROUS = "dangerous"


class Distractor(ContentModel):
    """Why a wrong option is plausible — required metadata for invalid commands."""

    existence: Existence
    issue: DistractorIssue | None = None
    command: str | None = None
    note: str | None = None

    @model_validator(mode="after")
    def _explain_non_existing(self) -> "Distractor":
        if self.existence is not Existence.EXISTS and not self.note:
            raise ValueError(f"a '{self.existence}' distractor must explain itself in `note`")
        return self


class Option(ContentModel):
    id: Slug
    text: NonEmptyStr
    correct: bool = False
    why: str | None = None
    distractor: Distractor | None = None

    @model_validator(mode="after")
    def _wrong_needs_why(self) -> "Option":
        if not self.correct and not self.why:
            raise ValueError(f"wrong option {self.id!r} must have a `why`")
        return self


class ChoiceSpec(ContentModel):
    options: list[Option] = Field(min_length=2, max_length=6)
    multi_select: bool = False

    @model_validator(mode="after")
    def _check_correct_count(self) -> "ChoiceSpec":
        ids = [o.id for o in self.options]
        if len(ids) != len(set(ids)):
            raise ValueError("option ids must be unique")
        correct = sum(o.correct for o in self.options)
        if correct == 0:
            raise ValueError("at least one option must be correct")
        if not self.multi_select and correct != 1:
            raise ValueError("single-select questions need exactly one correct option")
        return self


class KnownMistake(ContentModel):
    id: Slug
    match: NonEmptyStr
    feedback: NonEmptyStr


class ShellFeature(StrEnum):
    PIPE = "pipe"
    REDIRECT = "redirect"
    SEQUENCE = "sequence"  # ; && ||


class Normalization(ContentModel):
    strip_dot_slash: bool = True  # ./old.txt == old.txt


class CommandTestCases(ContentModel):
    accept: list[NonEmptyStr] = Field(min_length=1)
    reject: list[NonEmptyStr] = Field(min_length=1)


# ---------------------------------------------------------------- per-type specs


class _ExerciseBase(ContentModel):
    id: Slug
    level: Level
    cognitive_level: CognitiveLevel
    skills: list[SkillRef] = Field(min_length=1)
    commands: list[Slug] = []
    prompt: NonEmptyStr
    hints: list[NonEmptyStr] = []
    explanation: NonEmptyStr
    reference: Slug | None = None  # command whose reference enriches the feedback
    citations: list[Citation] = []


class MultipleChoiceExercise(_ExerciseBase):
    type: Literal["multiple_choice"]
    spec: ChoiceSpec


class CommandSelectionExercise(_ExerciseBase):
    type: Literal["command_selection"]
    spec: ChoiceSpec


BLANK = "____"


class Blank(ContentModel):
    accepted: list[NonEmptyStr] = Field(min_length=1)
    known_mistakes: list[KnownMistake] = []
    # Commands and flags are case-sensitive; concept words (e.g. "SaaS") usually are not.
    case_sensitive: bool = True


class FillInSpec(ContentModel):
    template: NonEmptyStr
    blanks: list[Blank] = Field(min_length=1)

    @model_validator(mode="after")
    def _blank_count(self) -> "FillInSpec":
        if self.template.count(BLANK) != len(self.blanks):
            raise ValueError(
                f"template has {self.template.count(BLANK)} blanks, spec defines {len(self.blanks)}"
            )
        return self


class FillInCommandExercise(_ExerciseBase):
    type: Literal["fill_in_command"]
    spec: FillInSpec


class CommandWritingSpec(ContentModel):
    accepted: list[NonEmptyStr] = Field(min_length=1)
    known_mistakes: list[KnownMistake] = []
    allow: list[ShellFeature] = []
    normalization: Normalization = Normalization()
    # Per command name: flags that may be added or omitted without changing correctness
    # for this task (e.g. `cp -i`/`cp -v`). Avoids listing every combination in `accepted`.
    optional_flags: dict[str, list[str]] = {}
    test_cases: CommandTestCases


class CommandWritingExercise(_ExerciseBase):
    type: Literal["command_writing"]
    spec: CommandWritingSpec


class Step(ContentModel):
    id: Slug
    text: NonEmptyStr


class OrderingSpec(ContentModel):
    steps: list[Step] = Field(min_length=2, max_length=10)  # authored in the correct order

    @model_validator(mode="after")
    def _unique(self) -> "OrderingSpec":
        if len({s.id for s in self.steps}) != len(self.steps):
            raise ValueError("step ids must be unique")
        return self


class OrderingExercise(_ExerciseBase):
    type: Literal["ordering"]
    spec: OrderingSpec


class OutputAnalysisSpec(ChoiceSpec):
    command: NonEmptyStr
    output: NonEmptyStr
    captured_on: NonEmptyStr  # e.g. "debian-13.7"; outputs must come from the pinned image


class OutputAnalysisExercise(_ExerciseBase):
    type: Literal["output_analysis"]
    spec: OutputAnalysisSpec


Exercise = Annotated[
    MultipleChoiceExercise
    | CommandSelectionExercise
    | FillInCommandExercise
    | CommandWritingExercise
    | OrderingExercise
    | OutputAnalysisExercise,
    Field(discriminator="type"),
]

ExerciseType = Literal[
    "multiple_choice",
    "command_selection",
    "fill_in_command",
    "command_writing",
    "ordering",
    "output_analysis",
]
