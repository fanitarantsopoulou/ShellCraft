from datetime import date

from app.content.lint import Severity, find_cycle, lint
from app.content.loader import ContentBundle
from app.content.schemas import Source, Track
from tests.factories import cp_command


def test_find_cycle():
    assert find_cycle({"a": ["b"], "b": ["c"], "c": []}) is None
    assert find_cycle({"a": ["b"], "b": ["a"]}) == ["a", "b", "a"]
    assert find_cycle({"a": ["a"]}) == ["a", "a"]


def bundle(**kw) -> ContentBundle:
    b = ContentBundle()
    b.sources["gnu-coreutils"] = Source(
        id="gnu-coreutils",
        name="GNU",
        publisher="GNU",
        kind="official_manual",
        url="https://www.gnu.org/",
        allowed_domains=["gnu.org"],
    )
    for key, value in kw.items():
        getattr(b, key).update(value)
    return b


def messages(issues, severity=Severity.ERROR):
    return [i.message for i in issues if i.severity is severity]


TODAY = date(2026, 10, 6)


def test_clean_bundle_has_no_issues():
    assert lint(bundle(commands={"cp": cp_command(related=[])}), today=TODAY) == []


def test_dangling_related_command():
    errors = messages(lint(bundle(commands={"cp": cp_command()}), today=TODAY))
    assert errors == ["unknown related command 'mv'"]


def test_citation_domain_must_match_source():
    cmd = cp_command(
        related=[],
        citations=[
            {
                "source": "gnu-coreutils",
                "url": "https://medium.com/x",
                "doc_version": "1",
                "last_verified": TODAY,
            }
        ],
    )
    errors = messages(lint(bundle(commands={"cp": cmd}), today=TODAY))
    assert "not allowed" in errors[0]


def test_unregistered_source():
    cmd = cp_command(
        related=[],
        citations=[
            {
                "source": "some-blog",
                "url": "https://blog.example/x",
                "doc_version": "1",
                "last_verified": TODAY,
            }
        ],
    )
    assert "unregistered source" in messages(lint(bundle(commands={"cp": cmd}), today=TODAY))[0]


def test_stale_and_future_citations():
    stale = cp_command(
        related=[],
        citations=[
            {
                "source": "gnu-coreutils",
                "url": "https://www.gnu.org/x",
                "doc_version": "1",
                "last_verified": date(2024, 1, 1),
            }
        ],
    )
    assert messages(lint(bundle(commands={"cp": stale}), today=TODAY), Severity.WARNING)
    future = stale.model_copy(
        update={
            "citations": [stale.citations[0].model_copy(update={"last_verified": date(2027, 1, 1)})]
        }
    )
    assert "future" in messages(lint(bundle(commands={"cp": future}), today=TODAY))[0]


def test_skill_cycle_detected():
    track = Track(
        id="linux",
        title="Linux",
        biome="woods",
        order=1,
        skills=[
            {"id": "a", "title": "A", "requires": ["b"]},
            {"id": "b", "title": "B", "requires": ["a"]},
        ],
    )
    assert any("cycle" in m for m in messages(lint(bundle(tracks={"linux": track}), today=TODAY)))
