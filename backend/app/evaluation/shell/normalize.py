"""Turn a parsed command line into a canonical form for comparison.

Equivalences applied are *only* those the command reference declares:
- a command alias maps to the command's name (`docker run` == `docker container run`);
- for `gnu_getopt`/`pflag` commands: bundled short flags are split (`-rf` == `-r -f`), every
  spelling of an option maps to its canonical flag (`-R` == `-r` == `--recursive`),
  option order does not matter, `--` ends options; options may follow operands unless the
  command declares `interspersed: false` (then everything after the first operand is an operand);
- optionally, a leading `./` on operands is dropped.
Operand order always matters. Commands without a declared grammar compare literally.
"""

from collections.abc import Mapping
from dataclasses import dataclass, replace

from app.content.schemas.command import Command, FlagGrammar, OptionValue
from app.evaluation.context import EvalContext
from app.evaluation.shell.parser import CommandLine, SimpleCommand


@dataclass(frozen=True)
class CanonicalCommand:
    name: str
    options: frozenset[tuple[str, str | None]]
    operands: tuple[str, ...]
    redirects: tuple[tuple[str, str], ...]
    unknown_options: tuple[str, ...] = ()
    missing_values: tuple[str, ...] = ()  # options that require a value but got none


@dataclass(frozen=True)
class CanonicalLine:
    commands: tuple[CanonicalCommand, ...]
    operators: tuple[str, ...]


def _norm_path(token: str, strip_dot_slash: bool) -> str:
    if strip_dot_slash and token.startswith("./") and len(token) > 2:
        return token[2:]
    return token


def _getopt(spec: Command, args: tuple[str, ...]) -> tuple[set, list[str], list[str], list[str]]:
    options: set[tuple[str, str | None]] = set()
    operands: list[str] = []
    unknown: list[str] = []
    missing: list[str] = []
    pflag = spec.flag_grammar is FlagGrammar.PFLAG
    i = 0
    while i < len(args):
        tok = args[i]
        if tok == "--" or (operands and not spec.interspersed):
            operands.extend(args[i + 1 if tok == "--" else i :])
            break
        if tok.startswith("--"):
            name, eq, value = tok.partition("=")
            opt = spec.option_for(name)
            if opt is None:
                unknown.append(name)
            elif opt.value is OptionValue.NONE:
                if eq:
                    unknown.append(tok)
                else:
                    options.add((opt.flags[0], None))
            elif eq:
                options.add((opt.flags[0], value))
            elif opt.value is OptionValue.REQUIRED:
                if i + 1 < len(args):
                    options.add((opt.flags[0], args[i + 1]))
                    i += 1
                else:
                    missing.append(name)
            else:
                options.add((opt.flags[0], None))
        elif spec.numeric_shorthand and tok[1:].isdigit() and tok.startswith("-"):
            opt = spec.option_for(spec.numeric_shorthand)
            options.add(((opt.flags[0] if opt else spec.numeric_shorthand), tok[1:]))
        elif tok.startswith("-") and tok != "-":
            chars = tok[1:]
            for j, ch in enumerate(chars):
                opt = spec.option_for(f"-{ch}")
                if opt is None:
                    unknown.append(f"-{ch}")
                    continue
                if opt.value is OptionValue.REQUIRED:
                    rest = chars[j + 1 :]
                    if pflag and rest.startswith("="):
                        rest = rest[1:]  # pflag accepts -p=8080:80
                    if rest:
                        options.add((opt.flags[0], rest))
                    elif i + 1 < len(args):
                        options.add((opt.flags[0], args[i + 1]))
                        i += 1
                    else:
                        missing.append(f"-{ch}")
                    break
                options.add((opt.flags[0], None))
        else:
            operands.append(tok)
        i += 1
    return options, operands, unknown, missing


def canonical_command(
    cmd: SimpleCommand, ctx: EvalContext, *, strip_dot_slash: bool
) -> CanonicalCommand:
    redirects = tuple((op, _norm_path(t, strip_dot_slash)) for op, t in cmd.redirects)
    spec, words = ctx.resolve(cmd.argv)
    name = spec.name if spec else cmd.argv[0]
    args = cmd.argv[words or 1 :]
    if spec is None or spec.flag_grammar is FlagGrammar.NONE:
        # No option grammar: compare tokens literally, but still treat `./x` as `x`.
        return CanonicalCommand(
            name, frozenset(), tuple(_norm_path(a, strip_dot_slash) for a in args), redirects
        )
    options, operands, unknown, missing = _getopt(spec, args)
    return CanonicalCommand(
        name=name,
        # Option values are often paths too (`-f ./app.yaml`).
        options=frozenset(
            (k, None if v is None else _norm_path(v, strip_dot_slash)) for k, v in options
        ),
        operands=tuple(_norm_path(o, strip_dot_slash) for o in operands),
        redirects=redirects,
        unknown_options=tuple(unknown),
        missing_values=tuple(missing),
    )


def _drop_optional(
    cmd: CanonicalCommand, ctx: EvalContext, optional: Mapping[str, list[str]]
) -> CanonicalCommand:
    spec = ctx.command_by_name(cmd.name)
    if spec is None:
        return cmd
    # Keys may use any spelling of the command (name or alias).
    flags = [f for key, fs in optional.items() if ctx.command_by_name(key) is spec for f in fs]
    if not flags:
        return cmd
    keys = {opt.flags[0] for f in flags if (opt := spec.option_for(f)) is not None}
    return replace(cmd, options=frozenset(o for o in cmd.options if o[0] not in keys))


def canonicalize(
    line: CommandLine,
    ctx: EvalContext,
    *,
    strip_dot_slash: bool = True,
    optional_flags: Mapping[str, list[str]] | None = None,
) -> CanonicalLine:
    commands = (canonical_command(c, ctx, strip_dot_slash=strip_dot_slash) for c in line.commands)
    if optional_flags:
        commands = (_drop_optional(c, ctx, optional_flags) for c in commands)
    return CanonicalLine(commands=tuple(commands), operators=line.operators)
