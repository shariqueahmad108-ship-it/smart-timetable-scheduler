"""Timetable generation endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from api.schemas import (
    Algorithm,
    FitnessOut,
    GenerateRequest,
    GenerateResponse,
    ScheduledClassOut,
    SolverStatsOut,
    ViolationOut,
)
from scheduler.backtracking import solve as solve_backtracking
from scheduler.constraints import validate_timetable
from scheduler.fitness import evaluate
from scheduler.genetic import GAConfig, solve as solve_genetic
from scheduler.graph import build_conflict_graph
from scheduler.parser import parse_input

router = APIRouter()


def _request_to_raw(req: GenerateRequest) -> dict:
    """Convert Pydantic request to the raw dict format the parser expects."""
    constraints = {
        "max_classes_per_day_per_teacher": req.constraints.max_classes_per_day_per_teacher,
        "max_classes_per_day_per_group": req.constraints.max_classes_per_day_per_group,
        "lunch_break_after_period": req.constraints.lunch_break_after_period,
        "teacher_preferences": {},
    }
    for tid, pref in req.constraints.teacher_preferences.items():
        p: dict = {}
        if pref.no_classes_before:
            p["no_classes_before"] = pref.no_classes_before
        if pref.preferred_days:
            p["preferred_days"] = pref.preferred_days
        if p:
            constraints["teacher_preferences"][tid] = p

    return {
        "working_days": req.working_days,
        "periods_per_day": req.periods_per_day,
        "teachers": [t.model_dump() for t in req.teachers],
        "rooms": [r.model_dump() for r in req.rooms],
        "subjects": [s.model_dump() for s in req.subjects],
        "student_groups": [g.model_dump() for g in req.student_groups],
        "constraints": constraints,
    }


def _build_stats(stats, algorithm: str, total_lectures: int) -> SolverStatsOut:
    """Build stats output from solver stats object."""
    out = SolverStatsOut(
        nodes_explored=stats.nodes_explored,
        backtracks=stats.backtracks,
        time_seconds=stats.time_seconds,
        solution_found=stats.solution_found,
        total_lectures=total_lectures,
        algorithm=algorithm,
    )
    if hasattr(stats, "generations_run"):
        out.generations_run = stats.generations_run
    if hasattr(stats, "best_generation"):
        out.best_generation = stats.best_generation
    return out


@router.post("/generate", response_model=GenerateResponse)
def generate_timetable(req: GenerateRequest) -> GenerateResponse:
    """Generate an optimized, clash-free timetable."""
    try:
        raw = _request_to_raw(req)
        data = parse_input(raw)
        graph, lectures = build_conflict_graph(data)

        # Choose algorithm
        if req.algorithm == Algorithm.GENETIC:
            config = GAConfig(
                population_size=req.ga_population,
                max_generations=req.ga_generations,
            )
            timetable, stats = solve_genetic(
                data, graph, lectures, timeout=req.timeout, config=config
            )
            algo_name = "genetic"
        else:
            timetable, stats = solve_backtracking(
                data, graph, lectures, timeout=req.timeout
            )
            algo_name = "backtracking"

        if timetable is None:
            return GenerateResponse(
                success=False,
                error="No valid timetable found. Try adding more rooms, reducing constraints, or increasing timeout.",
                stats=_build_stats(stats, algo_name, len(lectures)),
            )

        violations = validate_timetable(timetable, data)
        fb = evaluate(timetable, data)

        schedule_out = []
        for sc in timetable.assignments.values():
            subject = data.subjects[sc.lecture.subject_id]
            teacher = data.teachers[sc.lecture.teacher_id]
            group = data.student_groups[sc.lecture.group_id]
            room = data.rooms[sc.room_id]
            schedule_out.append(
                ScheduledClassOut(
                    subject_id=sc.lecture.subject_id,
                    subject_code=subject.code,
                    subject_name=subject.name,
                    teacher_id=sc.lecture.teacher_id,
                    teacher_name=teacher.name,
                    group_id=sc.lecture.group_id,
                    group_name=group.name,
                    room_id=sc.room_id,
                    room_name=room.name,
                    day=sc.time_slot.day,
                    period=sc.time_slot.period,
                    is_lab=sc.lecture.requires_lab,
                )
            )

        violations_out = [
            ViolationOut(
                constraint_type=v.constraint_type,
                description=v.description,
                penalty=v.penalty,
            )
            for v in violations
        ]

        fitness_out = FitnessOut(
            total=fb.total,
            hard_penalty=fb.hard_penalty,
            soft_penalty=fb.soft_penalty,
            bonus=fb.bonus,
            teacher_clashes=fb.teacher_clashes,
            room_clashes=fb.room_clashes,
            group_clashes=fb.group_clashes,
            student_gaps=fb.student_gaps,
        )

        return GenerateResponse(
            success=True,
            schedule=schedule_out,
            violations=violations_out,
            stats=_build_stats(stats, algo_name, len(schedule_out)),
            fitness=fitness_out,
        )

    except Exception as e:
        return GenerateResponse(success=False, error=str(e))
