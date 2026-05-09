# Contributing

Thanks for your interest in QueenQuest. This project is intentionally small and
approachable, so contributions should keep the code easy to read.

## Development Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Checks

Run the test suite before submitting changes:

```bash
python -m unittest discover -s tests
```

You can also run a quick CLI smoke test:

```bash
python main.py --algorithm backtracking --no-save
```

## Style

- Keep comments concise and useful.
- Prefer clear names over clever abstractions.
- Keep GUI behavior backed by trace data rather than one-off UI state.
- Add tests when changing the problem model or deterministic solvers.
