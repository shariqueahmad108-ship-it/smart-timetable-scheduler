from .models import Timetable, TimetableInput


COL_WIDTH = 22


def format_timetable_by_group(timetable: Timetable, data: TimetableInput) -> str:
    lines: list[str] = []

    for group_id, group in data.student_groups.items():
        lines.append("")
        lines.append("=" * 90)
        lines.append(f"  TIMETABLE: {group.name} (Strength: {group.strength})")
        lines.append("=" * 90)

        header = f"{'Period':<10}" + "".join(f"{d:<{COL_WIDTH}}" for d in data.working_days)
        lines.append(header)
        lines.append("-" * 90)

        for period in range(1, data.periods_per_day + 1):
            row = f"{'P' + str(period):<10}"
            for day in data.working_days:
                cell = _find_cell(timetable, data, group_id, day, period)
                row += f"{cell:<{COL_WIDTH}}"
            lines.append(row)

            if period == data.lunch_break_after_period:
                lines.append(f"{'LUNCH':<10}" + "~ ~ ~ ~ ~ " * len(data.working_days))

        lines.append("")
    return "\n".join(lines)


def _find_cell(timetable, data, group_id, day, period) -> str:
    for sc in timetable.assignments.values():
        if sc.lecture.group_id == group_id and sc.time_slot.day == day and sc.time_slot.period == period:
            subj = data.subjects[sc.lecture.subject_id]
            room = data.rooms[sc.room_id]
            lab = " [LAB]" if sc.lecture.requires_lab else ""
            return f"{subj.code}{lab} ({room.name[:5]})"
    return "---"


def format_teacher_schedule(timetable: Timetable, data: TimetableInput) -> str:
    lines: list[str] = []

    for teacher_id, teacher in data.teachers.items():
        schedule = timetable.get_teacher_schedule(teacher_id)
        if not schedule:
            continue

        lines.append("")
        lines.append(f"--- {teacher.name} ({teacher_id}) ---")

        for day in data.working_days:
            day_classes = sorted(
                [sc for sc in schedule if sc.time_slot.day == day],
                key=lambda sc: sc.time_slot.period,
            )
            if day_classes:
                parts = [
                    f"P{sc.time_slot.period}-{data.subjects[sc.lecture.subject_id].code}"
                    f"({data.student_groups[sc.lecture.group_id].name},{data.rooms[sc.room_id].name})"
                    for sc in day_classes
                ]
                lines.append(f"  {day[:3]}: " + " | ".join(parts))

    return "\n".join(lines)


def print_stats(timetable: Timetable, data: TimetableInput, stats) -> str:
    lines = [
        "", "=" * 50, "  SOLVER STATISTICS", "=" * 50,
        f"  Total lectures scheduled: {len(timetable.assignments)}",
    ]
    for attr, label in [("nodes_explored", "Nodes explored"), ("backtracks", "Backtracks")]:
        if hasattr(stats, attr):
            lines.append(f"  {label}: {getattr(stats, attr)}")
    if hasattr(stats, "time_seconds"):
        lines.append(f"  Time taken: {stats.time_seconds:.3f}s")
    if hasattr(stats, "solution_found"):
        lines.append(f"  Solution: {'FOUND' if stats.solution_found else 'NOT FOUND'}")
    lines.append("=" * 50)
    return "\n".join(lines)
