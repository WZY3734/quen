from __future__ import annotations

import random

from queenquest.algorithms.base import SearchResult, Solver
from queenquest.problem import Solution


class GeneticSolver(Solver):
    """Genetic algorithm solver."""

    name = "GeneticAlgorithm"

    def __init__(
        self,
        problem,
        population_size: int = 100,
        generations: int = 1_000,
        mutation_rate: float = 0.2,
    ) -> None:
        super().__init__(problem)
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate

    def solve(self) -> SearchResult:
        start = self._start_timer()
        population = [self.problem.random_solution() for _ in range(self.population_size)]
        found: list[Solution] = []
        seen: set[tuple[int, ...]] = set()

        for _ in range(self.generations):
            self.iterations += 1

            for individual in population:
                if self.problem.is_valid(individual):
                    key = tuple(individual)
                    if key not in seen:
                        seen.add(key)
                        found.append(individual.copy())

            if found:
                break

            population = self._next_generation(population)

        return self._build_result(
            start,
            found,
            {
                "population_size": self.population_size,
                "generations": self.generations,
                "mutation_rate": self.mutation_rate,
            },
        )

    def _next_generation(self, population: list[Solution]) -> list[Solution]:
        """Build the next population from the current one."""

        ranked = sorted(population, key=self.problem.fitness, reverse=True)
        elite_count = max(2, self.population_size // 10)
        next_population = [item.copy() for item in ranked[:elite_count]]

        while len(next_population) < self.population_size:
            parent_a = self._tournament_select(population)
            parent_b = self._tournament_select(population)
            child = self._crossover(parent_a, parent_b)
            self._mutate(child)
            next_population.append(child)

        return next_population

    def _tournament_select(self, population: list[Solution]) -> Solution:
        """Select one parent with tournament selection."""

        candidates = random.sample(population, k=min(5, len(population)))
        return max(candidates, key=self.problem.fitness)

    def _crossover(self, parent_a: Solution, parent_b: Solution) -> Solution:
        """Return one child using single-point crossover."""

        split = random.randrange(1, self.problem.size)
        return parent_a[:split] + parent_b[split:]

    def _mutate(self, solution: Solution) -> None:
        """Mutate a board in place."""

        for col in range(self.problem.size):
            if random.random() < self.mutation_rate:
                solution[col] = random.randrange(self.problem.size)
