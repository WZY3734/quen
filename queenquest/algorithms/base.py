from __future__ import annotations

import time
from dataclasses import dataclass, field

from queenquest.problem import NQueensProblem, Solution


@dataclass
class SearchResult:
    """Normalized result returned by every solver."""

    algorithm: str
    board_size: int
    solutions: list[Solution]
    iterations: int
    elapsed_seconds: float
    parameters: dict[str, float | int | str] = field(default_factory=dict)

    @property
    def total_solutions(self) -> int:
        return len(self.solutions)


class Solver:
    """Base class for solver implementations."""

    name = "Solver"

    def __init__(self, problem: NQueensProblem) -> None:
        self.problem = problem
        self.iterations = 0

    def solve(self) -> SearchResult:
        raise NotImplementedError

    def _start_timer(self) -> float:
        self.iterations = 0
        return time.perf_counter()

    def _build_result(
        self,
        start_time: float,
        solutions: list[Solution],
        parameters: dict[str, float | int | str] | None = None,
    ) -> SearchResult:
        return SearchResult(
            algorithm=self.name,
            board_size=self.problem.size,
            solutions=solutions,
            iterations=self.iterations,
            elapsed_seconds=time.perf_counter() - start_time,
            parameters=parameters or {},
        )
