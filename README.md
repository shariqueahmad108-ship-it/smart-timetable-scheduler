# smart-timetable-scheduler

Automatic timetable and exam schedule generation for colleges. Takes teachers, rooms, subjects, and constraints as input — produces a clash-free, optimized schedule.

Scheduling is NP-hard (it reduces to graph coloring). This project implements three different algorithms so you can pick the right trade-off for your input size and time budget.

![Tests](https://img.shields.io/badge/tests-47%20passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## Features

- **Three solvers** — backtracking, genetic algorithm, simulated annealing
- **Two modes** — regular timetable scheduling and exam scheduling
- **Web UI** — React frontend with live configuration editor and timetable grid
- **REST API** — FastAPI backend, easy to integrate with other tools
- **Excel export** — one sheet per student group, colour-coded by subject
- **CLI** — works without starting any server

---

## Quick start

```bash
git clone https://github.com/shariqueahmad108-ship-it/smart-timetable-scheduler.git
cd smart-timetable-scheduler
pip install -e .

# generate a timetable from the sample input
python -m scheduler examples/small_college.json

# try a different algorithm
python -m scheduler examples/small_college.json --algorithm genetic
python -m scheduler examples/small_college.json --algorithm simulated_annealing

# exam scheduling mode
python -m scheduler examples/exam_schedule.json --mode exam
```

### Running the web UI

```bash
# terminal 1 — backend
pip install -e ".[dev]"
uvicorn api.main:app --reload

# terminal 2 — frontend
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:5173` — Backend: `http://localhost:8000`

---

## Algorithms

### Backtracking + MRV

Models the problem as constraint satisfaction. Every lecture is a node in a conflict graph; two nodes are connected if they can't share a time slot (same teacher or same student group). Scheduling becomes graph coloring.

Two heuristics keep it fast in practice:

- **MRV** (Minimum Remaining Values) — always schedule the lecture with fewest valid options first
- **Forward checking** — after each assignment, prune now-invalid options from neighboring lectures. If any domain empties, backtrack immediately

Guarantees a valid solution if one exists. Best for small–medium inputs.

### Genetic Algorithm

Maintains a population of candidate timetables and evolves them over generations.

1. Initialize random population
2. Score each individual with the fitness function
3. Tournament selection → uniform crossover → random mutation
4. Elitism carries the best solutions forward
5. Stop on convergence, stagnation, or timeout

Better at optimizing soft constraints. Handles larger inputs where backtracking times out.

### Simulated Annealing

Starts from a random assignment and iteratively improves it by making random swaps. Worse moves are accepted with probability `e^(Δ/T)` — high early on so the solver can escape local optima, low later so it converges. Multiple restarts from different random starting points keep the overall best.

Good middle ground: faster than GA on many inputs, still finds high-quality solutions.

---

## Fitness scoring

Hard violations disqualify a solution; soft penalties and bonuses guide optimization.

| Criterion | Score |
|---|---|
| Teacher / room / group clash | −1000 each |
| Teacher unavailability | −1000 each |
| Teacher daily overload | −50 each |
| Group daily overload | −30 each |
| Student schedule gap | −10 each |
| Consecutive lab sessions | +10 each |
| Balanced daily load | +5 per group |

### Exam mode additions

| Criterion | Score |
|---|---|
| More than 1 exam per group per day | −1000 each |
| Back-to-back exams same day | −20 each |
| Exams spread across all days | +15 per group |

---

## Scheduling modes

### Timetable mode (default)

Regular weekly schedule with lectures, lab sessions, teacher assignments, and room allocations.

### Exam mode (`--mode exam`)

Different constraints apply:

- Max **1 exam per student group per day** (hard constraint)
- Back-to-back exams for the same group are penalized
- Exams spread evenly across available days get a bonus
- All three solvers work in exam mode — same interface, different fitness function

```bash
python -m scheduler examples/exam_schedule.json --algorithm genetic --mode exam
```

---

## CLI reference

```
python -m scheduler INPUT_FILE [options]

  --algorithm {backtracking,genetic,simulated_annealing}
                        solver to use (default: backtracking)
  --mode {timetable,exam}
                        scheduling mode (default: timetable)
  --timeout SECONDS     max solve time (default: 30)
  --teacher-view        print per-teacher schedules after solving

  GA options:
  --population N        population size (default: 100)
  --generations N       max generations (default: 500)

  SA options:
  --initial-temp F      starting temperature (default: 1000.0)
  --cooling-rate F      temperature multiplier per step (default: 0.995)
```

---

## Input format

```json
{
  "working_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
  "periods_per_day": 6,
  "teachers": [
    { "id": "T1", "name": "Dr. Sharma", "subjects": ["S1", "S2"] }
  ],
  "rooms": [
    { "id": "R1", "name": "Room 101", "capacity": 60, "type": "lecture_hall" },
    { "id": "R2", "name": "Lab A",    "capacity": 40, "type": "lab" }
  ],
  "subjects": [
    { "id": "S1", "name": "Data Structures", "code": "CS301",
      "lectures_per_week": 4, "requires_lab": true, "lab_hours": 1 }
  ],
  "student_groups": [
    { "id": "G1", "name": "CSE-3A", "strength": 55, "subjects": ["S1"] }
  ],
  "constraints": {
    "max_classes_per_day_per_teacher": 4,
    "max_classes_per_day_per_group": 5,
    "lunch_break_after_period": 3,
    "teacher_preferences": {
      "T1": { "no_classes_before": "10:00", "preferred_days": ["Monday", "Wednesday"] }
    }
  }
}
```

See [`examples/small_college.json`](examples/small_college.json) and [`examples/exam_schedule.json`](examples/exam_schedule.json) for complete examples.

---

## Project structure

```
scheduler/            core algorithm engine
  models.py           data models (Teacher, Room, Subject, Timetable, ...)
  graph.py            conflict graph construction
  backtracking.py     MRV + forward checking solver
  genetic.py          genetic algorithm solver
  annealing.py        simulated annealing solver
  exam.py             exam mode fitness adjustments
  fitness.py          scoring / fitness evaluation
  constraints.py      hard constraint validation
  parser.py           JSON input parsing
  display.py          CLI output formatting

api/                  FastAPI backend
  main.py             app setup, CORS, routing
  schemas.py          Pydantic request/response models
  routes/
    generate.py       POST /api/generate
    export.py         POST /api/export/excel

frontend/             React + Tailwind CSS
  src/
    App.jsx           main app, mode toggle, algorithm picker
    sampleData.js     built-in sample data (timetable + exam)
    components/
      InputForm.jsx   configuration editor
      TimetableGrid.jsx  schedule display grid
      TeacherView.jsx    per-teacher view
      StatsPanel.jsx     fitness stats and violations

tests/                pytest suite (47 tests)
examples/             sample JSON inputs
```

---

## Running tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

---

## Contributing

Issues and pull requests are welcome. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## License

MIT
