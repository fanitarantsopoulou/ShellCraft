"""Content tooling.

    python -m cli.content validate [--dir PATH] [--strict]

Exit code 1 on any error (or any warning with --strict). Used locally and in CI.
"""

import argparse
import sys

from app.content.lint import Severity, lint
from app.content.loader import ContentLoadError, load_content
from app.core.config import get_settings
from app.evaluation.content_checks import check_command_exercises


def validate(content_dir: str, strict: bool) -> int:
    try:
        bundle = load_content(content_dir)
    except ContentLoadError as exc:
        for error in exc.errors:
            print(f"[error] {error}", file=sys.stderr)
        print(f"\n{len(exc.errors)} schema error(s).", file=sys.stderr)
        return 1

    issues = lint(bundle, extra=[check_command_exercises])
    for issue in issues:
        print(issue, file=sys.stderr)
    errors = sum(i.severity is Severity.ERROR for i in issues)
    warnings = len(issues) - errors
    print(
        f"{len(bundle.lessons)} lessons, {len(bundle.exercises)} exercises, "
        f"{len(bundle.commands)} commands — {errors} error(s), {warnings} warning(s)."
    )
    return 1 if errors or (strict and warnings) else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m cli.content")
    sub = parser.add_subparsers(dest="command", required=True)
    v = sub.add_parser("validate", help="schema-validate and lint the content tree")
    v.add_argument("--dir", default=None, help="content directory (default: APP_CONTENT_DIR)")
    v.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = parser.parse_args(argv)

    if args.command == "validate":
        return validate(args.dir or get_settings().content_dir, args.strict)
    return 2


if __name__ == "__main__":
    sys.exit(main())
