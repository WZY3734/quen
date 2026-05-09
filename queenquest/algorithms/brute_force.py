from __future__ import annotations

from itertools import permutations

from queenquest.algorithms.base import SearchResult, Solver


class BruteForceSolver(Solver):
    """Permutation-based exhaustive solver."""

    name = "BruteForce"

    def solve(self) -> SearchResult:
        start = self._start_timer()
        solutions = []

        for candidate in permutations(range(self.problem.size)):
            self.iterations += 1
            solution = list(candidate)
            if self.problem.is_valid(solution):
                solutions.append(solution)

        return self._build_result(start, solutions)
