from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

_matplotlib_cache = Path(tempfile.gettempdir()) / "queenquest-matplotlib"
_matplotlib_cache.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_matplotlib_cache))
os.environ.setdefault("XDG_CACHE_HOME", str(_matplotlib_cache))

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle

from queenquest.problem import NQueensProblem, Solution


@dataclass
class SearchFrame:
    """One frame in the legacy Matplotlib backtracking animation."""

    board: Solution
    active_col: int | None
    active_row: int | None
    conflicts: list[tuple[int, int]]
    message: str
    attempts: int
    backtracks: int
    solutions_found: int
    is_solution: bool = False


class BacktrackingAnimator:
    """Legacy Matplotlib animation for the backtracking search."""

    def __init__(self, problem: NQueensProblem, interval: int = 280) -> None:
        self.problem = problem
        self.interval = interval
        self.frames = list(self._build_frames())

    def show(self) -> None:
        """Open a Matplotlib window and play the animation."""

        fig = plt.figure(figsize=(10, 6))
        grid = fig.add_gridspec(1, 2, width_ratios=[3, 2])
        board_ax = fig.add_subplot(grid[0, 0])
        info_ax = fig.add_subplot(grid[0, 1])

        def update(frame_index: int) -> None:
            frame = self.frames[frame_index]
            self._draw_board(board_ax, frame)
            self._draw_info(info_ax, frame, frame_index)

        animation = FuncAnimation(
            fig,
            update,
            frames=len(self.frames),
            interval=self.interval,
            repeat=False,
            cache_frame_data=False,
        )

        update(0)
        plt.tight_layout()
        self._animation = animation
        fig._queenquest_animation = animation
        plt.show()

    def _build_frames(self) -> Iterable[SearchFrame]:
        board = [-1] * self.problem.size
        attempts = 0
        backtracks = 0
        solutions_found = 0

        yield SearchFrame(
            board=board.copy(),
            active_col=None,
            active_row=None,
            conflicts=[],
            message="Start: place one queen in each column.",
            attempts=attempts,
            backtracks=backtracks,
            solutions_found=solutions_found,
        )

        def search(col: int) -> Iterable[SearchFrame]:
            nonlocal attempts, backtracks, solutions_found

            if col == self.problem.size:
                solutions_found += 1
                yield SearchFrame(
                    board=board.copy(),
                    active_col=None,
                    active_row=None,
                    conflicts=[],
                    message="Solution found. No queens attack each other.",
                    attempts=attempts,
                    backtracks=backtracks,
                    solutions_found=solutions_found,
                    is_solution=True,
                )
                return

            for row in range(self.problem.size):
                attempts += 1
                conflicts = self._find_conflicts(board, col, row)

                yield SearchFrame(
                    board=board.copy(),
                    active_col=col,
                    active_row=row,
                    conflicts=conflicts,
                    message=f"Try column {col}, row {row}.",
                    attempts=attempts,
                    backtracks=backtracks,
                    solutions_found=solutions_found,
                )

                if conflicts:
                    yield SearchFrame(
                        board=board.copy(),
                        active_col=col,
                        active_row=row,
                        conflicts=conflicts,
                        message="Conflict detected, try the next row.",
                        attempts=attempts,
                        backtracks=backtracks,
                        solutions_found=solutions_found,
                    )
                    continue

                board[col] = row
                yield SearchFrame(
                    board=board.copy(),
                    active_col=col,
                    active_row=row,
                    conflicts=[],
                    message="Safe position, place the queen.",
                    attempts=attempts,
                    backtracks=backtracks,
                    solutions_found=solutions_found,
                )

                yield from search(col + 1)

                if solutions_found:
                    return

                board[col] = -1
                backtracks += 1
                yield SearchFrame(
                    board=board.copy(),
                    active_col=col,
                    active_row=row,
                    conflicts=[],
                    message="No row worked later, backtrack.",
                    attempts=attempts,
                    backtracks=backtracks,
                    solutions_found=solutions_found,
                )

        yield from search(0)

    def _find_conflicts(
        self,
        board: Solution,
        col: int,
        row: int,
    ) -> list[tuple[int, int]]:
        conflicts: list[tuple[int, int]] = []

        for placed_col, placed_row in enumerate(board):
            if placed_row == -1:
                continue

            same_row = placed_row == row
            same_diagonal = abs(placed_row - row) == abs(placed_col - col)

            if same_row or same_diagonal:
                conflicts.append((placed_col, placed_row))

        return conflicts

    def _draw_board(self, ax, frame: SearchFrame) -> None:
        ax.clear()
        ax.set_title("Backtracking Search", fontsize=14)
        ax.set_xlim(0, self.problem.size)
        ax.set_ylim(0, self.problem.size)
        ax.set_aspect("equal")
        ax.invert_yaxis()
        ax.set_xticks([])
        ax.set_yticks([])

        for row in range(self.problem.size):
            for col in range(self.problem.size):
                color = "#f3d9a4" if (row + col) % 2 == 0 else "#876445"
                ax.add_patch(Rectangle((col, row), 1, 1, facecolor=color, edgecolor="#2f241d"))

        if frame.active_col is not None and frame.active_row is not None:
            ax.add_patch(
                Rectangle(
                    (frame.active_col, frame.active_row),
                    1,
                    1,
                    facecolor="#60a5fa",
                    alpha=0.55,
                    edgecolor="#1d4ed8",
                    linewidth=2,
                )
            )

        for col, row in frame.conflicts:
            ax.add_patch(
                Rectangle(
                    (col, row),
                    1,
                    1,
                    facecolor="#ef4444",
                    alpha=0.6,
                    edgecolor="#7f1d1d",
                    linewidth=2,
                )
            )

        for col, row in enumerate(frame.board):
            if row == -1:
                continue

            color = "#047857" if frame.is_solution else "#111827"
            ax.text(
                col + 0.5,
                row + 0.5,
                "Q",
                ha="center",
                va="center",
                fontsize=26,
                color=color,
                fontweight="bold",
            )

    def _draw_info(self, ax, frame: SearchFrame, frame_index: int) -> None:
        ax.clear()
        ax.axis("off")

        lines = [
            "N-Queens Backtracking",
            "",
            frame.message,
            "",
            f"Frame: {frame_index + 1}/{len(self.frames)}",
            f"Board size: {self.problem.size} x {self.problem.size}",
            f"Attempts: {frame.attempts}",
            f"Backtracks: {frame.backtracks}",
            f"Solutions found: {frame.solutions_found}",
            "",
            "Legend:",
            "Blue = current try",
            "Red = conflicting queen",
            "Q = placed queen",
        ]

        if frame.is_solution:
            lines.extend(["", "First solution:", str(frame.board)])

        ax.text(
            0.02,
            0.98,
            "\n".join(lines),
            va="top",
            fontsize=12,
            family="monospace",
            bbox={"facecolor": "#f9fafb", "edgecolor": "#d1d5db", "boxstyle": "round,pad=0.6"},
        )


def show_backtracking_animation(size: int = 8, interval: int = 280) -> None:
    """Open the legacy backtracking animation."""

    problem = NQueensProblem(size)
    BacktrackingAnimator(problem, interval=interval).show()
