"""Tests for the genetic algorithm solver."""

from scheduler.constraints import count_hard_violations, validate_timetable
from scheduler.fitness import evaluate
from scheduler.genetic import GAConfig, solve
from scheduler.graph import build_conflict_graph
from scheduler.models import (
    Room,
    StudentGroup,
    Subject,
    Teacher,
    TimetableInput,
)
from scheduler.parser import load_input


def test_ga_solve_trivial():
    """GA should easily solve a trivial case."""
    data = TimetableInput(periods_per_day=6)
    data.teachers = {"T1": Teacher(id="T1", name="Dr. A", subjects=["S1"])}
    data.rooms = {"R1": Room(id="R1", name="Room 1", capacity=60)}
    data.subjects = {
        "S1": Subject(id="S1", name="DSA", code="CS301", lectures_per_week=3),
    }
    data.student_groups = {
        "G1": StudentGroup(id="G1", name="CSE-3A", strength=50, subjects=["S1"]),
    }

    config = GAConfig(population_size=50, max_generations=100)
    graph, lectures = build_conflict_graph(data)
    timetable, stats = solve(data, graph, lectures, timeout=10.0, config=config)

    assert timetable is not None
    assert stats.solution_found is True
    assert len(timetable.assignments) == 3

    fb = evaluate(timetable, data)
    assert fb.hard_penalty == 0


def test_ga_solve_multiple_groups():
    """GA should handle multiple groups with shared teachers."""
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

    config = GAConfig(population_size=100, max_generations=200)
    graph, lectures = build_conflict_graph(data)
    timetable, stats = solve(data, graph, lectures, timeout=15.0, config=config)

    assert timetable is not None
    assert stats.solution_found is True
    assert len(timetable.assignments) == 8

    fb = evaluate(timetable, data)
    assert fb.hard_penalty == 0


def test_ga_solve_sample_input():
    """GA should solve the full sample input."""
    data = load_input("examples/small_college.json")
    config = GAConfig(population_size=150, max_generations=500)
    graph, lectures = build_conflict_graph(data)
    timetable, stats = solve(data, graph, lectures, timeout=30.0, config=config)

    assert timetable is not None
    assert stats.solution_found is True
    assert len(timetable.assignments) == len(lectures)

    fb = evaluate(timetable, data)
    assert fb.hard_penalty == 0


def test_ga_stats():
    """GA should return meaningful statistics."""
    data = TimetableInput(periods_per_day=6)
    data.teachers = {"T1": Teacher(id="T1", name="Dr. A", subjects=["S1"])}
    data.rooms = {"R1": Room(id="R1", name="Room 1", capacity=60)}
    data.subjects = {
        "S1": Subject(id="S1", name="DSA", code="CS301", lectures_per_week=2),
    }
    data.student_groups = {
        "G1": StudentGroup(id="G1", name="CSE-3A", strength=50, subjects=["S1"]),
    }

    config = GAConfig(population_size=30, max_generations=50)
    graph, lectures = build_conflict_graph(data)
    timetable, stats = solve(data, graph, lectures, timeout=10.0, config=config)

    assert stats.generations_run > 0
    assert stats.nodes_explored > 0
    assert stats.time_seconds > 0
    assert stats.population_size == 30


def test_ga_respects_timeout():
    """GA should stop within timeout."""
    data = TimetableInput(periods_per_day=6)
    data.teachers = {"T1": Teacher(id="T1", name="Dr. A", subjects=["S1"])}
    data.rooms = {"R1": Room(id="R1", name="Room 1", capacity=60)}
    data.subjects = {
        "S1": Subject(id="S1", name="DSA", code="CS301", lectures_per_week=2),
    }
    data.student_groups = {
        "G1": StudentGroup(id="G1", name="CSE-3A", strength=50, subjects=["S1"]),
    }

    config = GAConfig(population_size=50, max_generations=99999)
    graph, lectures = build_conflict_graph(data)
    timetable, stats = solve(data, graph, lectures, timeout=2.0, config=config)

    assert stats.time_seconds < 5.0  # generous upper bound
