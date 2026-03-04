"""
Simulated annealing solver.

Starts from a random assignment and iteratively improves it by making
random swaps.  Worse solutions are accepted with probability e^(delta/T)
where T (temperature) decreases over time, allowing the solver to escape
local optima early on and converge to a good solution later.

Multiple restarts from different random starts keep the overall best.
"""
import math
import random
import time
from dataclasses import dataclass

from .fitness import FitnessBreakdown, evaluate
from .graph import ConflictGraph
from .models import Lecture, ScheduledClass, TimeSlot, Timetable, TimetableInput


@dataclass
class SAConfig:
    initial_temp: float = 1000.0
    cooling_rate: float = 0.995
    min_temp: float = 0.1
    max_iterations: int = 50000
    restarts: int = 3


@dataclass
class SAStats:
    iterations_run: int = 0
    best_fitness: int = 0
    restarts_used: int = 0
    time_seconds: float = 0.0
    solution_found: bool = False
    nodes_explored: int = 0
    backtracks: int = 0  # unused, kept for API compat


def solve(
    data: TimetableInput,
    graph: ConflictGraph,
    lectures: list[Lecture],
    timeout: float = 30.0,
    config: SAConfig | None = None,
) -> tuple[Timetable | None, SAStats]:
    if config is None:
        config = SAConfig()

    stats = SAStats()
    start = time.time()

    # precompute valid (slot, room) options per lecture
    all_slots = data.get_all_time_slots()
    domains: dict[str, list[tuple[TimeSlot, str]]] = {}
    for lec in lectures:
        rooms = data.get_suitable_rooms(lec)
        domains[lec.id] = [(s, r.id) for s in all_slots for r in rooms]

    if any(len(d) == 0 for d in domains.values()):
        stats.time_seconds = time.time() - start
        return None, stats

    best_genes: dict[str, tuple[TimeSlot, str]] | None = None
    best_score = -999999

    for restart in range(config.restarts):
        if time.time() - start > timeout:
            break

        stats.restarts_used = restart + 1

        # random initial solution
        genes = {lec.id: random.choice(domains[lec.id]) for lec in lectures}
        current_score = _score(genes, graph, data)
        stats.nodes_explored += 1

        if current_score > best_score:
            best_score = current_score
            best_genes = dict(genes)

        temp = config.initial_temp

        for iteration in range(config.max_iterations):
            if time.time() - start > timeout:
                break
            if temp < config.min_temp:
                break

            stats.iterations_run += 1

            # pick a random lecture and swap to a random valid assignment
            lec = random.choice(lectures)
            old_val = genes[lec.id]
            new_val = random.choice(domains[lec.id])

            genes[lec.id] = new_val
            new_score = _score(genes, graph, data)
            stats.nodes_explored += 1

            delta = new_score - current_score

            if delta > 0 or random.random() < math.exp(delta / temp):
                # accept the move
                current_score = new_score
            else:
                # reject — revert
                genes[lec.id] = old_val

            if current_score > best_score:
                best_score = current_score
                best_genes = dict(genes)

            temp *= config.cooling_rate

            # early exit on perfect solution
            if best_score >= 0:
                fb = evaluate(_to_timetable(best_genes, graph), data)
                if fb.hard_penalty == 0 and fb.soft_penalty == 0:
                    break

    stats.time_seconds = time.time() - start
    stats.best_fitness = best_score

    if best_genes is not None:
        stats.solution_found = True
        return _to_timetable(best_genes, graph), stats

    return None, stats


def _score(
    genes: dict[str, tuple[TimeSlot, str]],
    graph: ConflictGraph,
    data: TimetableInput,
) -> int:
    tt = _to_timetable(genes, graph)
    fb = evaluate(tt, data)
    return fb.total


def _to_timetable(
    genes: dict[str, tuple[TimeSlot, str]], graph: ConflictGraph
) -> Timetable:
    tt = Timetable()
    for lid, (slot, room_id) in genes.items():
        tt.add(lid, ScheduledClass(lecture=graph.lectures[lid], time_slot=slot, room_id=room_id))
    return tt
