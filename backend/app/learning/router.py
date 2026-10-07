from typing import Any

from fastapi import APIRouter, Body, HTTPException

from app.content.repository import get_bundle
from app.evaluation.context import EvalContext
from app.evaluation.registry import evaluate
from app.evaluation.result import EvaluationResult
from app.learning.public import (
    intro_view,
    lesson_view,
    module_summaries,
    quiz_summaries,
    quiz_view,
    track_summaries,
)

router = APIRouter(tags=["learning"])


@router.get("/tracks")
def list_tracks() -> list[dict[str, Any]]:
    return track_summaries(get_bundle())


@router.get("/tracks/{track_id}")
def get_track(track_id: str) -> dict[str, Any]:
    bundle = get_bundle()
    track = next((t for t in track_summaries(bundle) if t["id"] == track_id), None)
    if track is None:
        raise HTTPException(status_code=404, detail="Track not found")
    return {
        **track,
        "modules": module_summaries(bundle, track_id),
        "quizzes": quiz_summaries(bundle, track_id),
        "intro": intro_view(bundle, track_id),
    }


@router.get("/quizzes/{quiz_id}")
def get_quiz(quiz_id: str) -> dict[str, Any]:
    view = quiz_view(get_bundle(), quiz_id)
    if view is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return view


@router.get("/modules")
def list_modules() -> list[dict[str, Any]]:
    return module_summaries(get_bundle())


@router.get("/lessons/{lesson_id}")
def get_lesson(lesson_id: str) -> dict[str, Any]:
    view = lesson_view(get_bundle(), lesson_id)
    if view is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return view


@router.post("/exercises/{exercise_id}/answer")
def answer(exercise_id: str, submission: dict[str, Any] = Body(...)) -> EvaluationResult:  # noqa: B008
    bundle = get_bundle()
    exercise = bundle.exercises.get(exercise_id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return evaluate(exercise, submission, EvalContext(commands=bundle.commands))
