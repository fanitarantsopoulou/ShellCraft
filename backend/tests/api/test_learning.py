import json

import pytest

from tests.content.test_repository_content import content_dir


@pytest.fixture(autouse=True)
def _content(monkeypatch):
    from app.core.config import get_settings

    monkeypatch.setenv("APP_CONTENT_DIR", str(content_dir()))
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_modules_list_lessons(client):
    modules = client.get("/api/modules").json()
    assert modules and modules[0]["lessons"]


SECRET_KEYS = ("correct", "why", "accepted", "known_mistakes", "distractor", "explanation")


def test_quizzes_never_leak_answers(client):
    for quiz in client.get("/api/tracks/linux").json()["quizzes"]:
        body = client.get(f"/api/quizzes/{quiz['id']}").json()
        raw = json.dumps(body)
        for key in SECRET_KEYS:
            assert f'"{key}"' not in raw, (quiz["id"], key)


def test_lessons_are_theory_only(client):
    for module in client.get("/api/modules").json():
        for lesson in module["lessons"]:
            body = client.get(f"/api/lessons/{lesson['id']}").json()
            assert "exercises" not in body and body["body_html"]


def test_quiz_path_is_ordered_and_linked(client):
    quizzes = client.get("/api/tracks/linux").json()["quizzes"]
    assert [q["number"] for q in quizzes] == list(range(1, len(quizzes) + 1))
    assert len(quizzes) >= 6
    first = client.get(f"/api/quizzes/{quizzes[0]['id']}").json()
    assert first["next_quiz"]["id"] == quizzes[1]["id"]
    last = client.get(f"/api/quizzes/{quizzes[-1]['id']}").json()
    assert last["next_quiz"] is None


def test_ordering_steps_are_not_sent_in_answer_order(client):
    body = client.get("/api/quizzes/linux.q02").json()
    ordering = next(q for q in body["questions"] if q["type"] == "ordering")
    assert [s["id"] for s in ordering["steps"]] != ["backup", "edit", "verify", "restore"]


def test_answer_is_evaluated(client):
    url = "/api/exercises/linux.q02.cp-dir-write/answer"

    def outcome(payload):
        return client.post(url, json=payload).json()["outcome"]

    assert outcome({"command": "cp -r config config-backup"}) == "correct"
    assert outcome({"command": "mv config config-backup"}) == "incorrect"
    assert outcome({"selected": ["x"]}) == "invalid"


def test_unknown_ids_404(client):
    assert client.get("/api/lessons/nope").status_code == 404
    assert client.post("/api/exercises/nope/answer", json={}).status_code == 404
    assert client.get("/api/quizzes/nope").status_code == 404


def test_lesson_markdown_escapes_raw_html():
    from app.content.render import render_block

    assert "<script>" not in render_block("hi <script>alert(1)</script>")


def test_tracks(client):
    tracks = client.get("/api/tracks").json()
    assert [t["id"] for t in tracks][:4] == ["linux", "docker", "kubernetes", "cloud"]
    assert all(t["available"] and t["quiz_count"] >= 2 for t in tracks[:4])
    linux = client.get("/api/tracks/linux").json()
    assert linux["modules"] and all(m["id"].startswith("linux") for m in linux["modules"])
    docker = client.get("/api/tracks/docker").json()
    assert docker["modules"] == [] and docker["quizzes"]
    assert client.get("/api/tracks/nope").status_code == 404
