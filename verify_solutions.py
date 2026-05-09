"""Validate solution files written by QueenQuest."""

from __future__ import annotations

from pathlib import Path

from queenquest.io import load_solutions
from queenquest.problem import NQueensProblem


def verify_file(path: Path) -> None:
    solutions = load_solutions(path)

    if not solutions:
        print(f"{path}: no solutions to validate")
        return

    problem = NQueensProblem(len(solutions[0]))
    valid_count = sum(1 for solution in solutions if problem.is_valid(solution))

    print(f"{path}")
    print(f"  solutions: {len(solutions)}")
    print(f"  valid: {valid_count}")
    print(f"  invalid: {len(solutions) - valid_count}")


def main() -> None:
    result_files = sorted(Path("results").glob("*/nqueens_*_solutions.json"))

    if not result_files:
        print("No result files found under results/.")
        print("Run: python main.py --algorithm backtracking")
        return

    for path in result_files:
        verify_file(path)


if __name__ == "__main__":
    main()
