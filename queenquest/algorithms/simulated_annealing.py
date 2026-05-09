from __future__ import annotations

import math
import random

from queenquest.algorithms.base import SearchResult, Solver
from queenquest.problem import Solution


class SimulatedAnnealingSolver(Solver):
    """Simulated annealing solver."""

    name = "SimulatedAnnealing"

    def __init__(
        self,
        problem,
        max_steps: int = 20_000,
        initial_temperature: float = 5.0,
        cooling_rate: float = 0.995,
    ) -> None:
        super().__init__(problem)
        self.max_steps = max_steps
        self.initial_temperature = initial_temperature
        self.cooling_rate = cooling_rate

    def solve(self) -> SearchResult:
        start = self._start_timer()
        solution = self.problem.random_solution()
        found: list[Solution] = []

        temperature = self.initial_temperature
        current_conflicts = self.problem.count_conflicts(solution)

        for _ in range(self.max_steps):
            self.iterations += 1

            if current_conflicts == 0:
                found.append(solution.copy())
                break

            neighbor = self._random_neighbor(solution)
            neighbor_conflicts = self.problem.count_conflicts(neighbor)

            if self._should_accept(current_conflicts, neighbor_conflicts, temperature):
                solution = neighbor
                current_conflicts = neighbor_conflicts

            temperature *= self.cooling_rate
            if temperature < 0.0001:
                temperature = self.initial_temperature

        return self._build_result(
            start,
            found,
            {
                "max_steps": self.max_steps,
                "initial_temperature": self.initial_temperature,
                "cooling_rate": self.cooling_rate,
            },
        )

    def _random_neighbor(self, solution: Solution) -> Solution:
        """Return a board produced by moving one random queen."""

        neighbor = solution.copy()
        col = random.randrange(self.problem.size)
        neighbor[col] = random.randrange(self.problem.size)
        return neighbor

    def _should_accept(
        self,
        current_conflicts: int,
        neighbor_conflicts: int,
        temperature: float,
    ) -> bool:
        """Return whether the candidate move should be accepted."""

        if neighbor_conflicts <= current_conflicts:
            return True

        delta = current_conflicts - neighbor_conflicts
        probability = math.exp(delta / temperature)
        return random.random() < probability
