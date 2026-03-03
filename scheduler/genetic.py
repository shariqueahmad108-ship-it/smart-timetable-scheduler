"""
Genetic algorithm solver.

Explores many candidate timetables in parallel, evolving them toward
better solutions through selection, crossover, and mutation. Unlike
backtracking, this can optimize for soft constraints like teacher
preferences, minimal gaps, and balanced daily load.
"""
import random
import time
from dataclasses import dataclass

from .fitness import FitnessBreakdown, evaluate
from .graph import ConflictGraph
from .models import Lecture, ScheduledClass, TimeSlot, Timetable, TimetableInput


@dataclass
class GAConfig:
    population_size: int = 100
    max_generations: int = 500
    mutation_rate: float = 0.03
    crossover_rate: float = 0.8
    tournament_size: int = 5
    elitism_count: int = 2
    stagnation_limit: int = 50


@dataclass
class GAStats:
    generations_run: int = 0
    best_fitness: int = 0
    best_generation: int = 0
    time_seconds: float = 0.0
    solution_found: bool = False
    population_size: int = 0
    nodes_explored: int = 0
    backtracks: int = 0  # unused, kept for API compat


@dataclass
class Individual:
    genes: dict[str, tuple[TimeSlot, str]]  # lecture_id -> (slot, room_id)
    fitness: FitnessBreakdown | None = None

    @property
    def score(self) -> int:
        return self.fitness.total if self.fitness else -999999


def solve(
    data: TimetableInput,
    graph: ConflictGraph,
    lectures: list[Lecture],
    timeout: float = 30.0,
    config: GAConfig | None = None,
) -> tuple[Timetable | None, GAStats]:
    if config is None:
        config = GAConfig()

    stats = GAStats(population_size=config.population_size)
    start = time.time()
    all_slots = data.get_all_time_slots()

    # precompute valid options per lecture
    domains: dict[str, list[tuple[TimeSlot, str]]] = {}
    for lec in lectures:
        rooms = data.get_suitable_rooms(lec)
        domains[lec.id] = [(s, r.id) for s in all_slots for r in rooms]

    if any(len(d) == 0 for d in domains.values()):
        stats.time_seconds = time.time() - start
        return None, stats

    population = [_random_individual(lectures, domains) for _ in range(config.population_size)]

    for ind in population:
        ind.fitness = evaluate(_to_timetable(ind.genes, graph), data)
        stats.nodes_explored += 1

    best_ever = max(population, key=lambda i: i.score)
    stats.best_fitness = best_ever.score
    stagnation = 0

    for gen in range(1, config.max_generations + 1):
        if time.time() - start > timeout:
            break

        population.sort(key=lambda i: i.score, reverse=True)
        new_pop: list[Individual] = population[:config.elitism_count]

        while len(new_pop) < config.population_size:
            p1 = _tournament(population, config.tournament_size)
            p2 = _tournament(population, config.tournament_size)

            if random.random() < config.crossover_rate:
                g1, g2 = _crossover(p1.genes, p2.genes, lectures)
            else:
                g1, g2 = dict(p1.genes), dict(p2.genes)

            _mutate(g1, lectures, domains, config.mutation_rate)
            _mutate(g2, lectures, domains, config.mutation_rate)

            c1 = Individual(genes=g1)
            c1.fitness = evaluate(_to_timetable(g1, graph), data)
            stats.nodes_explored += 1
            new_pop.append(c1)

            if len(new_pop) < config.population_size:
                c2 = Individual(genes=g2)
                c2.fitness = evaluate(_to_timetable(g2, graph), data)
                stats.nodes_explored += 1
                new_pop.append(c2)

        population = new_pop

        gen_best = max(population, key=lambda i: i.score)
        if gen_best.score > best_ever.score:
            best_ever = gen_best
            stats.best_fitness = best_ever.score
            stats.best_generation = gen
            stagnation = 0
        else:
            stagnation += 1

        stats.generations_run = gen

        # stop early on a perfect solution
        if best_ever.fitness and best_ever.fitness.hard_penalty == 0 and best_ever.fitness.soft_penalty == 0:
            break
        if stagnation >= config.stagnation_limit:
            break

    stats.time_seconds = time.time() - start

    if best_ever.fitness:
        stats.solution_found = True
        return _to_timetable(best_ever.genes, graph), stats

    return None, stats


def _random_individual(
    lectures: list[Lecture], domains: dict[str, list[tuple[TimeSlot, str]]]
) -> Individual:
    genes = {lec.id: random.choice(domains[lec.id]) for lec in lectures}
    return Individual(genes=genes)


def _tournament(population: list[Individual], size: int) -> Individual:
    contestants = random.sample(population, min(size, len(population)))
    return max(contestants, key=lambda i: i.score)


def _crossover(
    p1: dict[str, tuple[TimeSlot, str]],
    p2: dict[str, tuple[TimeSlot, str]],
    lectures: list[Lecture],
) -> tuple[dict[str, tuple[TimeSlot, str]], dict[str, tuple[TimeSlot, str]]]:
    c1, c2 = {}, {}
    for lec in lectures:
        if random.random() < 0.5:
            c1[lec.id], c2[lec.id] = p1[lec.id], p2[lec.id]
        else:
            c1[lec.id], c2[lec.id] = p2[lec.id], p1[lec.id]
    return c1, c2


def _mutate(
    genes: dict[str, tuple[TimeSlot, str]],
    lectures: list[Lecture],
    domains: dict[str, list[tuple[TimeSlot, str]]],
    rate: float,
):
    for lec in lectures:
        if random.random() < rate:
            genes[lec.id] = random.choice(domains[lec.id])


def _to_timetable(genes: dict[str, tuple[TimeSlot, str]], graph: ConflictGraph) -> Timetable:
    tt = Timetable()
    for lid, (slot, room_id) in genes.items():
        tt.add(lid, ScheduledClass(lecture=graph.lectures[lid], time_slot=slot, room_id=room_id))
    return tt
