"""Tests for data models."""

from scheduler.models import (
    Lecture,
    Room,
    ScheduledClass,
    Teacher,
    TimeSlot,
    Timetable,
    TimetableInput,
)


def test_teacher_availability_default():
    t = Teacher(id="T1", name="Test", subjects=["S1"])
    assert t.is_available("Monday", 1) is True
    assert t.is_available("Friday", 6) is True


def test_teacher_availability_restricted():
    t = Teacher(
        id="T1",
        name="Test",
        subjects=["S1"],
        availability={"Monday": [1, 2, 3], "Tuesday": [4, 5]},
    )
    assert t.is_available("Monday", 1) is True
    assert t.is_available("Monday", 4) is False
    assert t.is_available("Tuesday", 4) is True
    assert t.is_available("Wednesday", 1) is True  # not restricted


def test_timeslot_equality():
    s1 = TimeSlot(day="Monday", period=1)
    s2 = TimeSlot(day="Monday", period=1)
    s3 = TimeSlot(day="Monday", period=2)
    assert s1 == s2
    assert s1 != s3
    assert hash(s1) == hash(s2)


def test_timetable_add_remove():
    tt = Timetable()
    lecture = Lecture(id="L1", subject_id="S1", teacher_id="T1", group_id="G1")
    slot = TimeSlot(day="Monday", period=1)
    sc = ScheduledClass(lecture=lecture, time_slot=slot, room_id="R1")

    tt.add("L1", sc)
    assert len(tt.assignments) == 1
    assert tt.get_at_slot(slot) == [sc]

    tt.remove("L1")
    assert len(tt.assignments) == 0


def test_timetable_queries():
    tt = Timetable()
    l1 = Lecture(id="L1", subject_id="S1", teacher_id="T1", group_id="G1")
    l2 = Lecture(id="L2", subject_id="S2", teacher_id="T1", group_id="G2")
    l3 = Lecture(id="L3", subject_id="S3", teacher_id="T2", group_id="G1")

    slot1 = TimeSlot(day="Monday", period=1)
    slot2 = TimeSlot(day="Monday", period=2)

    tt.add("L1", ScheduledClass(lecture=l1, time_slot=slot1, room_id="R1"))
    tt.add("L2", ScheduledClass(lecture=l2, time_slot=slot2, room_id="R2"))
    tt.add("L3", ScheduledClass(lecture=l3, time_slot=slot1, room_id="R2"))

    # Teacher T1 has 2 classes
    assert len(tt.get_teacher_schedule("T1")) == 2

    # Group G1 has 2 classes
    assert len(tt.get_group_schedule("G1")) == 2

    # Room R2 has 2 classes
    assert len(tt.get_room_schedule("R2")) == 2

    # Slot1 has 2 classes
    assert len(tt.get_at_slot(slot1)) == 2


def test_get_all_time_slots():
    data = TimetableInput(
        working_days=["Monday", "Tuesday"],
        periods_per_day=3,
    )
    slots = data.get_all_time_slots()
    assert len(slots) == 6
    assert slots[0] == TimeSlot(day="Monday", period=1)
    assert slots[-1] == TimeSlot(day="Tuesday", period=3)


def test_get_suitable_rooms():
    data = TimetableInput()
    data.rooms = {
        "R1": Room(id="R1", name="Big Room", capacity=60, room_type="lecture_hall"),
        "R2": Room(id="R2", name="Small Room", capacity=20, room_type="lecture_hall"),
        "R3": Room(id="R3", name="Lab", capacity=30, room_type="lab"),
    }
    from scheduler.models import StudentGroup, Subject

    data.subjects = {
        "S1": Subject(id="S1", name="DSA", code="CS301", lectures_per_week=4, requires_lab=True),
    }
    data.student_groups = {
        "G1": StudentGroup(id="G1", name="CSE-3A", strength=25, subjects=["S1"]),
    }

    # Lab lecture — needs lab room with enough capacity
    lab_lecture = Lecture(id="L1", subject_id="S1", teacher_id="T1", group_id="G1", requires_lab=True)
    suitable = data.get_suitable_rooms(lab_lecture)
    assert len(suitable) == 1
    assert suitable[0].id == "R3"

    # Regular lecture — any room with enough capacity (R2 too small at 20 < 25)
    reg_lecture = Lecture(id="L2", subject_id="S1", teacher_id="T1", group_id="G1", requires_lab=False)
    suitable = data.get_suitable_rooms(reg_lecture)
    assert len(suitable) == 2  # R1 (60) and R3 (30) fit, R2 (20) doesn't
