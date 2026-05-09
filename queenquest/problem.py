from __future__ import annotations

import random
from dataclasses import dataclass


Solution = list[int]


@dataclass(frozen=True)
class NQueensProblem:
    """Core N-Queens rules and scoring helpers.

    A solution is represented as a list where the index is the column and the
    value is the row. For example, ``[1, 3, 0, 2]`` means the queen in column 0
    is placed on row 1, the queen in column 1 is placed on row 3, and so on.
    """

    size: int = 8

    def __post_init__(self) -> None:
        if self.size < 1:
            raise ValueError("Board size must be greater than 0")

    def random_solution(self) -> Solution:
        """Return a random complete board configuration."""

        return [random.randrange(self.size) for _ in range(self.size)]

    def count_conflicts(self, solution: Solution) -> int:
        """Count the number of attacking queen pairs."""

        self._check_solution_shape(solution)
        conflicts = 0

        for left_col in range(self.size):
            for right_col in range(left_col + 1, self.size):
                left_row = solution[left_col]
                right_row = solution[right_col]

                same_row = left_row == right_row
                same_diagonal = abs(left_row - right_row) == abs(left_col - right_col)

                if same_row or same_diagonal:
                    conflicts += 1

        return conflicts

    def is_valid(self, solution: Solution) -> bool:
        """Return whether a complete board configuration is a valid solution."""

        return self.count_conflicts(solution) == 0

    def fitness(self, solution: Solution) -> float:
        """Convert conflicts into a score in ``(0, 1]``."""

        return 1.0 / (1.0 + self.count_conflicts(solution))

    def render_text(self, solution: Solution) -> str:
        """Render a board as plain text."""

        self._check_solution_shape(solution)
        rows: list[str] = []

        for row in range(self.size):
            cells = []
            for col in range(self.size):
                cells.append("Q" if solution[col] == row else ".")
            rows.append(" ".join(cells))

        return "\n".join(rows)

    def _check_solution_shape(self, solution: Solution) -> None:
        """Validate that a complete solution fits this board."""

        if len(solution) != self.size:
            raise ValueError(f"Solution length must be {self.size}")

        for row in solution:
            if row < 0 or row >= self.size:
                raise ValueError(f"Row {row} is outside the board range 0..{self.size - 1}")
