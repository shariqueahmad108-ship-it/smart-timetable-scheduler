"""
Backtracking solver using graph coloring.

Treats lectures as graph nodes and (time_slot, room) pairs as colors.
Uses MRV (pick the most constrained variable first) and forward
checking (prune neighbor domains after each assignment) to cut
the search space.
"""
import time
from dataclasses import dataclass

from .constraints import is_slot_valid
from .graph import ConflictGraph
from .models import Lecture, ScheduledClass, TimeSlot, Timetable, TimetableInput


@dataclass
class SolverStats:
    nodes_explored: int = 0
    backtracks: int = 0
    time_seconds: float = 0.0
    solution_found: bool = False


def solve(
    data: TimetableInput,
    graph: ConflictGraph,
    lectures: list[Lecture],
    timeout: float = 30.0,
) -> tuple[Timetable | None, SolverStats]:
    stats = SolverStats()
    start = time.time()
    timetable = Timetable()
    all_slots = data.get_all_time_slots()

    # build domain: for each lecture, all valid (slot, room) combos
    domains: dict[str, list[tuple[TimeSlot, str]]] = {}
    for lec in lectures:
        rooms = data.get_suitable_rooms(lec)
        domains[lec.id] = [(s, r.id) for s in all_slots for r in rooms]

    unassigned = {lec.id for lec in lectures}
    success = _backtrack(data, graph, timetable, domains, unassigned, stats, start, timeout)

    stats.time_seconds = time.time() - start
    stats.solution_found = success
    return (timetable if success else None), stats


def _select_mrv(
    domains: dict[str, list[tuple[TimeSlot, str]]],
    unassigned: set[str],
    graph: ConflictGraph,
) -> str:
    """Pick the variable with fewest remaining values; break ties by degree."""
    best_id = None
    best_size = float("inf")
    best_deg = -1

    for lid in unassigned:
        size = len(domains[lid])
        deg = graph.degree(lid)
        if size < best_size or (size == best_size and deg > best_deg):
            best_id = lid
            best_size = size
            best_deg = deg

    return best_id  # type: ignore[return-value]


def _forward_check(
    lecture_id: str,
    slot: TimeSlot,
    room_id: str,
    graph: ConflictGraph,
    domains: dict[str, list[tuple[TimeSlot, str]]],
    unassigned: set[str],
    data: TimetableInput,
    timetable: Timetable,
) -> dict[str, list[tuple[TimeSlot, str]]]:
    """Prune neighbor domains after an assignment. Returns removed values for undo."""
    pruned: dict[str, list[tuple[TimeSlot, str]]] = {}

    for nid in graph.get_neighbors(lecture_id):
        if nid not in unassigned:
            continue

        neighbor = graph.lectures[nid]
        removed = []
        kept = []

        for s, r in domains[nid]:
            # conflicting lectures can't share a time slot
            if s == slot:
                removed.append((s, r))
            elif not is_slot_valid(timetable, s, neighbor.teacher_id, neighbor.group_id, r, data):
                removed.append((s, r))
            else:
                kept.append((s, r))

        if removed:
            pruned[nid] = removed
            domains[nid] = kept

    return pruned


def _restore_domains(
    pruned: dict[str, list[tuple[TimeSlot, str]]],
    domains: dict[str, list[tuple[TimeSlot, str]]],
):
    for nid, removed in pruned.items():
        domains[nid].extend(removed)


def _backtrack(
    data: TimetableInput,
    graph: ConflictGraph,
    timetable: Timetable,
    domains: dict[str, list[tuple[TimeSlot, str]]],
    unassigned: set[str],
    stats: SolverStats,
    start: float,
    timeout: float,
) -> bool:
    if not unassigned:
        return True
    if time.time() - start > timeout:
        return False

    stats.nodes_explored += 1
    lid = _select_mrv(domains, unassigned, graph)
    lecture = graph.lectures[lid]

    for slot, room_id in list(domains[lid]):
        if not is_slot_valid(timetable, slot, lecture.teacher_id, lecture.group_id, room_id, data):
            continue

        timetable.add(lid, ScheduledClass(lecture=lecture, time_slot=slot, room_id=room_id))
        unassigned.remove(lid)

        pruned = _forward_check(lid, slot, room_id, graph, domains, unassigned, data, timetable)

        # if any neighbor lost all options, skip
        wiped = any(len(domains[n]) == 0 for n in graph.get_neighbors(lid) if n in unassigned)

        if not wiped and _backtrack(data, graph, timetable, domains, unassigned, stats, start, timeout):
            return True

        stats.backtracks += 1
        timetable.remove(lid)
        unassigned.add(lid)
        _restore_domains(pruned, domains)

    return False
