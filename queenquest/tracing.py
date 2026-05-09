from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from itertools import permutations

from queenquest.problem import NQueensProblem, Solution


ALGORITHMS = (
    "Backtracking",
    "Brute Force",
    "Hill Climbing",
    "Simulated Annealing",
    "Genetic Algorithm",
)


@dataclass(frozen=True)
class TraceSettings:
    """User-adjustable settings used when building a trace."""

    board_size: int = 8
    algorithm: str = "Backtracking"
    max_steps: int = 2_000
    restarts: int = 20
    population_size: int = 80
    generations: int = 300
    mutation_rate: float = 0.2
    initial_temperature: float = 5.0
    cooling_rate: float = 0.995
    seed: int | None = 7
    stop_at_first_solution: bool = True
    max_frames: int = 8_000


@dataclass
class TraceFrame:
    """A single visual step in an algorithm run."""

    board: Solution
    message: str
    phase: str
    attempts: int = 0
    conflicts: list[tuple[int, int]] = field(default_factory=list)
    active: tuple[int, int] | None = None
    metrics: dict[str, int | float | str] = field(default_factory=dict)
    is_solution: bool = False


@dataclass
class SearchTrace:
    """A complete, replayable algorithm trace."""

    algorithm: str
    board_size: int
    frames: list[TraceFrame]
    solutions: list[Solution]

    @property
    def final_frame(self) -> TraceFrame:
        return self.frames[-1]


def build_trace(settings: TraceSettings) -> SearchTrace:
    """Build a replayable trace for the selected algorithm."""

    problem = NQueensProblem(settings.board_size)
    rng = random.Random(settings.seed)

    builders = {
        "Backtracking": _trace_backtracking,
        "Brute Force": _trace_brute_force,
        "Hill Climbing": _trace_hill_climbing,
        "Simulated Annealing": _trace_simulated_annealing,
        "Genetic Algorithm": _trace_genetic,
    }

    try:
        return builders[settings.algorithm](problem, settings, rng)
    except KeyError as exc:
        raise ValueError(f"Unsupported algorithm: {settings.algorithm}") from exc


def _new_trace(algorithm: str, problem: NQueensProblem) -> tuple[list[TraceFrame], list[Solution]]:
    frames = [
        TraceFrame(
            board=[-1] * problem.size,
            message=f"{algorithm} ready.",
            phase="start",
        )
    ]
    return frames, []


def _append_frame(frames: list[TraceFrame], frame: TraceFrame, settings: TraceSettings) -> bool:
    if len(frames) >= settings.max_frames:
        return False
    frames.append(frame)
    return True


def _position_conflicts(board: Solution, col: int, row: int) -> list[tuple[int, int]]:
    conflicts: list[tuple[int, int]] = []

    for placed_col, placed_row in enumerate(board):
        if placed_row == -1:
            continue

        same_row = placed_row == row
        same_diagonal = abs(placed_row - row) == abs(placed_col - col)
        if same_row or same_diagonal:
            conflicts.append((placed_col, placed_row))

    return conflicts


def _all_conflicts(board: Solution) -> list[tuple[int, int]]:
    conflicts: list[tuple[int, int]] = []

    for left_col in range(len(board)):
        for right_col in range(left_col + 1, len(board)):
            left_row = board[left_col]
            right_row = board[right_col]
            if left_row == -1 or right_row == -1:
                continue
            if left_row == right_row or abs(left_row - right_row) == abs(left_col - right_col):
                conflicts.append((left_col, left_row))
                conflicts.append((right_col, right_row))

    return list(dict.fromkeys(conflicts))


def _trace_backtracking(
    problem: NQueensProblem,
    settings: TraceSettings,
    rng: random.Random,
) -> SearchTrace:
    del rng
    frames, solutions = _new_trace("Backtracking", problem)
    board = [-1] * problem.size
    attempts = 0
    backtracks = 0
    should_stop = False

    def search(col: int) -> None:
        nonlocal attempts, backtracks, should_stop
        if should_stop:
            return

        if col == problem.size:
            solution = board.copy()
            solutions.append(solution)
            _append_frame(
                frames,
                TraceFrame(
                    board=solution,
                    message="Solution found.",
                    phase="solution",
                    attempts=attempts,
                    metrics={"solutions": len(solutions), "backtracks": backtracks},
                    is_solution=True,
                ),
                settings,
            )
            should_stop = settings.stop_at_first_solution
            return

        for row in range(problem.size):
            attempts += 1
            conflicts = _position_conflicts(board, col, row)
            if not _append_frame(
                frames,
                TraceFrame(
                    board=board.copy(),
                    message=f"Try column {col}, row {row}.",
                    phase="try",
                    attempts=attempts,
                    active=(col, row),
                    conflicts=conflicts,
                    metrics={"solutions": len(solutions), "backtracks": backtracks},
                ),
                settings,
            ):
                should_stop = True
                return

            if conflicts:
                continue

            board[col] = row
            _append_frame(
                frames,
                TraceFrame(
                    board=board.copy(),
                    message="Safe position. Continue to the next column.",
                    phase="place",
                    attempts=attempts,
                    active=(col, row),
                    metrics={"solutions": len(solutions), "backtracks": backtracks},
                ),
                settings,
            )

            search(col + 1)
            if should_stop:
                return

            board[col] = -1
            backtracks += 1
            _append_frame(
                frames,
                TraceFrame(
                    board=board.copy(),
                    message="Backtrack to the previous column.",
                    phase="backtrack",
                    attempts=attempts,
                    active=(col, row),
                    metrics={"solutions": len(solutions), "backtracks": backtracks},
                ),
                settings,
            )

    search(0)
    return SearchTrace("Backtracking", problem.size, frames, solutions)


