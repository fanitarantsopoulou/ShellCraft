"""Command reference entries (one YAML file per command)."""

from enum import StrEnum
from typing import Annotated

from pydantic import Field, StringConstraints, model_validator

from app.content.schemas.common import Citation, ContentModel, Level, NonEmptyStr, Slug

Flag = Annotated[str, StringConstraints(pattern=r"^(-[A-Za-z0-9]|--[a-z0-9][a-z0-9-]*)$")]


class CommandKind(StrEnum):
    SHELL_BUILTIN = "shell_builtin"
    SHELL_KEYWORD = "shell_keyword"
    EXTERNAL_UTILITY = "external_utility"
    CLI_SUBCOMMAND = "cli_subcommand"


class FlagGrammar(StrEnum):
    """How the command parses options. `none` disables flag normalization."""

    GNU_GETOPT = "gnu_getopt"  # -rf == -r -f, options may follow operands, `--` ends options
    PFLAG = "pflag"  # Go CLIs (docker, kubectl): like getopt, plus `-p=VALUE`
    NONE = "none"  # compare tokens literally


class OptionValue(StrEnum):
    NONE = "none"
    REQUIRED = "required"
    OPTIONAL = "optional"  # only attachable as --long=VALUE


class CommandOption(ContentModel):
    flags: list[Flag] = Field(min_length=1)  # all spellings are equivalent; first is canonical
    summary: NonEmptyStr
    value: OptionValue = OptionValue.NONE
    value_name: str | None = None
    level: Level = Level.BEGINNER


class TokenExplanation(ContentModel):
    token: NonEmptyStr
    meaning: NonEmptyStr


class CommandExample(ContentModel):
    cmd: NonEmptyStr
    explain: list[TokenExplanation] = []
    output: str | None = None
    note: str | None = None


class CommonMistake(ContentModel):
    wrong: NonEmptyStr
    why: NonEmptyStr


class Relation(StrEnum):
    RELATED = "related"
    CONFUSED_WITH = "confused_with"
    SEE_ALSO = "see_also"


class RelatedCommand(ContentModel):
    id: Slug
    relation: Relation = Relation.RELATED


class Command(ContentModel):
    id: Slug
    name: NonEmptyStr  # may contain subcommands, e.g. "docker container run"
    aliases: list[NonEmptyStr] = []  # equivalent spellings, e.g. "docker run"
    kind: CommandKind
    provider: NonEmptyStr
    platform: NonEmptyStr
    category: NonEmptyStr
    level: Level
    summary: NonEmptyStr
    description: str = ""
    synopsis: list[NonEmptyStr] = Field(min_length=1)
    flag_grammar: FlagGrammar = FlagGrammar.NONE
    # False when parsing stops at the first operand (e.g. `docker run IMAGE CMD...`).
    interspersed: bool = True
    # Obsolete GNU form where `-NUM` means `<flag> NUM` (e.g. `head -5` == `head -n 5`).
    numeric_shorthand: Flag | None = None
    options: list[CommandOption] = []
    examples: list[CommandExample] = []
    common_mistakes: list[CommonMistake] = []
    when_not_to_use: list[NonEmptyStr] = []
    related: list[RelatedCommand] = []
    citations: list[Citation] = Field(min_length=1)

    @model_validator(mode="after")
    def _flags_unique(self) -> "Command":
        seen: set[str] = set()
        for option in self.options:
            for flag in option.flags:
                if flag in seen:
                    raise ValueError(f"flag {flag!r} declared twice in command {self.id!r}")
                seen.add(flag)
        return self

    def option_for(self, flag: str) -> CommandOption | None:
        for option in self.options:
            if flag in option.flags:
                return option
        return None
