from __future__ import annotations

from queenquest.algorithms.base import SearchResult, Solver
from queenquest.problem import Solution


class BacktrackingSolver(Solver):
    """Depth-first backtracking solver."""

    name = "Backtracking"

    def solve(self) -> SearchResult:
        start = self._start_timer()
        solutions: list[Solution] = []
        current: Solution = [-1] * self.problem.size

        def is_safe(col: int, row: int) -> bool:
            """Return whether placing a queen at ``(col, row)`` is safe."""

            for placed_col in range(col):
                placed_row = current[placed_col]
                same_row = placed_row == row
                same_diagonal = abs(placed_row - row) == abs(placed_col - col)
                if same_row or same_diagonal:
                    return False
            return True

        def search(col: int) -> None:
            """Recursively place a queen in the requested column."""

            if col == self.problem.size:
                solutions.append(current.copy())
                return

            for row in range(self.problem.size):
                self.iterations += 1
                if is_safe(col, row):
                    current[col] = row
                    search(col + 1)
                    current[col] = -1

        search(0)
        return self._build_result(start, solutions)
