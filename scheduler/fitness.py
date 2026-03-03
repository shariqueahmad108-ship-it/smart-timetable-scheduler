"""
Scoring function for timetable quality.

Hard violations (clashes, unavailability) get -1000 each.
Soft penalties (gaps, overloads) get -10 to -50.
Bonuses (consecutive labs, balanced load) give +5 to +10.
"""
from dataclasses import dataclass

from .models import Timetable, TimetableInput


@dataclass
class FitnessBreakdown:
    hard_penalty: int = 0
    soft_penalty: int = 0
    bonus: int = 0
    teacher_clashes: int = 0
    room_clashes: int = 0
    group_clashes: int = 0
    teacher_availability_violations: int = 0
    teacher_overload_days: int = 0
    group_overload_days: int = 0
    student_gaps: int = 0
    consecutive_lab_bonus: int = 0
    balance_bonus: int = 0

    @property
    def total(self) -> int:
        return self.hard_penalty + self.soft_penalty + self.bonus


def evaluate(timetable: Timetable, data: TimetableInput) -> FitnessBreakdown:
    fb = FitnessBreakdown()

    # hard constraints: clashes at each time slot
    for slot in data.get_all_time_slots():
        classes = timetable.get_at_slot(slot)
        teachers: dict[str, int] = {}
        rooms: dict[str, int] = {}
        groups: dict[str, int] = {}

        for sc in classes:
            tid = sc.lecture.teacher_id
            teachers[tid] = teachers.get(tid, 0) + 1
            rooms[sc.room_id] = rooms.get(sc.room_id, 0) + 1
            gid = sc.lecture.group_id
            groups[gid] = groups.get(gid, 0) + 1

        fb.teacher_clashes += sum(c - 1 for c in teachers.values() if c > 1)
        fb.room_clashes += sum(c - 1 for c in rooms.values() if c > 1)
        fb.group_clashes += sum(c - 1 for c in groups.values() if c > 1)

    for sc in timetable.assignments.values():
        teacher = data.teachers[sc.lecture.teacher_id]
        if not teacher.is_available(sc.time_slot.day, sc.time_slot.period):
            fb.teacher_availability_violations += 1

    fb.hard_penalty = -1000 * (
        fb.teacher_clashes + fb.room_clashes + fb.group_clashes + fb.teacher_availability_violations
    )

    # soft constraints
    for teacher_id, teacher in data.teachers.items():
        for day in data.working_days:
            n = sum(1 for sc in timetable.get_teacher_schedule(teacher_id) if sc.time_slot.day == day)
            if n > teacher.max_classes_per_day:
                fb.teacher_overload_days += 1

    for group_id in data.student_groups:
        for day in data.working_days:
            n = sum(1 for sc in timetable.get_group_schedule(group_id) if sc.time_slot.day == day)
            if n > data.max_classes_per_day_per_group:
                fb.group_overload_days += 1

    # gaps in student schedules
    for group_id in data.student_groups:
        for day in data.working_days:
            periods = sorted(
                sc.time_slot.period
                for sc in timetable.get_group_schedule(group_id)
                if sc.time_slot.day == day
            )
            if len(periods) >= 2:
                span = periods[-1] - periods[0] + 1
                fb.student_gaps += span - len(periods)

    fb.soft_penalty = -50 * fb.teacher_overload_days - 30 * fb.group_overload_days - 10 * fb.student_gaps

    # bonuses: consecutive lab sessions
    for group_id in data.student_groups:
        for day in data.working_days:
            day_classes = sorted(
                (sc for sc in timetable.get_group_schedule(group_id) if sc.time_slot.day == day),
                key=lambda sc: sc.time_slot.period,
            )
            for i in range(len(day_classes) - 1):
                curr, nxt = day_classes[i], day_classes[i + 1]
                if (curr.lecture.requires_lab and nxt.lecture.requires_lab
                        and curr.lecture.subject_id == nxt.lecture.subject_id
                        and nxt.time_slot.period == curr.time_slot.period + 1):
                    fb.consecutive_lab_bonus += 1

    # bonus: balanced daily load
    for group_id in data.student_groups:
        counts = [
            sum(1 for sc in timetable.get_group_schedule(group_id) if sc.time_slot.day == day)
            for day in data.working_days
        ]
        if counts:
            avg = sum(counts) / len(counts)
            variance = sum((c - avg) ** 2 for c in counts) / len(counts)
            if variance <= 1.0:
                fb.balance_bonus += 1

    fb.bonus = 10 * fb.consecutive_lab_bonus + 5 * fb.balance_bonus
    return fb
