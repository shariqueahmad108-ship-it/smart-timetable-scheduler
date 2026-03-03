"""
Conflict graph construction.

Each lecture becomes a node; edges connect lectures that can't share
a time slot (same teacher or same student group).
"""
from dataclasses import dataclass, field

from .models import Lecture, TimetableInput


@dataclass
class ConflictGraph:
    lectures: dict[str, Lecture] = field(default_factory=dict)
    adjacency: dict[str, set[str]] = field(default_factory=dict)

    @property
    def num_nodes(self) -> int:
        return len(self.lectures)

    @property
    def num_edges(self) -> int:
        return sum(len(nb) for nb in self.adjacency.values()) // 2

    def add_lecture(self, lecture: Lecture):
        self.lectures[lecture.id] = lecture
        if lecture.id not in self.adjacency:
            self.adjacency[lecture.id] = set()

    def add_conflict(self, id1: str, id2: str):
        self.adjacency[id1].add(id2)
        self.adjacency[id2].add(id1)

    def get_neighbors(self, lecture_id: str) -> set[str]:
        return self.adjacency.get(lecture_id, set())

    def degree(self, lecture_id: str) -> int:
        return len(self.adjacency.get(lecture_id, set()))


def build_conflict_graph(data: TimetableInput) -> tuple[ConflictGraph, list[Lecture]]:
    graph = ConflictGraph()
    all_lectures: list[Lecture] = []

    for group_id, group in data.student_groups.items():
        for subject_id in group.subjects:
            subject = data.subjects[subject_id]
            teacher_id = _find_teacher(data, subject_id)
            if teacher_id is None:
                raise ValueError(f"No teacher found for subject {subject_id} ({subject.name})")

            lab_sessions = subject.lab_hours if subject.requires_lab else 0
            regular = subject.lectures_per_week - lab_sessions

            for i in range(regular):
                lec = Lecture(
                    id=f"{group_id}_{subject_id}_{teacher_id}_L{i+1}",
                    subject_id=subject_id, teacher_id=teacher_id,
                    group_id=group_id, requires_lab=False,
                )
                graph.add_lecture(lec)
                all_lectures.append(lec)

            for i in range(lab_sessions):
                lec = Lecture(
                    id=f"{group_id}_{subject_id}_{teacher_id}_LAB{i+1}",
                    subject_id=subject_id, teacher_id=teacher_id,
                    group_id=group_id, requires_lab=True,
                )
                graph.add_lecture(lec)
                all_lectures.append(lec)

    # pairwise conflict detection
    nodes = list(graph.lectures.values())
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if _conflicts(nodes[i], nodes[j]):
                graph.add_conflict(nodes[i].id, nodes[j].id)

    return graph, all_lectures


def _find_teacher(data: TimetableInput, subject_id: str) -> str | None:
    for tid, teacher in data.teachers.items():
        if subject_id in teacher.subjects:
            return tid
    return None


def _conflicts(a: Lecture, b: Lecture) -> bool:
    return a.teacher_id == b.teacher_id or a.group_id == b.group_id
