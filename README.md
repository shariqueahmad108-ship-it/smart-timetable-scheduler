# smart-timetable-scheduler

Automatic timetable generation for colleges. Takes teachers, rooms, subjects, and constraints as input — produces a clash-free, optimized timetable.

This is an NP-hard problem (reducible to graph coloring). The solver implements two algorithms:

- **Backtracking with MRV heuristic** — models lectures as graph nodes and time slots as colors. Uses Minimum Remaining Values to pick the most constrained variable first, with forward checking to prune the search space early.
- **Genetic algorithm** — evolves a population of candidate timetables through selection, crossover, and mutation. Optimizes for soft constraints like teacher preferences, minimal student gaps, and balanced daily load.

## Quick start

```bash
# clone and install
git clone https://github.com/YOUR_USERNAME/smart-timetable-scheduler.git
cd smart-timetable-scheduler
pip install -e .

# generate a timetable from the command line
python -m scheduler examples/small_college.json

# try the genetic algorithm
python -m scheduler examples/small_college.json --algorithm genetic

# run with the web UI
pip install -e ".[dev]"
cd frontend && npm install && npm run build && cd ..
uvicorn api.main:app --port 8000
# open http://localhost:8000
```

## How it works

### Input

A JSON file describing teachers, rooms, subjects, student groups, and constraints. See [`examples/small_college.json`](examples/small_college.json) for the full format.

### Conflict graph

Every lecture that needs to happen during the week becomes a node. Two lectures get an edge between them if they can't happen at the same time — because they share a teacher or a student group. This turns scheduling into a graph coloring problem: assign a "color" (time slot + room) to every node such that no two connected nodes share a color.

### Backtracking solver

Standard CSP backtracking with two key optimizations:

- **MRV** (Minimum Remaining Values): always schedule the lecture with the fewest valid options first. Ties broken by constraint degree.
- **Forward checking**: after each assignment, prune now-invalid options from neighboring lectures' domains. If any domain empties, backtrack immediately.

### Genetic algorithm

For larger inputs or when soft constraint quality matters:

1. Initialize a random population of timetables
2. Score each using a fitness function (hard penalties, soft penalties, bonuses)
3. Tournament selection → crossover → mutation
4. Elitism keeps the best solutions alive
5. Repeat until convergence or timeout

### Fitness scoring

| Criterion | Weight |
|---|---|
| Teacher/room/group clash | -1000 each |
| Teacher unavailability | -1000 each |
| Teacher daily overload | -50 each |
| Group daily overload | -30 each |
| Student schedule gap | -10 each |
| Consecutive lab bonus | +10 each |
| Balanced daily load | +5 per group |

## Project structure

```
scheduler/          core algorithm engine
  models.py         data models
  graph.py          conflict graph construction
  backtracking.py   MRV + forward checking solver
  genetic.py        genetic algorithm solver
  fitness.py        scoring function
  constraints.py    validation
  parser.py         JSON input parsing
  display.py        CLI output formatting

api/                FastAPI backend
  main.py           app entry point
  schemas.py        request/response models
  routes/
    generate.py     POST /api/generate
    export.py       POST /api/export/excel

frontend/           React + Tailwind CSS
  src/
    App.jsx
    components/
      InputForm.jsx
      TimetableGrid.jsx
      TeacherView.jsx
      StatsPanel.jsx

tests/              pytest test suite
examples/           sample input files
```

## Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## CLI options

```
python -m scheduler INPUT_FILE [options]

  --algorithm {backtracking,genetic}   default: backtracking
  --timeout SECONDS                    default: 30
  --teacher-view                       print per-teacher schedules
  --population N                       GA population size (default: 100)
  --generations N                      GA max generations (default: 500)
```

## License

MIT
