"""
Exam scheduling fitness adjustments.

In exam mode, additional constraints apply:
- Hard: max 1 exam per student group per day
- Soft: no back-to-back exams for the same group (consecutive periods)
- Bonus: exams spread evenly across available days
"""
from .fitness import FitnessBreakdown
from .models import Timetable, TimetableInput


def apply_exam_penalties(
    fb: FitnessBreakdown, timetable: Timetable, data: TimetableInput
) -> FitnessBreakdown:
    """Layer exam-specific penalties on top of the base fitness breakdown."""

    exam_day_violations = 0
    back_to_back_penalties = 0
    spread_bonus = 0

    for group_id in data.student_groups:
        days_with_exams = 0

        for day in data.working_days:
            day_classes = [
                sc for sc in timetable.get_group_schedule(group_id)
                if sc.time_slot.day == day
            ]
            count = len(day_classes)

            if count > 1:
                # hard constraint: only 1 exam per group per day
                exam_day_violations += count - 1

            if count > 0:
                days_with_exams += 1

            # soft: penalize back-to-back exams (consecutive periods)
            if count >= 2:
                periods = sorted(sc.time_slot.period for sc in day_classes)
                for i in range(len(periods) - 1):
                    if periods[i + 1] == periods[i] + 1:
                        back_to_back_penalties += 1

        # bonus: reward spreading exams across many days
        total_exams = len(timetable.get_group_schedule(group_id))
        if total_exams > 0 and days_with_exams >= min(total_exams, len(data.working_days)):
            spread_bonus += 1

    fb.hard_penalty += -1000 * exam_day_violations
    fb.soft_penalty += -20 * back_to_back_penalties
    fb.bonus += 15 * spread_bonus

    return fb
