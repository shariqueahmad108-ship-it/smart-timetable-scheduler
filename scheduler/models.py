from dataclasses import dataclass, field


@dataclass
class Teacher:
    id: str
    name: str
    subjects: list[str]
    availability: dict[str, list[int]] | None = None  # day -> available periods
    max_classes_per_day: int = 4

    def is_available(self, day: str, period: int) -> bool:
        if self.availability is None:
            return True
        day_slots = self.availability.get(day)
        if day_slots is None:
            return True
        return period in day_slots


@dataclass
class Room:
    id: str
    name: str
    capacity: int
    room_type: str = "lecture_hall"


@dataclass
class Subject:
    id: str
    name: str
    code: str
    lectures_per_week: int
    requires_lab: bool = False
    lab_hours: int = 0


@dataclass
class StudentGroup:
    id: str
    name: str
    strength: int
    subjects: list[str]


@dataclass
class TimeSlot:
    day: str
    period: int

    def __hash__(self):
        return hash((self.day, self.period))

    def __eq__(self, other):
        if not isinstance(other, TimeSlot):
            return NotImplemented
        return self.day == other.day and self.period == other.period

    def __repr__(self):
        return f"{self.day[:3]}-P{self.period}"


@dataclass
class Lecture:
    """One scheduled session — a (subject, teacher, group) tuple."""
    id: str
    subject_id: str
    teacher_id: str
    group_id: str
    requires_lab: bool = False

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, Lecture):
            return NotImplemented
        return self.id == other.id


@dataclass
class ScheduledClass:
    lecture: Lecture
    time_slot: TimeSlot
    room_id: str


@dataclass
class TimetableInput:
    teachers: dict[str, Teacher] = field(default_factory=dict)
    rooms: dict[str, Room] = field(default_factory=dict)
    subjects: dict[str, Subject] = field(default_factory=dict)
    student_groups: dict[str, StudentGroup] = field(default_factory=dict)
    working_days: list[str] = field(
        default_factory=lambda: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    )
    periods_per_day: int = 6
    lunch_break_after_period: int = 3
    max_classes_per_day_per_group: int = 5
    mode: str = "timetable"  # "timetable" or "exam"

    def get_all_time_slots(self) -> list[TimeSlot]:
        return [
            TimeSlot(day=day, period=p)
            for day in self.working_days
            for p in range(1, self.periods_per_day + 1)
        ]

    def get_suitable_rooms(self, lecture: Lecture) -> list[Room]:
        subject = self.subjects[lecture.subject_id]
        group = self.student_groups[lecture.group_id]
        suitable = []
        for room in self.rooms.values():
            if room.capacity < group.strength:
                continue
            if subject.requires_lab and lecture.requires_lab and room.room_type != "lab":
                continue
            suitable.append(room)
        return suitable


@dataclass
class Timetable:
    assignments: dict[str, ScheduledClass] = field(default_factory=dict)

    def add(self, lecture_id: str, scheduled: ScheduledClass):
        self.assignments[lecture_id] = scheduled

    def remove(self, lecture_id: str):
        self.assignments.pop(lecture_id, None)

    def get_teacher_schedule(self, teacher_id: str) -> list[ScheduledClass]:
        return [sc for sc in self.assignments.values() if sc.lecture.teacher_id == teacher_id]

    def get_group_schedule(self, group_id: str) -> list[ScheduledClass]:
        return [sc for sc in self.assignments.values() if sc.lecture.group_id == group_id]

    def get_room_schedule(self, room_id: str) -> list[ScheduledClass]:
        return [sc for sc in self.assignments.values() if sc.room_id == room_id]

    def get_at_slot(self, time_slot: TimeSlot) -> list[ScheduledClass]:
        return [sc for sc in self.assignments.values() if sc.time_slot == time_slot]
