"""Tests for constraint checking."""

from scheduler.constraints import (
    check_group_clash,
    check_room_clash,
    check_teacher_clash,
    count_hard_violations,
    is_slot_valid,
    validate_timetable,
)
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
        "S1": Subject(id="S1", name="DSA", code="CS301", lectures_per_week=3),
        "S2": Subject(id="S2", name="OS", code="CS302", lectures_per_week=3),
    }
    data.student_groups = {
        "G1": StudentGroup(id="G1", name="CSE-3A", strength=50, subjects=["S1", "S2"]),
    }
    return data


def test_teacher_clash_detected():
    tt = Timetable()
    slot = TimeSlot(day="Monday", period=1)
    l1 = Lecture(id="L1", subject_id="S1", teacher_id="T1", group_id="G1")
    tt.add("L1", ScheduledClass(lecture=l1, time_slot=slot, room_id="R1"))

    assert check_teacher_clash(tt, slot, "T1") is True
    assert check_teacher_clash(tt, slot, "T2") is False


def test_room_clash_detected():
    tt = Timetable()
    slot = TimeSlot(day="Monday", period=1)
    l1 = Lecture(id="L1", subject_id="S1", teacher_id="T1", group_id="G1")
    tt.add("L1", ScheduledClass(lecture=l1, time_slot=slot, room_id="R1"))

    assert check_room_clash(tt, slot, "R1") is True
    assert check_room_clash(tt, slot, "R2") is False


def test_group_clash_detected():
    tt = Timetable()
    slot = TimeSlot(day="Monday", period=1)
    l1 = Lecture(id="L1", subject_id="S1", teacher_id="T1", group_id="G1")
    tt.add("L1", ScheduledClass(lecture=l1, time_slot=slot, room_id="R1"))

    assert check_group_clash(tt, slot, "G1") is True
    assert check_group_clash(tt, slot, "G2") is False


def test_is_slot_valid_no_conflicts():
    data = _make_data()
    tt = Timetable()
    slot = TimeSlot(day="Monday", period=1)
    assert is_slot_valid(tt, slot, "T1", "G1", "R1", data) is True


def test_is_slot_valid_teacher_conflict():
    data = _make_data()
    tt = Timetable()
    slot = TimeSlot(day="Monday", period=1)
    l1 = Lecture(id="L1", subject_id="S1", teacher_id="T1", group_id="G1")
    tt.add("L1", ScheduledClass(lecture=l1, time_slot=slot, room_id="R1"))

    # T1 already teaching at this slot
    assert is_slot_valid(tt, slot, "T1", "G2", "R2", data) is False
    # T2 is free
    assert is_slot_valid(tt, slot, "T2", "G2", "R2", data) is True


def test_validate_timetable_clean():
    data = _make_data()
    tt = Timetable()
    l1 = Lecture(id="L1", subject_id="S1", teacher_id="T1", group_id="G1")
    l2 = Lecture(id="L2", subject_id="S2", teacher_id="T2", group_id="G1")
    tt.add("L1", ScheduledClass(lecture=l1, time_slot=TimeSlot("Monday", 1), room_id="R1"))
    tt.add("L2", ScheduledClass(lecture=l2, time_slot=TimeSlot("Monday", 2), room_id="R1"))

    violations = validate_timetable(tt, data)
    hard = count_hard_violations(violations)
    assert hard == 0


def test_validate_timetable_with_clash():
    data = _make_data()
    tt = Timetable()
    slot = TimeSlot("Monday", 1)
    l1 = Lecture(id="L1", subject_id="S1", teacher_id="T1", group_id="G1")
    l2 = Lecture(id="L2", subject_id="S2", teacher_id="T1", group_id="G1")
    # Force both into same slot (bypassing solver)
    tt.add("L1", ScheduledClass(lecture=l1, time_slot=slot, room_id="R1"))
    tt.add("L2", ScheduledClass(lecture=l2, time_slot=slot, room_id="R2"))

    violations = validate_timetable(tt, data)
    hard = count_hard_violations(violations)
    assert hard > 0  # teacher clash + group clash
