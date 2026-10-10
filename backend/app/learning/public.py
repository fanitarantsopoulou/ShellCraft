"""Learner-facing views of content. Never include answers, explanations or distractor metadata."""

import random
from typing import Any

from app.content.loader import ContentBundle
from app.content.render import render_block, render_inline
from app.content.schemas import Exercise
from app.content.schemas.common import DIFFICULTY
from app.content.schemas.exercise import (
    BLANK,
    ChoiceSpec,
    CommandWritingExercise,
    FillInCommandExercise,
    OrderingExercise,
    OutputAnalysisExercise,
)


def public_exercise(ex: Exercise) -> dict[str, Any]:
    view: dict[str, Any] = {
        "id": ex.id,
        "type": ex.type,
        "level": ex.level,
        "difficulty": DIFFICULTY[ex.cognitive_level],
        "prompt_html": render_inline(ex.prompt.strip()),
        "hints": list(ex.hints),
    }
    spec = ex.spec
    if isinstance(spec, ChoiceSpec):
        view["options"] = [{"id": o.id, "text": o.text} for o in spec.options]
        view["multi_select"] = spec.multi_select
    if isinstance(ex, OutputAnalysisExercise):
        view["command"] = ex.spec.command
        view["output"] = ex.spec.output
    elif isinstance(ex, FillInCommandExercise):
        view["template_parts"] = ex.spec.template.split(BLANK)
    elif isinstance(ex, OrderingExercise):
        steps = [{"id": s.id, "text": s.text} for s in ex.spec.steps]
        while len(steps) > 1 and [s["id"] for s in steps] == [s.id for s in ex.spec.steps]:
            random.shuffle(steps)  # authored order is the answer; never send it as-is
        view["steps"] = steps
    elif isinstance(ex, CommandWritingExercise):
        view["placeholder"] = "$ "
    return view


def track_summaries(bundle: ContentBundle) -> list[dict[str, Any]]:
    tracks = sorted(bundle.tracks.values(), key=lambda t: t.order)
    result = []
    for t in tracks:
        modules = [m for m in bundle.modules.values() if m.track == t.id]
        result.append(
            {
                "id": t.id,
                "title": t.title,
                "biome": t.biome,
                "summary": t.summary,
                "module_count": len(modules),
                "lesson_count": sum(len(m.lessons) for m in modules),
                "quiz_count": sum(q.track == t.id for q in bundle.quizzes.values()),
                "available": bool(modules) or any(q.track == t.id for q in bundle.quizzes.values()),
            }
        )
    return result


def module_summaries(bundle: ContentBundle, track: str | None = None) -> list[dict[str, Any]]:
    modules = sorted(
        (m for m in bundle.modules.values() if track is None or m.track == track),
        key=lambda m: (m.track, m.order),
    )
    return [
        {
            "id": m.id,
            "track": bundle.tracks[m.track].title,
            "title": m.title,
            "summary": m.summary,
            "level": m.level,
            "lessons": [
                {
                    "id": lid,
                    "title": bundle.lessons[lid].meta.title,
                    "est_minutes": bundle.lessons[lid].meta.est_minutes,
                }
                for lid in m.lessons
            ],
        }
        for m in modules
    ]


def lesson_view(bundle: ContentBundle, lesson_id: str) -> dict[str, Any] | None:
    lesson = bundle.lessons.get(lesson_id)
    if lesson is None:
        return None
    meta = lesson.meta
    module = next((m for m in bundle.modules.values() if lesson_id in m.lessons), None)
    siblings = module.lessons if module else [lesson_id]
    index = siblings.index(lesson_id)
    return {
        "id": meta.id,
        "title": meta.title,
        "objective": meta.objective,
        "level": meta.level,
        "est_minutes": meta.est_minutes,
        "module": {"id": module.id, "title": module.title} if module else None,
        "body_html": render_block(lesson.body_md),
        "commands": meta.commands,
        "quizzes": [
            {"id": q.id, "title": q.title}
            for q in sorted(bundle.quizzes.values(), key=lambda q: q.order)
            if lesson_id in q.related_lessons
        ],
        "next_lesson": siblings[index + 1] if index + 1 < len(siblings) else None,
        "sources": [
            {"url": str(c.url), "label": c.section or c.doc_version} for c in meta.citations
        ],
    }


def quiz_summaries(bundle: ContentBundle, track: str) -> list[dict[str, Any]]:
    quizzes = sorted(
        (q for q in bundle.quizzes.values() if q.track == track), key=lambda q: q.order
    )
    return [
        {
            "id": q.id,
            "number": i,
            "title": q.title,
            "description": q.description,
            "level": q.level,
            "question_count": len(q.questions),
        }
        for i, q in enumerate(quizzes, 1)
    ]


def quiz_view(bundle: ContentBundle, quiz_id: str) -> dict[str, Any] | None:
    quiz = bundle.quizzes.get(quiz_id)
    if quiz is None:
        return None
    siblings = quiz_summaries(bundle, quiz.track)
    index = next(i for i, q in enumerate(siblings) if q["id"] == quiz_id)
    return {
        **siblings[index],
        "track": quiz.track,
        "questions": [public_exercise(q) for q in quiz.questions],
        "related_lessons": [
            {"id": lid, "title": bundle.lessons[lid].meta.title} for lid in quiz.related_lessons
        ],
        "next_quiz": siblings[index + 1] if index + 1 < len(siblings) else None,
    }


def intro_view(bundle: ContentBundle, track_id: str) -> dict[str, Any] | None:
    intro = bundle.intros.get(track_id)
    if intro is None:
        return None
    return {
        "title": intro.meta.title,
        "body_html": render_block(intro.body_md),
        "sources": [
            {"url": str(c.url), "label": c.section or c.doc_version} for c in intro.meta.citations
        ],
    }
