"""Tests for the simulated annealing solver."""

from scheduler.fitness import evaluate
from scheduler.annealing import SAConfig, solve
from scheduler.graph import build_conflict_graph
from scheduler.models import (
    Room,
    StudentGroup,
    Subject,
    Teacher,
    TimetableInput,
)
from scheduler.parser import load_input


def test_sa_solve_trivial():
    """SA should easily solve a trivial case."""
    data = TimetableInput(periods_per_day=6)
    data.teachers = {"T1": Teacher(id="T1", name="Dr. A", subjects=["S1"])}
    data.rooms = {"R1": Room(id="R1", name="Room 1", capacity=60)}
    data.subjects = {
        "S1": Subject(id="S1", name="DSA", code="CS301", lectures_per_week=3),
    }
    data.student_groups = {
        "G1": StudentGroup(id="G1", name="CSE-3A", strength=50, subjects=["S1"]),
    }

    config = SAConfig(initial_temp=500.0, max_iterations=10000, restarts=2)
    graph, lectures = build_conflict_graph(data)
    timetable, stats = solve(data, graph, lectures, timeout=10.0, config=config)

    assert timetable is not None
    assert stats.solution_found is True
    assert len(timetable.assignments) == 3

    fb = evaluate(timetable, data)
    assert fb.hard_penalty == 0


def test_sa_solve_multiple_groups():
    """SA should handle multiple groups with shared teachers."""
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

    config = SAConfig(initial_temp=1000.0, max_iterations=30000, restarts=3)
    graph, lectures = build_conflict_graph(data)
    timetable, stats = solve(data, graph, lectures, timeout=15.0, config=config)

    assert timetable is not None
    assert stats.solution_found is True
    assert len(timetable.assignments) == 8

    fb = evaluate(timetable, data)
    assert fb.hard_penalty == 0


def test_sa_solve_sample_input():
    """SA should solve the full sample input."""
    data = load_input("examples/small_college.json")
    config = SAConfig(initial_temp=1000.0, max_iterations=50000, restarts=3)
    graph, lectures = build_conflict_graph(data)
    timetable, stats = solve(data, graph, lectures, timeout=30.0, config=config)

    assert timetable is not None
    assert stats.solution_found is True
    assert len(timetable.assignments) == len(lectures)

    fb = evaluate(timetable, data)
    assert fb.hard_penalty == 0


def test_sa_stats():
    """SA should return meaningful statistics."""
    data = TimetableInput(periods_per_day=6)
    data.teachers = {"T1": Teacher(id="T1", name="Dr. A", subjects=["S1"])}
    data.rooms = {"R1": Room(id="R1", name="Room 1", capacity=60)}
    data.subjects = {
        "S1": Subject(id="S1", name="DSA", code="CS301", lectures_per_week=2),
    }
    data.student_groups = {
        "G1": StudentGroup(id="G1", name="CSE-3A", strength=50, subjects=["S1"]),
    }

    config = SAConfig(initial_temp=500.0, max_iterations=5000, restarts=2)
    graph, lectures = build_conflict_graph(data)
    timetable, stats = solve(data, graph, lectures, timeout=10.0, config=config)

    assert stats.iterations_run > 0
    assert stats.nodes_explored > 0
    assert stats.time_seconds > 0
    assert stats.restarts_used >= 1


def test_sa_respects_timeout():
    """SA should stop within timeout."""
    data = TimetableInput(periods_per_day=6)
    data.teachers = {"T1": Teacher(id="T1", name="Dr. A", subjects=["S1"])}
    data.rooms = {"R1": Room(id="R1", name="Room 1", capacity=60)}
    data.subjects = {
        "S1": Subject(id="S1", name="DSA", code="CS301", lectures_per_week=2),
    }
    data.student_groups = {
        "G1": StudentGroup(id="G1", name="CSE-3A", strength=50, subjects=["S1"]),
    }

    config = SAConfig(initial_temp=10000.0, max_iterations=999999, restarts=99)
    graph, lectures = build_conflict_graph(data)
    timetable, stats = solve(data, graph, lectures, timeout=2.0, config=config)

    assert stats.time_seconds < 5.0  # generous upper bound


def test_sa_config_affects_behavior():
    """Different SA configs should produce different search patterns."""
    data = load_input("examples/small_college.json")
    graph, lectures = build_conflict_graph(data)

    # fast cooling — fewer iterations before temp drops below min_temp
    fast = SAConfig(initial_temp=100.0, cooling_rate=0.9, min_temp=0.1, max_iterations=50000, restarts=1)
    _, stats_fast = solve(data, graph, lectures, timeout=10.0, config=fast)

    # slow cooling — more iterations before temp drops below min_temp
    slow = SAConfig(initial_temp=1000.0, cooling_rate=0.999, min_temp=0.1, max_iterations=50000, restarts=1)
    _, stats_slow = solve(data, graph, lectures, timeout=10.0, config=slow)

    # slow cooling should explore more iterations (temperature takes longer to drop)
    assert stats_slow.iterations_run > stats_fast.iterations_run
