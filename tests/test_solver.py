"""Tests for the backtracking solver."""

from scheduler.backtracking import solve
from scheduler.constraints import count_hard_violations, validate_timetable
from scheduler.graph import build_conflict_graph
from scheduler.models import (
    Room,
    StudentGroup,
    Subject,
    Teacher,
    TimetableInput,
)
from scheduler.parser import load_input


def test_solve_trivial():
    """One teacher, one subject, one group, one room."""
    data = TimetableInput(periods_per_day=6)
    data.teachers = {"T1": Teacher(id="T1", name="Dr. A", subjects=["S1"])}
    data.rooms = {"R1": Room(id="R1", name="Room 1", capacity=60)}
    data.subjects = {
        "S1": Subject(id="S1", name="DSA", code="CS301", lectures_per_week=3),
    }
    data.student_groups = {
        "G1": StudentGroup(id="G1", name="CSE-3A", strength=50, subjects=["S1"]),
    }

    graph, lectures = build_conflict_graph(data)
    timetable, stats = solve(data, graph, lectures)

    assert timetable is not None
    assert stats.solution_found is True
    assert len(timetable.assignments) == 3

    violations = validate_timetable(timetable, data)
    assert count_hard_violations(violations) == 0


def test_solve_multiple_groups():
    """Two groups, shared teacher — no clashes."""
    data = TimetableInput(periods_per_day=6)
    data.teachers = {
        "T1": Teacher(id="T1", name="Dr. A", subjects=["S1"]),
        "T2": Teacher(id="T2", name="Dr. B", subjects=["S2"]),
    }
    data.rooms = {
        "R1": Room(id="R1", name="Room 1", capacity=60),
        "R2": Room(id="R2", name="Room 2", capacity=60),
    }
    data.subjects = {
        "S1": Subject(id="S1", name="DSA", code="CS301", lectures_per_week=2),
        "S2": Subject(id="S2", name="OS", code="CS302", lectures_per_week=2),
    }
    data.student_groups = {
        "G1": StudentGroup(id="G1", name="CSE-3A", strength=50, subjects=["S1", "S2"]),
        "G2": StudentGroup(id="G2", name="CSE-3B", strength=50, subjects=["S1", "S2"]),
    }

    graph, lectures = build_conflict_graph(data)
    timetable, stats = solve(data, graph, lectures)

    assert timetable is not None
    assert stats.solution_found is True
    # 2 groups × 2 subjects × 2 lectures = 8
    assert len(timetable.assignments) == 8

    violations = validate_timetable(timetable, data)
    assert count_hard_violations(violations) == 0


def test_solve_with_labs():
    """Subjects requiring labs should be assigned to lab rooms."""
    data = TimetableInput(periods_per_day=6)
    data.teachers = {"T1": Teacher(id="T1", name="Dr. A", subjects=["S1"])}
    data.rooms = {
        "R1": Room(id="R1", name="Room 1", capacity=60, room_type="lecture_hall"),
        "R2": Room(id="R2", name="Lab A", capacity=60, room_type="lab"),
    }
    data.subjects = {
        "S1": Subject(
            id="S1", name="DSA", code="CS301",
            lectures_per_week=3, requires_lab=True, lab_hours=1
        ),
    }
    data.student_groups = {
        "G1": StudentGroup(id="G1", name="CSE-3A", strength=50, subjects=["S1"]),
    }

    graph, lectures = build_conflict_graph(data)
    timetable, stats = solve(data, graph, lectures)

    assert timetable is not None
    assert stats.solution_found is True
    # 3 lectures - 1 lab = 2 regular + 1 lab
    assert len(timetable.assignments) == 3

    # Verify lab class is in lab room
    for sc in timetable.assignments.values():
        if sc.lecture.requires_lab:
            assert sc.room_id == "R2"

    violations = validate_timetable(timetable, data)
    assert count_hard_violations(violations) == 0


def test_solve_sample_input():
    """Full integration test with the sample JSON input."""
    data = load_input("examples/small_college.json")
    graph, lectures = build_conflict_graph(data)
    timetable, stats = solve(data, graph, lectures, timeout=30.0)

    assert timetable is not None
    assert stats.solution_found is True
    assert len(timetable.assignments) == len(lectures)

    violations = validate_timetable(timetable, data)
    assert count_hard_violations(violations) == 0


def test_no_solution_impossible():
    """Impossible case: more lectures than available slots."""
    data = TimetableInput(
        working_days=["Monday"],
        periods_per_day=1,
    )
    data.teachers = {"T1": Teacher(id="T1", name="Dr. A", subjects=["S1"])}
    data.rooms = {"R1": Room(id="R1", name="Room 1", capacity=60)}
    data.subjects = {
        "S1": Subject(id="S1", name="DSA", code="CS301", lectures_per_week=3),
    }
    data.student_groups = {
        "G1": StudentGroup(id="G1", name="CSE-3A", strength=50, subjects=["S1"]),
    }

    graph, lectures = build_conflict_graph(data)
    timetable, stats = solve(data, graph, lectures, timeout=5.0)

    # Only 1 slot available but 3 lectures needed — impossible
    assert timetable is None
    assert stats.solution_found is False
