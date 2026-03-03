"""Tests for the fitness function."""

from scheduler.fitness import evaluate
from scheduler.models import (
    Lecture,
    Room,
    ScheduledClass,
    StudentGroup,
    Subject,
    Teacher,
    TimeSlot,
    Timetable,
    TimetableInput,
)


def _make_data() -> TimetableInput:
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
    }
    return data


def test_fitness_no_violations():
    data = _make_data()
    tt = Timetable()
    # Clean schedule — no clashes, different slots
    tt.add("L1", ScheduledClass(
        lecture=Lecture(id="L1", subject_id="S1", teacher_id="T1", group_id="G1"),
        time_slot=TimeSlot("Monday", 1), room_id="R1"))
    tt.add("L2", ScheduledClass(
        lecture=Lecture(id="L2", subject_id="S1", teacher_id="T1", group_id="G1"),
        time_slot=TimeSlot("Monday", 2), room_id="R1"))
    tt.add("L3", ScheduledClass(
        lecture=Lecture(id="L3", subject_id="S2", teacher_id="T2", group_id="G1"),
        time_slot=TimeSlot("Tuesday", 1), room_id="R1"))
    tt.add("L4", ScheduledClass(
        lecture=Lecture(id="L4", subject_id="S2", teacher_id="T2", group_id="G1"),
        time_slot=TimeSlot("Tuesday", 2), room_id="R1"))

    fb = evaluate(tt, data)
    assert fb.hard_penalty == 0
    assert fb.teacher_clashes == 0
    assert fb.room_clashes == 0
    assert fb.group_clashes == 0


def test_fitness_teacher_clash():
    data = _make_data()
    tt = Timetable()
    slot = TimeSlot("Monday", 1)
    # Same teacher, same slot — CLASH
    tt.add("L1", ScheduledClass(
        lecture=Lecture(id="L1", subject_id="S1", teacher_id="T1", group_id="G1"),
        time_slot=slot, room_id="R1"))
    tt.add("L2", ScheduledClass(
        lecture=Lecture(id="L2", subject_id="S1", teacher_id="T1", group_id="G1"),
        time_slot=slot, room_id="R2"))

    fb = evaluate(tt, data)
    assert fb.teacher_clashes > 0
    assert fb.hard_penalty < 0


def test_fitness_student_gaps():
    data = _make_data()
    tt = Timetable()
    # Classes at P1 and P4 — gap of 2 periods
    tt.add("L1", ScheduledClass(
        lecture=Lecture(id="L1", subject_id="S1", teacher_id="T1", group_id="G1"),
        time_slot=TimeSlot("Monday", 1), room_id="R1"))
    tt.add("L2", ScheduledClass(
        lecture=Lecture(id="L2", subject_id="S2", teacher_id="T2", group_id="G1"),
        time_slot=TimeSlot("Monday", 4), room_id="R2"))

    fb = evaluate(tt, data)
    assert fb.student_gaps == 2  # P2 and P3 are gaps
    assert fb.soft_penalty < 0


def test_fitness_total_calculation():
    data = _make_data()
    tt = Timetable()
    tt.add("L1", ScheduledClass(
        lecture=Lecture(id="L1", subject_id="S1", teacher_id="T1", group_id="G1"),
        time_slot=TimeSlot("Monday", 1), room_id="R1"))

    fb = evaluate(tt, data)
    assert fb.total == fb.hard_penalty + fb.soft_penalty + fb.bonus
