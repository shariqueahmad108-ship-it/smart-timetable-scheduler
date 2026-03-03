# Contributing

Thanks for wanting to contribute. Here's how to get started.

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/smart-timetable-scheduler.git
cd smart-timetable-scheduler

# backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -e ".[dev]"

# frontend
cd frontend
npm install
cd ..

# verify
pytest tests/ -v
```

## Making changes

1. Fork the repo and create a branch from `main`
2. Make your changes
3. Run tests: `pytest tests/ -v`
4. If you changed frontend code: `cd frontend && npm run build`
5. Open a pull request

## What to work on

Check the [issues](https://github.com/YOUR_USERNAME/smart-timetable-scheduler/issues) page. Issues labeled `good first issue` are meant for newcomers.

Some ideas if nothing's listed:

- Add a new constraint type (e.g. "no back-to-back classes for a teacher")
- Improve the genetic algorithm (try different selection/crossover strategies)
- Add CSV import/export
- Write more test cases for edge conditions
- Improve the UI (dark mode, mobile layout, drag-to-swap slots)

## Code style

- Python: no strict formatter enforced, but keep it readable. Use type hints where they help.
- React: functional components, hooks only. Tailwind for styling.
- Tests go in `tests/`. Name them `test_<module>.py`.
- Keep commits focused. One logical change per commit.

## Reporting bugs

Open an issue with:
- What you did
- What you expected
- What actually happened
- Input data if relevant (paste the JSON or attach the file)

## Questions?

Open an issue with the `question` label.
