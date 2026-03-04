import argparse
import sys

from .annealing import SAConfig, solve as solve_annealing
from .backtracking import solve as solve_backtracking
from .constraints import count_hard_violations, count_soft_violations, validate_timetable
from .display import format_teacher_schedule, format_timetable_by_group, print_stats
from .fitness import evaluate
from .genetic import GAConfig, solve as solve_genetic
from .graph import build_conflict_graph
from .parser import load_input


def main():
    parser = argparse.ArgumentParser(
        description="Generate clash-free timetables using graph coloring",
    )
    parser.add_argument("input_file", help="JSON input file")
    parser.add_argument("--algorithm", choices=["backtracking", "genetic", "simulated_annealing"], default="backtracking")
    parser.add_argument("--timeout", type=float, default=30.0, help="Max solving time (seconds)")
    parser.add_argument("--teacher-view", action="store_true", help="Show teacher schedules")
    parser.add_argument("--population", type=int, default=100, help="GA population size")
    parser.add_argument("--generations", type=int, default=500, help="GA max generations")
    parser.add_argument("--initial-temp", type=float, default=1000.0, help="SA initial temperature")
    parser.add_argument("--cooling-rate", type=float, default=0.995, help="SA cooling rate")
    parser.add_argument("--mode", choices=["timetable", "exam"], default="timetable", help="Scheduling mode")
    args = parser.parse_args()

    print(f"\nLoading input from: {args.input_file}")
    try:
        data = load_input(args.input_file)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    data.mode = args.mode

    print(f"  Teachers: {len(data.teachers)}")
    print(f"  Rooms: {len(data.rooms)}")
    print(f"  Subjects: {len(data.subjects)}")
    print(f"  Student Groups: {len(data.student_groups)}")
    print(f"  Working Days: {len(data.working_days)}")
    print(f"  Periods/Day: {data.periods_per_day}")
    if args.mode == "exam":
        print("  Mode: EXAM SCHEDULING")

    print("\nBuilding conflict graph...")
    graph, lectures = build_conflict_graph(data)
    print(f"  Lectures to schedule: {len(lectures)}")
    print(f"  Conflict edges: {graph.num_edges}")

    print(f"\nSolving with {args.algorithm} (timeout: {args.timeout}s)...")

    if args.algorithm == "genetic":
        config = GAConfig(population_size=args.population, max_generations=args.generations)
        timetable, solver_stats = solve_genetic(data, graph, lectures, timeout=args.timeout, config=config)
    elif args.algorithm == "simulated_annealing":
        config = SAConfig(initial_temp=args.initial_temp, cooling_rate=args.cooling_rate)
        timetable, solver_stats = solve_annealing(data, graph, lectures, timeout=args.timeout, config=config)
    else:
        timetable, solver_stats = solve_backtracking(data, graph, lectures, timeout=args.timeout)

    if timetable is None:
        print("\nNo valid timetable found within the time limit.")
        print("Try increasing --timeout, adding more rooms, or relaxing constraints.")
        sys.exit(1)

    violations = validate_timetable(timetable, data)
    hard = count_hard_violations(violations)
    soft = count_soft_violations(violations)

    if hard > 0:
        print(f"\nWARNING: {hard} hard constraint violations!")
        for v in violations:
            if v.constraint_type == "hard":
                print(f"  - {v.description}")
    elif soft > 0:
        print(f"\nTimetable valid ({soft} soft constraint warnings)")
    else:
        print("\nPerfect timetable generated!")

    fb = evaluate(timetable, data)
    print(f"\nFitness: {fb.total}  (hard: {fb.hard_penalty}, soft: {fb.soft_penalty}, bonus: +{fb.bonus})")
    if fb.student_gaps > 0:
        print(f"  Student schedule gaps: {fb.student_gaps}")

    print(format_timetable_by_group(timetable, data))

    if args.teacher_view:
        print("\n" + "=" * 50)
        print("  TEACHER SCHEDULES")
        print("=" * 50)
        print(format_teacher_schedule(timetable, data))

    print(print_stats(timetable, data, solver_stats))


if __name__ == "__main__":
    main()
