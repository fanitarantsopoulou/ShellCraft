"""Cross-reference and quality checks over a loaded ContentBundle.

Schema validation (loader) checks each file in isolation; lint checks the bundle as a whole:
dangling references, cycles, citation sources, staleness.
"""

from collections import Counter
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import date, timedelta
from enum import StrEnum
from urllib.parse import urlparse

from app.content.loader import ContentBundle
from app.content.schemas import Citation

MAX_CITATION_AGE = timedelta(days=365)


class Severity(StrEnum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class Issue:
    severity: Severity
    location: str
    message: str

    def __str__(self) -> str:
        return f"[{self.severity}] {self.location}: {self.message}"


def find_cycle(graph: Mapping[str, Iterable[str]]) -> list[str] | None:
    """Return one cycle as a list of nodes (first == last), or None if the graph is a DAG."""
    WHITE, GREY, BLACK = 0, 1, 2
    color = dict.fromkeys(graph, WHITE)
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        color[node] = GREY
        stack.append(node)
        for nxt in graph.get(node, ()):
            if color.get(nxt, BLACK) == GREY:
                return [*stack[stack.index(nxt) :], nxt]
            if color.get(nxt) == WHITE and (cycle := visit(nxt)):
                return cycle
        stack.pop()
        color[node] = BLACK
        return None

    for node in graph:
        if color[node] == WHITE and (cycle := visit(node)):
            return cycle
    return None


class _Linter:
    def __init__(self, bundle: ContentBundle, today: date) -> None:
        self.b = bundle
        self.today = today
        self.issues: list[Issue] = []

    def where(self, kind: str, id_: str) -> str:
        return self.b.origins.get((kind, id_), f"{kind}:{id_}")

    def error(self, loc: str, msg: str) -> None:
        self.issues.append(Issue(Severity.ERROR, loc, msg))

    def warn(self, loc: str, msg: str) -> None:
        self.issues.append(Issue(Severity.WARNING, loc, msg))

    def refs(self, loc: str, what: str, ids: Iterable[str], known: Mapping[str, object]) -> None:
        for ref in ids:
            if ref not in known:
                self.error(loc, f"unknown {what} {ref!r}")

    def citations(self, loc: str, citations: Iterable[Citation]) -> None:
        for c in citations:
            source = self.b.sources.get(c.source)
            if source is None:
                self.error(loc, f"citation uses unregistered source {c.source!r}")
                continue
            host = urlparse(str(c.url)).hostname or ""
            if not any(host == d or host.endswith("." + d) for d in source.allowed_domains):
                self.error(
                    loc, f"citation URL host {host!r} is not allowed for source {c.source!r}"
                )
            if c.last_verified > self.today:
                self.error(loc, f"last_verified {c.last_verified} is in the future")
            elif self.today - c.last_verified > MAX_CITATION_AGE:
                self.warn(loc, f"citation for {c.url} last verified {c.last_verified}; re-verify")

    def run(self) -> list[Issue]:
        b = self.b
        skills = {s.id: s for t in b.tracks.values() for s in t.skills}
        skill_counts = Counter(s.id for t in b.tracks.values() for s in t.skills)
        for skill_id, n in skill_counts.items():
            if n > 1:
                self.error(f"skill:{skill_id}", f"skill declared {n} times")

        for track in b.tracks.values():
            loc = self.where("track", track.id)
            for skill in track.skills:
                self.refs(loc, f"prerequisite skill of {skill.id!r}", skill.requires, skills)
        if cycle := find_cycle({s.id: s.requires for s in skills.values()}):
            self.error("skills", "prerequisite cycle: " + " -> ".join(cycle))

        lesson_owner: dict[str, list[str]] = {}
        for module in b.modules.values():
            loc = self.where("module", module.id)
            self.refs(loc, "track", [module.track], b.tracks)
            self.refs(loc, "prerequisite module", module.prerequisites, b.modules)
            self.refs(loc, "lesson", module.lessons, b.lessons)
            for lesson_id in module.lessons:
                lesson_owner.setdefault(lesson_id, []).append(module.id)
        if cycle := find_cycle({m.id: m.prerequisites for m in b.modules.values()}):
            self.error("modules", "prerequisite cycle: " + " -> ".join(cycle))

        for lesson in b.lessons.values():
            loc = self.where("lesson", lesson.id)
            owners = lesson_owner.get(lesson.id, [])
            if not owners:
                self.warn(loc, "lesson is not listed in any module")
            elif len(owners) > 1:
                self.error(loc, f"lesson belongs to several modules: {owners}")
            self.refs(loc, "skill", lesson.meta.skills, skills)
            self.refs(loc, "command", lesson.meta.commands, b.commands)
            self.citations(loc, lesson.meta.citations)

        orders: dict[tuple[str, int], str] = {}
        for quiz in b.quizzes.values():
            loc = self.where("quiz", quiz.id)
            self.refs(loc, "track", [quiz.track], b.tracks)
            self.refs(loc, "skill", quiz.skills, skills)
            self.refs(loc, "related lesson", quiz.related_lessons, b.lessons)
            if (other := orders.get((quiz.track, quiz.order))) is not None:
                self.error(loc, f"quiz order {quiz.order} already used by {other!r}")
            orders[(quiz.track, quiz.order)] = quiz.id

        for ex in b.exercises.values():
            loc = self.where("exercise", ex.id)
            self.refs(loc, f"skill (in {ex.id})", [s.id for s in ex.skills], skills)
            self.refs(loc, f"command (in {ex.id})", ex.commands, b.commands)
            if ex.reference:
                self.refs(loc, f"reference command (in {ex.id})", [ex.reference], b.commands)
            self.citations(loc, ex.citations)

        for cmd in b.commands.values():
            loc = self.where("command", cmd.id)
            self.refs(loc, "related command", [r.id for r in cmd.related], b.commands)
            self.citations(loc, cmd.citations)

        for path in b.paths.values():
            self.refs(self.where("path", path.id), "module", path.modules, b.modules)

        return self.issues


# Extra checks contributed by other packages (e.g. evaluation runs exercise test cases).
ExtraCheck = Callable[[ContentBundle], list[Issue]]


def lint(
    bundle: ContentBundle, *, today: date | None = None, extra: Iterable[ExtraCheck] = ()
) -> list[Issue]:
    issues = _Linter(bundle, today or date.today()).run()
    for check in extra:
        issues.extend(check(bundle))
    return issues
