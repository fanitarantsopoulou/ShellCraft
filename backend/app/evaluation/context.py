from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from functools import cached_property

from app.content.schemas import Command


@dataclass(frozen=True)
class EvalContext:
    """Read-only data evaluators may consult. No database, no I/O."""

    commands: Mapping[str, Command] = field(default_factory=dict)

    @cached_property
    def _by_words(self) -> dict[tuple[str, ...], Command]:
        index: dict[tuple[str, ...], Command] = {}
        for command in self.commands.values():
            for spelling in (command.name, *command.aliases):
                index[tuple(spelling.split())] = command
        return index

    def resolve(self, argv: Sequence[str]) -> tuple[Command | None, int]:
        """Longest command name (or alias) that prefixes argv, and how many words it used.

        `docker run -d nginx` resolves to the `docker container run` reference using 2 words.
        """
        for n in range(min(len(argv), 4), 0, -1):
            if (command := self._by_words.get(tuple(argv[:n]))) is not None:
                return command, n
        return None, 0

    def command_by_name(self, name: str) -> Command | None:
        return self.resolve(name.split())[0]
