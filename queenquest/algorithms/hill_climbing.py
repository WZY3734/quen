from __future__ import annotations

import random

from queenquest.algorithms.base import SearchResult, Solver
from queenquest.problem import Solution


class HillClimbingSolver(Solver):
    """Local-search solver with random restarts."""

    name = "HillClimbing"

    def __init__(
        self,
        problem,
        max_steps: int = 5_000,
        restarts: int = 30,
    ) -> None:
        super().__init__(problem)
        self.max_steps = max_steps
        self.restarts = restarts

    def solve(self) -> SearchResult:
        start = self._start_timer()
        found: list[Solution] = []
        seen: set[tuple[int, ...]] = set()

        for _ in range(self.restarts):
            current = self.problem.random_solution()
            current_score = self.problem.fitness(current)

            for _ in range(self.max_steps):
                self.iterations += 1

                if self.problem.is_valid(current):
                    key = tuple(current)
                    if key not in seen:
                        seen.add(key)
                        found.append(current.copy())
                    break

                neighbor = self._best_neighbor(current)
                neighbor_score = self.problem.fitness(neighbor)

                if neighbor_score <= current_score:
                    break

                current = neighbor
                current_score = neighbor_score

        return self._build_result(
            start,
            found,
            {"max_steps": self.max_steps, "restarts": self.restarts},
        )

    def _best_neighbor(self, solution: Solution) -> Solution:
        """Return the best board reachable by moving one queen."""

        best = solution.copy()
        best_score = self.problem.fitness(best)

        for col in range(self.problem.size):
            original_row = solution[col]
            for row in range(self.problem.size):
                if row == original_row:
                    continue

                candidate = solution.copy()
                candidate[col] = row
                score = self.problem.fitness(candidate)

                if score > best_score:
                    best = candidate
                    best_score = score

        return best
