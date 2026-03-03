from dataclasses import dataclass

from .models import TimeSlot, Timetable, TimetableInput


@dataclass
class Violation:
    constraint_type: str  # "hard" or "soft"
    description: str
    penalty: int


def check_teacher_clash(timetable: Timetable, time_slot: TimeSlot, teacher_id: str) -> bool:
    return any(sc.lecture.teacher_id == teacher_id for sc in timetable.get_at_slot(time_slot))


def check_room_clash(timetable: Timetable, time_slot: TimeSlot, room_id: str) -> bool:
    return any(sc.room_id == room_id for sc in timetable.get_at_slot(time_slot))


def check_group_clash(timetable: Timetable, time_slot: TimeSlot, group_id: str) -> bool:
    return any(sc.lecture.group_id == group_id for sc in timetable.get_at_slot(time_slot))


def is_slot_valid(
    timetable: Timetable,
    time_slot: TimeSlot,
    teacher_id: str,
    group_id: str,
    room_id: str,
    data: TimetableInput,
) -> bool:
    """Check all hard constraints for assigning a lecture to a slot + room."""
    if check_teacher_clash(timetable, time_slot, teacher_id):
        return False
    if check_room_clash(timetable, time_slot, room_id):
        return False
    if check_group_clash(timetable, time_slot, group_id):
        return False

    teacher = data.teachers[teacher_id]
    if not teacher.is_available(time_slot.day, time_slot.period):
        return False

    teacher_day_count = sum(
        1 for sc in timetable.get_teacher_schedule(teacher_id)
        if sc.time_slot.day == time_slot.day
    )
    if teacher_day_count >= teacher.max_classes_per_day:
        return False

    group_day_count = sum(
        1 for sc in timetable.get_group_schedule(group_id)
        if sc.time_slot.day == time_slot.day
    )
    if group_day_count >= data.max_classes_per_day_per_group:
        return False

    return True


def validate_timetable(timetable: Timetable, data: TimetableInput) -> list[Violation]:
    """Run all constraint checks on a completed timetable."""
    violations: list[Violation] = []

    for slot in data.get_all_time_slots():
        classes_at_slot = timetable.get_at_slot(slot)

        teachers_at_slot: dict[str, int] = {}
        rooms_at_slot: dict[str, int] = {}
        groups_at_slot: dict[str, int] = {}

        for sc in classes_at_slot:
            tid = sc.lecture.teacher_id
            teachers_at_slot[tid] = teachers_at_slot.get(tid, 0) + 1
            rooms_at_slot[sc.room_id] = rooms_at_slot.get(sc.room_id, 0) + 1
            gid = sc.lecture.group_id
            groups_at_slot[gid] = groups_at_slot.get(gid, 0) + 1

        for tid, count in teachers_at_slot.items():
            if count > 1:
                violations.append(Violation("hard", f"Teacher {tid} has {count} classes at {slot}", 1000))

        for rid, count in rooms_at_slot.items():
            if count > 1:
                violations.append(Violation("hard", f"Room {rid} has {count} classes at {slot}", 1000))

        for gid, count in groups_at_slot.items():
            if count > 1:
                violations.append(Violation("hard", f"Group {gid} has {count} classes at {slot}", 1000))

    for teacher_id, teacher in data.teachers.items():
        for day in data.working_days:
            day_count = sum(1 for sc in timetable.get_teacher_schedule(teacher_id) if sc.time_slot.day == day)
            if day_count > teacher.max_classes_per_day:
                violations.append(Violation(
                    "soft", f"Teacher {teacher_id} has {day_count} classes on {day} (max {teacher.max_classes_per_day})", 50
                ))

    for group_id in data.student_groups:
        for day in data.working_days:
            day_count = sum(1 for sc in timetable.get_group_schedule(group_id) if sc.time_slot.day == day)
            if day_count > data.max_classes_per_day_per_group:
                violations.append(Violation(
                    "soft", f"Group {group_id} has {day_count} classes on {day} (max {data.max_classes_per_day_per_group})", 30
                ))

    return violations


def count_hard_violations(violations: list[Violation]) -> int:
    return sum(1 for v in violations if v.constraint_type == "hard")


def count_soft_violations(violations: list[Violation]) -> int:
    return sum(1 for v in violations if v.constraint_type == "soft")


def total_penalty(violations: list[Violation]) -> int:
    return sum(v.penalty for v in violations)