def _trace_brute_force(
    problem: NQueensProblem,
    settings: TraceSettings,
    rng: random.Random,
) -> SearchTrace:
    del rng
    frames, solutions = _new_trace("Brute Force", problem)

    for attempts, candidate in enumerate(permutations(range(problem.size)), start=1):
        board = list(candidate)
        is_solution = problem.is_valid(board)
        conflicts = [] if is_solution else _all_conflicts(board)

        if is_solution:
            solutions.append(board.copy())

        if not _append_frame(
            frames,
            TraceFrame(
                board=board,
                message="Valid permutation found." if is_solution else "Check the next permutation.",
                phase="solution" if is_solution else "try",
                attempts=attempts,
                conflicts=conflicts,
                metrics={"solutions": len(solutions)},
                is_solution=is_solution,
            ),
            settings,
        ):
            break

        if is_solution and settings.stop_at_first_solution:
            break

    return SearchTrace("Brute Force", problem.size, frames, solutions)


def _trace_hill_climbing(
    problem: NQueensProblem,
    settings: TraceSettings,
    rng: random.Random,
) -> SearchTrace:
    frames, solutions = _new_trace("Hill Climbing", problem)
    seen: set[tuple[int, ...]] = set()
    attempts = 0

    for restart in range(settings.restarts):
        current = [rng.randrange(problem.size) for _ in range(problem.size)]
        current_conflicts = problem.count_conflicts(current)
        _append_frame(
            frames,
            TraceFrame(
                board=current.copy(),
                message=f"Restart {restart + 1}: begin from a random board.",
                phase="restart",
                attempts=attempts,
                conflicts=_all_conflicts(current),
                metrics={"conflicts": current_conflicts, "restart": restart + 1},
            ),
            settings,
        )

        for _ in range(settings.max_steps):
            attempts += 1
            if current_conflicts == 0:
                key = tuple(current)
                if key not in seen:
                    seen.add(key)
                    solutions.append(current.copy())
                _append_frame(
                    frames,
                    TraceFrame(
                        board=current.copy(),
                        message="Local search reached a valid solution.",
                        phase="solution",
                        attempts=attempts,
                        metrics={"solutions": len(solutions), "restart": restart + 1},
                        is_solution=True,
                    ),
                    settings,
                )
                if settings.stop_at_first_solution:
                    return SearchTrace("Hill Climbing", problem.size, frames, solutions)

            neighbor = _best_neighbor(problem, current)
            neighbor_conflicts = problem.count_conflicts(neighbor)
            if neighbor_conflicts >= current_conflicts:
                _append_frame(
                    frames,
                    TraceFrame(
                        board=current.copy(),
                        message="No better neighbor was found.",
                        phase="plateau",
                        attempts=attempts,
                        conflicts=_all_conflicts(current),
                        metrics={"conflicts": current_conflicts, "restart": restart + 1},
                    ),
                    settings,
                )
                break

            current = neighbor
            current_conflicts = neighbor_conflicts
            if not _append_frame(
                frames,
                TraceFrame(
                    board=current.copy(),
                    message="Move to the best neighboring board.",
                    phase="move",
                    attempts=attempts,
                    conflicts=_all_conflicts(current),
                    metrics={"conflicts": current_conflicts, "restart": restart + 1},
                ),
                settings,
            ):
                return SearchTrace("Hill Climbing", problem.size, frames, solutions)

    return SearchTrace("Hill Climbing", problem.size, frames, solutions)


