from __future__ import annotations

import os
import tempfile
from pathlib import Path

_matplotlib_cache = Path(tempfile.gettempdir()) / "queenquest-matplotlib"
_matplotlib_cache.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_matplotlib_cache))
os.environ.setdefault("XDG_CACHE_HOME", str(_matplotlib_cache))

import matplotlib.pyplot as plt

from queenquest.algorithms.base import SearchResult
from queenquest.problem import NQueensProblem, Solution


def show_solution(problem: NQueensProblem, solution: Solution, title: str = "") -> None:
    """Display a complete N-Queens solution in a Matplotlib window."""

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_title(title or f"{problem.size}-Queens")
    ax.set_xlim(0, problem.size)
    ax.set_ylim(0, problem.size)
    ax.set_aspect("equal")
    ax.invert_yaxis()
    ax.set_xticks([])
    ax.set_yticks([])

    for row in range(problem.size):
        for col in range(problem.size):
            color = "#f2d8a7" if (row + col) % 2 == 0 else "#8f5f3c"
            square = plt.Rectangle((col, row), 1, 1, facecolor=color)
            ax.add_patch(square)

    for col, row in enumerate(solution):
        ax.text(
            col + 0.5,
            row + 0.5,
            "Q",
            ha="center",
            va="center",
            fontsize=24,
            color="#1f2937",
            fontweight="bold",
        )

    plt.show()


def show_first_solution(problem: NQueensProblem, result: SearchResult) -> None:
    """Display the first solution from a solver result."""

    if not result.solutions:
        print("No solution to display.")
        return

    show_solution(problem, result.solutions[0], f"{result.algorithm} first solution")
