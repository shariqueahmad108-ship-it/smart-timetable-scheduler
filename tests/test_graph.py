"""Tests for conflict graph construction."""

from scheduler.graph import build_conflict_graph
from scheduler.models import (
    Room,
    StudentGroup,
    Subject,
    Teacher,
    TimetableInput,
)


def _make_data() -> TimetableInput:
    data = TimetableInput(periods_per_day=6)
    data.teachers = {
        "T1": Teacher(id="T1", name="Dr. A", subjects=["S1", "S2"]),
        "T2": Teacher(id="T2", name="Dr. B", subjects=["S3"]),
    }
    data.rooms = {
        "R1": Room(id="R1", name="Room 1", capacity=60),
    }
    data.subjects = {
        "S1": Subject(id="S1", name="DSA", code="CS301", lectures_per_week=2),
        "S2": Subject(id="S2", name="DBMS", code="CS302", lectures_per_week=1),
        "S3": Subject(id="S3", name="OS", code="CS303", lectures_per_week=2),
    }
    data.student_groups = {
        "G1": StudentGroup(id="G1", name="CSE-3A", strength=50, subjects=["S1", "S2", "S3"]),
    }
    return data


def test_correct_number_of_lectures():
    data = _make_data()
    graph, lectures = build_conflict_graph(data)

    # S1: 2 lectures, S2: 1 lecture, S3: 2 lectures = 5 total
    assert len(lectures) == 5
    assert graph.num_nodes == 5


def test_conflicts_same_teacher():
    data = _make_data()
    graph, lectures = build_conflict_graph(data)

    # T1 teaches S1 and S2 for G1 — all 3 lectures by T1 should conflict with each other
    t1_lectures = [l for l in lectures if l.teacher_id == "T1"]
    assert len(t1_lectures) == 3  # 2 for S1 + 1 for S2

    for i in range(len(t1_lectures)):
        for j in range(i + 1, len(t1_lectures)):
            assert t1_lectures[j].id in graph.get_neighbors(t1_lectures[i].id)


def test_conflicts_same_group():
    data = _make_data()
    graph, lectures = build_conflict_graph(data)

    # All lectures are for G1, so every pair should conflict
    for i in range(len(lectures)):
        for j in range(i + 1, len(lectures)):
            assert lectures[j].id in graph.get_neighbors(lectures[i].id)


def test_no_conflict_different_teacher_different_group():
    data = TimetableInput(periods_per_day=6)
    data.teachers = {
        "T1": Teacher(id="T1", name="Dr. A", subjects=["S1"]),
        "T2": Teacher(id="T2", name="Dr. B", subjects=["S2"]),
    }
    data.rooms = {
        "R1": Room(id="R1", name="Room 1", capacity=60),
    }
    data.subjects = {
        "S1": Subject(id="S1", name="DSA", code="CS301", lectures_per_week=1),
        "S2": Subject(id="S2", name="OS", code="CS302", lectures_per_week=1),
    }
    data.student_groups = {
        "G1": StudentGroup(id="G1", name="CSE-3A", strength=50, subjects=["S1"]),
        "G2": StudentGroup(id="G2", name="CSE-3B", strength=50, subjects=["S2"]),
    }

    graph, lectures = build_conflict_graph(data)
    assert len(lectures) == 2
    # Different teacher + different group = no conflict
    assert graph.num_edges == 0
