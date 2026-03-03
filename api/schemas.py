from enum import Enum

from pydantic import BaseModel, Field


class TeacherIn(BaseModel):
    id: str
    name: str
    subjects: list[str]


class RoomIn(BaseModel):
    id: str
    name: str
    capacity: int
    type: str = "lecture_hall"


class SubjectIn(BaseModel):
    id: str
    name: str
    code: str
    lectures_per_week: int
    requires_lab: bool = False
    lab_hours: int = 0


class StudentGroupIn(BaseModel):
    id: str
    name: str
    strength: int
    subjects: list[str]


class TeacherPreference(BaseModel):
    no_classes_before: str | None = None
    preferred_days: list[str] | None = None


class ConstraintsIn(BaseModel):
    teacher_preferences: dict[str, TeacherPreference] = Field(default_factory=dict)
    max_classes_per_day_per_teacher: int = 4
    max_classes_per_day_per_group: int = 5
    lunch_break_after_period: int = 3


class Algorithm(str, Enum):
    BACKTRACKING = "backtracking"
    GENETIC = "genetic"


class GenerateRequest(BaseModel):
    teachers: list[TeacherIn]
    rooms: list[RoomIn]
    subjects: list[SubjectIn]
    student_groups: list[StudentGroupIn]
    working_days: list[str] = Field(default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
    periods_per_day: int = 6
    constraints: ConstraintsIn = Field(default_factory=ConstraintsIn)
    timeout: float = 30.0
    algorithm: Algorithm = Algorithm.BACKTRACKING
    ga_population: int = 100
    ga_generations: int = 500


# --- responses ---

class ScheduledClassOut(BaseModel):
    subject_id: str
    subject_code: str
    subject_name: str
    teacher_id: str
    teacher_name: str
    group_id: str
    group_name: str
    room_id: str
    room_name: str
    day: str
    period: int
    is_lab: bool


class ViolationOut(BaseModel):
    constraint_type: str
    description: str
    penalty: int


class FitnessOut(BaseModel):
    total: int = 0
    hard_penalty: int = 0
    soft_penalty: int = 0
    bonus: int = 0
    teacher_clashes: int = 0
    room_clashes: int = 0
    group_clashes: int = 0
    student_gaps: int = 0


class SolverStatsOut(BaseModel):
    nodes_explored: int
    backtracks: int
    time_seconds: float
    solution_found: bool
    total_lectures: int
    algorithm: str = "backtracking"
    generations_run: int | None = None
    best_generation: int | None = None


class GenerateResponse(BaseModel):
    success: bool
    schedule: list[ScheduledClassOut] = Field(default_factory=list)
    violations: list[ViolationOut] = Field(default_factory=list)
    stats: SolverStatsOut | None = None
    fitness: FitnessOut | None = None
    error: str | None = None