def _best_neighbor(problem: NQueensProblem, board: Solution) -> Solution:
    best = board.copy()
    best_conflicts = problem.count_conflicts(best)

    for col in range(problem.size):
        original_row = board[col]
        for row in range(problem.size):
            if row == original_row:
                continue
            candidate = board.copy()
            candidate[col] = row
            conflicts = problem.count_conflicts(candidate)
            if conflicts < best_conflicts:
                best = candidate
                best_conflicts = conflicts

    return best


def _trace_simulated_annealing(
    problem: NQueensProblem,
    settings: TraceSettings,
    rng: random.Random,
) -> SearchTrace:
    frames, solutions = _new_trace("Simulated Annealing", problem)
    current = [rng.randrange(problem.size) for _ in range(problem.size)]
    current_conflicts = problem.count_conflicts(current)
    temperature = settings.initial_temperature

    for step in range(1, settings.max_steps + 1):
        if current_conflicts == 0:
            solutions.append(current.copy())
            _append_frame(
                frames,
                TraceFrame(
                    board=current.copy(),
                    message="Annealing reached a valid solution.",
                    phase="solution",
                    attempts=step,
                    metrics={"temperature": round(temperature, 4), "solutions": len(solutions)},
                    is_solution=True,
                ),
                settings,
            )
            break

        neighbor = current.copy()
        col = rng.randrange(problem.size)
        neighbor[col] = rng.randrange(problem.size)
        neighbor_conflicts = problem.count_conflicts(neighbor)
        accepted = _accept_annealing_move(current_conflicts, neighbor_conflicts, temperature, rng)

        if accepted:
            current = neighbor
            current_conflicts = neighbor_conflicts

        if not _append_frame(
            frames,
            TraceFrame(
                board=current.copy(),
                message="Accepted a candidate board." if accepted else "Rejected a candidate board.",
                phase="move" if accepted else "reject",
                attempts=step,
                active=(col, current[col]),
                conflicts=_all_conflicts(current),
                metrics={"temperature": round(temperature, 4), "conflicts": current_conflicts},
            ),
            settings,
        ):
            break

        temperature *= settings.cooling_rate
        if temperature < 0.0001:
            temperature = settings.initial_temperature

    return SearchTrace("Simulated Annealing", problem.size, frames, solutions)


def _accept_annealing_move(
    current_conflicts: int,
    neighbor_conflicts: int,
    temperature: float,
    rng: random.Random,
) -> bool:
    if neighbor_conflicts <= current_conflicts:
        return True
    probability = math.exp((current_conflicts - neighbor_conflicts) / temperature)
    return rng.random() < probability


def _trace_genetic(
    problem: NQueensProblem,
    settings: TraceSettings,
    rng: random.Random,
) -> SearchTrace:
    frames, solutions = _new_trace("Genetic Algorithm", problem)
    population = [
        [rng.randrange(problem.size) for _ in range(problem.size)]
        for _ in range(settings.population_size)
    ]

    for generation in range(1, settings.generations + 1):
        population.sort(key=problem.fitness, reverse=True)
        best = population[0]
        best_conflicts = problem.count_conflicts(best)

        if best_conflicts == 0:
            solutions.append(best.copy())

        if not _append_frame(
            frames,
            TraceFrame(
                board=best.copy(),
                message=(
                    "Best individual is a valid solution."
                    if best_conflicts == 0
                    else "Evolve the population."
                ),
                phase="solution" if best_conflicts == 0 else "generation",
                attempts=generation,
                conflicts=_all_conflicts(best),
                metrics={
                    "generation": generation,
                    "best_conflicts": best_conflicts,
                    "population": settings.population_size,
                },
                is_solution=best_conflicts == 0,
            ),
            settings,
        ):
            break

        if best_conflicts == 0 and settings.stop_at_first_solution:
            break

        population = _next_population(problem, population, settings, rng)

    return SearchTrace("Genetic Algorithm", problem.size, frames, solutions)


def _next_population(
    problem: NQueensProblem,
    population: list[Solution],
    settings: TraceSettings,
    rng: random.Random,
) -> list[Solution]:
    elite_count = max(2, settings.population_size // 10)
    next_population = [item.copy() for item in population[:elite_count]]

    while len(next_population) < settings.population_size:
        parent_a = _tournament(problem, population, rng)
        parent_b = _tournament(problem, population, rng)
        split = rng.randrange(1, problem.size)
        child = parent_a[:split] + parent_b[split:]

        for col in range(problem.size):
            if rng.random() < settings.mutation_rate:
                child[col] = rng.randrange(problem.size)

        next_population.append(child)

    return next_population


def _tournament(problem: NQueensProblem, population: list[Solution], rng: random.Random) -> Solution:
    sample = rng.sample(population, k=min(5, len(population)))
    return max(sample, key=problem.fitness)
