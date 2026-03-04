"""Tests for exam scheduling mode."""

from scheduler.annealing import SAConfig, solve as solve_annealing
from scheduler.backtracking import solve as solve_backtracking
from scheduler.exam import apply_exam_penalties
from scheduler.fitness import FitnessBreakdown, evaluate
from scheduler.genetic import GAConfig, solve as solve_genetic
from scheduler.graph import build_conflict_graph
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
from scheduler.parser import load_input


def _exam_data():
    """Create a small exam scheduling dataset."""
    data = TimetableInput(periods_per_day=3, max_classes_per_day_per_group=1, mode="exam")
    data.teachers = {
        "T1": Teacher(id="T1", name="Invigilator A", subjects=["S1", "S2", "S3"], max_classes_per_day=3),
    }
    data.rooms = {
        "R1": Room(id="R1", name="Hall A", capacity=120),
        "R2": Room(id="R2", name="Hall B", capacity=120),
    }
    data.subjects = {
        "S1": Subject(id="S1", name="DSA Exam", code="CS301", lectures_per_week=1),
        "S2": Subject(id="S2", name="DBMS Exam", code="CS302", lectures_per_week=1),
        "S3": Subject(id="S3", name="OS Exam", code="CS303", lectures_per_week=1),
    }
    data.student_groups = {
        "G1": StudentGroup(id="G1", name="CSE-3A", strength=55, subjects=["S1", "S2", "S3"]),
    }
    return data


def test_exam_one_per_day_penalty():
    """Exam mode should penalize >1 exam per group per day."""
    data = _exam_data()

    # Manually create a timetable with 2 exams on the same day for G1
    tt = Timetable()
    lec1 = Lecture(id="L1", subject_id="S1", teacher_id="T1", group_id="G1")
    lec2 = Lecture(id="L2", subject_id="S2", teacher_id="T1", group_id="G1")
    lec3 = Lecture(id="L3", subject_id="S3", teacher_id="T1", group_id="G1")

    tt.add("L1", ScheduledClass(lecture=lec1, time_slot=TimeSlot("Monday", 1), room_id="R1"))
    tt.add("L2", ScheduledClass(lecture=lec2, time_slot=TimeSlot("Monday", 2), room_id="R2"))  # same day!
    tt.add("L3", ScheduledClass(lecture=lec3, time_slot=TimeSlot("Tuesday", 1), room_id="R1"))

    fb = FitnessBreakdown()
    fb = apply_exam_penalties(fb, tt, data)

    # Monday has 2 exams for G1 → 1 violation → -1000
    assert fb.hard_penalty == -1000


def test_exam_back_to_back_penalty():
    """Back-to-back exams should get a soft penalty."""
    data = _exam_data()

    tt = Timetable()
    lec1 = Lecture(id="L1", subject_id="S1", teacher_id="T1", group_id="G1")
    lec2 = Lecture(id="L2", subject_id="S2", teacher_id="T1", group_id="G1")

    # Two exams on same day with consecutive periods
    tt.add("L1", ScheduledClass(lecture=lec1, time_slot=TimeSlot("Monday", 1), room_id="R1"))
    tt.add("L2", ScheduledClass(lecture=lec2, time_slot=TimeSlot("Monday", 2), room_id="R2"))

    fb = FitnessBreakdown()
    fb = apply_exam_penalties(fb, tt, data)

    # Should have back-to-back penalty (-20)
    assert fb.soft_penalty == -20


def test_exam_spread_bonus():
    """Exams spread across different days should get a bonus."""
    data = _exam_data()

    tt = Timetable()
    lec1 = Lecture(id="L1", subject_id="S1", teacher_id="T1", group_id="G1")
    lec2 = Lecture(id="L2", subject_id="S2", teacher_id="T1", group_id="G1")
    lec3 = Lecture(id="L3", subject_id="S3", teacher_id="T1", group_id="G1")

    # Each exam on a different day — perfect spread
    tt.add("L1", ScheduledClass(lecture=lec1, time_slot=TimeSlot("Monday", 1), room_id="R1"))
    tt.add("L2", ScheduledClass(lecture=lec2, time_slot=TimeSlot("Tuesday", 1), room_id="R1"))
    tt.add("L3", ScheduledClass(lecture=lec3, time_slot=TimeSlot("Wednesday", 1), room_id="R1"))

    fb = FitnessBreakdown()
    fb = apply_exam_penalties(fb, tt, data)

    assert fb.hard_penalty == 0
    assert fb.bonus == 15  # spread bonus


