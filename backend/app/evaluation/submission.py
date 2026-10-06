"""What a learner sends for each exercise type."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

MAX_COMMAND_LENGTH = 1000

ShortText = Annotated[str, StringConstraints(max_length=200)]


class _Submission(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ChoiceSubmission(_Submission):
    selected: list[ShortText] = Field(min_length=1, max_length=10)


class FillInSubmission(_Submission):
    blanks: list[ShortText] = Field(min_length=1, max_length=10)


class CommandSubmission(_Submission):
    command: Annotated[str, StringConstraints(max_length=MAX_COMMAND_LENGTH)]


class OrderingSubmission(_Submission):
    order: list[ShortText] = Field(min_length=1, max_length=20)


Submission = ChoiceSubmission | FillInSubmission | CommandSubmission | OrderingSubmission
