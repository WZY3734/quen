from __future__ import annotations

import argparse

from queenquest.algorithms import (
    BacktrackingSolver,
    BruteForceSolver,
    GeneticSolver,
    HillClimbingSolver,
    SimulatedAnnealingSolver,
)
from queenquest.algorithms.base import Solver
from queenquest.io import save_result
from queenquest.problem import NQueensProblem


def build_solver(name: str, problem: NQueensProblem) -> Solver:
    """Create a solver from its command-line name."""

    solvers = {
        "backtracking": BacktrackingSolver,
        "brute-force": BruteForceSolver,
        "genetic": GeneticSolver,
        "hill-climbing": HillClimbingSolver,
        "simulated-annealing": SimulatedAnnealingSolver,
    }

    try:
        return solvers[name](problem)
    except KeyError as exc:
        raise ValueError(f"Unknown algorithm: {name}") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="QueenQuest")
    parser.add_argument(
        "-n",
        "--size",
        type=int,
        default=8,
        help="Board size. Defaults to 8.",
    )
    parser.add_argument(
        "-a",
        "--algorithm",
        default="backtracking",
        choices=[
            "backtracking",
            "brute-force",
            "genetic",
            "hill-climbing",
            "simulated-annealing",
        ],
        help="Solver algorithm.",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Display the first solution in a Matplotlib window.",
    )
    parser.add_argument(
        "--animate",
        action="store_true",
        help="Animate the backtracking search for the first solution.",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=280,
        help="Animation frame interval in milliseconds. Defaults to 280.",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Print the result without writing a JSON file.",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the interactive QueenQuest desktop app.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.gui:
        from queenquest.app import main as run_app

        run_app()
        return

    if args.animate:
        from queenquest.animation import show_backtracking_animation

        show_backtracking_animation(args.size, interval=args.interval)
        return

    problem = NQueensProblem(args.size)
    solver = build_solver(args.algorithm, problem)
    result = solver.solve()

    print(f"Algorithm: {result.algorithm}")
    print(f"Board: {result.board_size} x {result.board_size}")
    print(f"Solutions: {result.total_solutions}")
    print(f"Iterations: {result.iterations}")
    print(f"Elapsed: {result.elapsed_seconds:.4f}s")

    if result.solutions:
        print("\nFirst solution:")
        print(result.solutions[0])
        print(problem.render_text(result.solutions[0]))

    if not args.no_save:
        output_path = save_result(result)
        print(f"\nSaved result to: {output_path}")

    if args.show:
        from queenquest.visualizer import show_first_solution

        show_first_solution(problem, result)


if __name__ == "__main__":
    main()