def test_exam_mode_full_evaluate():
    """Full evaluate() should include exam penalties when mode='exam'."""
    data = _exam_data()

    tt = Timetable()
    lec1 = Lecture(id="L1", subject_id="S1", teacher_id="T1", group_id="G1")
    lec2 = Lecture(id="L2", subject_id="S2", teacher_id="T1", group_id="G1")
    lec3 = Lecture(id="L3", subject_id="S3", teacher_id="T1", group_id="G1")

    # Perfect exam schedule: each on different day
    tt.add("L1", ScheduledClass(lecture=lec1, time_slot=TimeSlot("Monday", 1), room_id="R1"))
    tt.add("L2", ScheduledClass(lecture=lec2, time_slot=TimeSlot("Tuesday", 1), room_id="R1"))
    tt.add("L3", ScheduledClass(lecture=lec3, time_slot=TimeSlot("Wednesday", 1), room_id="R1"))

    fb = evaluate(tt, data)
    assert fb.hard_penalty == 0
    assert fb.bonus > 0  # should include exam spread bonus


def test_exam_mode_not_applied_in_timetable_mode():
    """Exam penalties should NOT apply in normal timetable mode."""
    data = _exam_data()
    data.mode = "timetable"

    tt = Timetable()
    lec1 = Lecture(id="L1", subject_id="S1", teacher_id="T1", group_id="G1")
    lec2 = Lecture(id="L2", subject_id="S2", teacher_id="T1", group_id="G1")

    # Two on same day — would be penalized in exam mode but not timetable
    tt.add("L1", ScheduledClass(lecture=lec1, time_slot=TimeSlot("Monday", 1), room_id="R1"))
    tt.add("L2", ScheduledClass(lecture=lec2, time_slot=TimeSlot("Monday", 2), room_id="R2"))

    fb = evaluate(tt, data)
    # No exam-specific -1000 penalty for same-day
    assert fb.hard_penalty == 0


def test_exam_with_backtracking():
    """Backtracking solver should produce a valid exam schedule."""
    data = _exam_data()
    graph, lectures = build_conflict_graph(data)
    timetable, stats = solve_backtracking(data, graph, lectures, timeout=10.0)

    assert timetable is not None
    assert stats.solution_found is True

    fb = evaluate(timetable, data)
    assert fb.hard_penalty == 0


def test_exam_with_genetic():
    """GA solver should produce a valid exam schedule."""
    data = _exam_data()
    config = GAConfig(population_size=50, max_generations=200)
    graph, lectures = build_conflict_graph(data)
    timetable, stats = solve_genetic(data, graph, lectures, timeout=15.0, config=config)

    assert timetable is not None
    assert stats.solution_found is True

    fb = evaluate(timetable, data)
    assert fb.hard_penalty == 0


def test_exam_with_sa():
    """SA solver should produce a valid exam schedule."""
    data = _exam_data()
    config = SAConfig(initial_temp=500.0, max_iterations=20000, restarts=3)
    graph, lectures = build_conflict_graph(data)
    timetable, stats = solve_annealing(data, graph, lectures, timeout=15.0, config=config)

    assert timetable is not None
    assert stats.solution_found is True

    fb = evaluate(timetable, data)
    assert fb.hard_penalty == 0


def test_exam_sample_file():
    """Exam sample input file should be solvable."""
    data = load_input("examples/exam_schedule.json")
    data.mode = "exam"
    graph, lectures = build_conflict_graph(data)
    timetable, stats = solve_backtracking(data, graph, lectures, timeout=10.0)

    assert timetable is not None
    assert stats.solution_found is True

    fb = evaluate(timetable, data)
    assert fb.hard_penalty == 0
