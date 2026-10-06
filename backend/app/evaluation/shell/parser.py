"""A deliberately small POSIX-shell command-line parser.

It understands quoting, simple commands, pipes, `;`/`&&`/`||` and `<`/`>`/`>>` redirects.
Anything else (expansions, subshells, background jobs, fd-numbered redirects) is rejected
as *unsupported* rather than guessed at: an evaluator that misreads shell syntax would
teach the wrong thing. Nothing is ever executed.
"""

import re
import shlex
from dataclasses import dataclass

CONTROL_OPERATORS = frozenset({"|", "&&", "||", ";"})
REDIRECT_OPERATORS = frozenset({">", ">>", "<"})


class ShellSyntaxError(ValueError):
    """The line is not valid shell (e.g. unclosed quote, dangling pipe)."""


class UnsupportedSyntax(ValueError):
    """Valid shell, but outside what the evaluator is willing to judge."""

    def __init__(self, feature: str, message: str) -> None:
        super().__init__(message)
        self.feature = feature


@dataclass(frozen=True)
class SimpleCommand:
    argv: tuple[str, ...]
    redirects: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class CommandLine:
    commands: tuple[SimpleCommand, ...]
    operators: tuple[str, ...] = ()  # operators[i] joins commands[i] and commands[i + 1]

    @property
    def uses_pipe(self) -> bool:
        return "|" in self.operators

    @property
    def uses_sequence(self) -> bool:
        return any(op != "|" for op in self.operators)

    @property
    def uses_redirect(self) -> bool:
        return any(c.redirects for c in self.commands)


_FD_REDIRECT = re.compile(r"\d+[<>]|[<>]&|&>")


def _scan_unquoted(line: str) -> None:
    """Reject constructs that only matter outside quotes (expansions, subshells, ...)."""
    quote: str | None = None
    unquoted: list[str] = []
    i = 0
    while i < len(line):
        ch = line[i]
        if quote == "'":
            if ch == "'":
                quote = None
        elif ch == "\\" and quote != "'":
            i += 2
            unquoted.append("  ")
            continue
        elif quote == '"':
            if ch == '"':
                quote = None
            elif ch in "$`":
                raise UnsupportedSyntax(
                    "expansion", "Οι επεκτάσεις (`$…`, `` `…` ``) δεν υποστηρίζονται εδώ."
                )
        elif ch in "'\"":
            quote = ch
        else:
            unquoted.append(ch)
            if ch in "$`":
                raise UnsupportedSyntax(
                    "expansion", "Οι επεκτάσεις (`$…`, `` `…` ``) δεν υποστηρίζονται εδώ."
                )
            if ch in "()":
                raise UnsupportedSyntax("subshell", "Τα subshells `( … )` δεν υποστηρίζονται εδώ.")
        i += 1
    flat = "".join(unquoted)
    if _FD_REDIRECT.search(flat):
        raise UnsupportedSyntax(
            "fd_redirect", "Οι ανακατευθύνσεις με αριθμό fd (π.χ. `2>`) δεν υποστηρίζονται εδώ."
        )
    if re.search(r"(?<!&)&(?!&)", flat):
        raise UnsupportedSyntax(
            "background", "Η εκτέλεση στο παρασκήνιο (`&`) δεν υποστηρίζεται εδώ."
        )


def tokenize(line: str) -> list[str]:
    lexer = shlex.shlex(line, posix=True, punctuation_chars=";&|<>")
    lexer.whitespace_split = True
    lexer.commenters = ""
    try:
        return list(lexer)
    except ValueError as exc:  # e.g. "No closing quotation"
        raise ShellSyntaxError("Μη έγκυρη σύνταξη: κάποιο εισαγωγικό δεν έκλεισε.") from exc


def parse(line: str) -> CommandLine:
    line = line.strip()
    if not line:
        raise ShellSyntaxError("Δεν γράφτηκε καμία εντολή.")
    if "\n" in line:
        raise UnsupportedSyntax("multiline", "Γράψε την εντολή σε μία γραμμή.")
    _scan_unquoted(line)

    commands: list[SimpleCommand] = []
    operators: list[str] = []
    argv: list[str] = []
    redirects: list[tuple[str, str]] = []
    tokens = tokenize(line)
    i = 0

    def close_command() -> None:
        if not argv:
            raise ShellSyntaxError("Λείπει εντολή πριν ή μετά από τελεστή (`|`, `;`, `&&`, `||`).")
        commands.append(SimpleCommand(tuple(argv), tuple(redirects)))
        argv.clear()
        redirects.clear()

    while i < len(tokens):
        tok = tokens[i]
        if tok in CONTROL_OPERATORS:
            close_command()
            operators.append(tok)
        elif tok in REDIRECT_OPERATORS:
            if i + 1 >= len(tokens) or tokens[i + 1] in CONTROL_OPERATORS | REDIRECT_OPERATORS:
                raise ShellSyntaxError(f"Λείπει το αρχείο μετά το `{tok}`.")
            redirects.append((tok, tokens[i + 1]))
            i += 1
        elif set(tok) <= set(";&|<>"):
            raise ShellSyntaxError(f"Μη έγκυρος τελεστής `{tok}`.")
        else:
            argv.append(tok)
        i += 1

    if operators and not argv and not redirects:
        raise ShellSyntaxError(f"Η εντολή τελειώνει με `{operators[-1]}`.")
    close_command()
    return CommandLine(tuple(commands), tuple(operators))
