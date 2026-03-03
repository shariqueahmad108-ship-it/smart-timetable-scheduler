import json
from pathlib import Path
from typing import Any

from .models import Room, StudentGroup, Subject, Teacher, TimetableInput


def load_input(filepath: str) -> TimetableInput:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {filepath}")

    with open(path, encoding="utf-8") as f:
        return parse_input(json.load(f))


def parse_input(raw: dict[str, Any]) -> TimetableInput:
    data = TimetableInput()

    if "working_days" in raw:
        data.working_days = raw["working_days"]
    if "periods_per_day" in raw:
        data.periods_per_day = raw["periods_per_day"]

    constraints = raw.get("constraints", {})
    if "lunch_break_after_period" in constraints:
        data.lunch_break_after_period = constraints["lunch_break_after_period"]
    if "max_classes_per_day_per_group" in constraints:
        data.max_classes_per_day_per_group = constraints["max_classes_per_day_per_group"]

    max_daily = constraints.get("max_classes_per_day_per_teacher", 4)
    teacher_prefs = constraints.get("teacher_preferences", {})

    for t in raw.get("teachers", []):
        teacher = Teacher(id=t["id"], name=t["name"], subjects=t["subjects"], max_classes_per_day=max_daily)

        prefs = teacher_prefs.get(t["id"], {})
        if "preferred_days" in prefs:
            teacher.availability = {
                day: list(range(1, data.periods_per_day + 1))
                for day in prefs["preferred_days"]
            }
        if "no_classes_before" in prefs:
            hour = int(prefs["no_classes_before"].split(":")[0])
            skip = hour - 9  # classes start at 9
            if teacher.availability is None:
                teacher.availability = {
                    day: list(range(skip + 1, data.periods_per_day + 1))
                    for day in data.working_days
                }
            else:
                for day in teacher.availability:
                    teacher.availability[day] = [p for p in teacher.availability[day] if p > skip]

        data.teachers[t["id"]] = teacher

    for r in raw.get("rooms", []):
        data.rooms[r["id"]] = Room(
            id=r["id"], name=r["name"], capacity=r["capacity"],
            room_type=r.get("type", "lecture_hall"),
        )

    for s in raw.get("subjects", []):
        data.subjects[s["id"]] = Subject(
            id=s["id"], name=s["name"], code=s["code"],
            lectures_per_week=s["lectures_per_week"],
            requires_lab=s.get("requires_lab", False),
            lab_hours=s.get("lab_hours", 0),
        )

    for g in raw.get("student_groups", []):
        data.student_groups[g["id"]] = StudentGroup(
            id=g["id"], name=g["name"], strength=g["strength"], subjects=g["subjects"],
        )

    return data
