# QueenQuest

QueenQuest is a small, beginner-friendly Python application for exploring the
N-Queens problem. It includes deterministic solvers, heuristic solvers, a
command-line interface, a desktop GUI, replayable search traces, and basic test
coverage.

The project is designed to be useful as a course assignment, a classroom demo,
or a compact open-source example of how to structure a Python application.

## Features

- Interactive desktop application built with Tkinter and Matplotlib
- Algorithm selection from Backtracking, Brute Force, Hill Climbing, Simulated Annealing, and Genetic Algorithm
- Adjustable solver parameters such as board size, speed, restarts, population size, mutation rate, temperature, and random seed
- Replay controls for search traces: play, pause, step forward, step backward, jump to start/end, and scrub through the timeline
- Command-line solver for quick runs and JSON output
- Static board visualization for solved boards
- Unit tests for the core problem model and backtracking solver

## Screenshot

The GUI can be launched locally with:

```bash
python main.py --gui
```

It shows the board on the left, the current algorithm state on the right, and
timeline controls underneath the canvas.

## Installation

Create a virtual environment and install the project dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For editable local development:

```bash
pip install -e .
```

## Usage

Launch the full interactive application:

```bash
python main.py --gui
```

Run the default 8-queens backtracking solver:

```bash
python main.py
```

Choose a solver:

```bash
python main.py --algorithm brute-force
python main.py --algorithm backtracking
python main.py --algorithm hill-climbing
python main.py --algorithm simulated-annealing
python main.py --algorithm genetic
```

Change the board size:

```bash
python main.py --size 10 --algorithm backtracking
```

Show the first solution in a Matplotlib window:

```bash
python main.py --algorithm backtracking --show
```

Run the legacy Matplotlib backtracking animation:

```bash
python main.py --animate --interval 120
```

Validate saved solution files:

```bash
python verify_solutions.py
```

Run tests:

```bash
python -m unittest discover -s tests
```

## Project Structure

```text
.
├── main.py
├── queenquest/
│   ├── app.py                 # Tkinter desktop application
│   ├── cli.py                 # Command-line interface
│   ├── problem.py             # Core N-Queens model
│   ├── tracing.py             # Replayable algorithm traces
│   ├── visualizer.py          # Static Matplotlib board rendering
│   ├── animation.py           # Legacy Matplotlib animation entry point
│   └── algorithms/
│       ├── backtracking.py
│       ├── brute_force.py
│       ├── genetic.py
│       ├── hill_climbing.py
│       └── simulated_annealing.py
├── tests/
├── pyproject.toml
├── requirements.txt
├── CONTRIBUTING.md
├── CHANGELOG.md
└── LICENSE
```

## Board Representation

QueenQuest represents a board as a list of row positions. The list index is the
column, and the value is the row:

```python
[0, 4, 7, 5, 2, 6, 1, 3]
```

This means:

- column 0 has a queen on row 0
- column 1 has a queen on row 4
- column 2 has a queen on row 7

The representation guarantees one queen per column. The solver only needs to
check row conflicts and diagonal conflicts.

## Development Notes

The core solvers return final results through `SearchResult`. The GUI uses
`SearchTrace` from `queenquest.tracing`, which is intentionally separate from
the solver classes so playback controls can move forward and backward through a
precomputed trace.

This separation keeps the command-line solver simple while giving the
interactive application a stable timeline model.

## License

QueenQuest is released under the MIT License.
