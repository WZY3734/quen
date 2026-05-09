"""Compatibility helper for running the brute-force solver directly."""

from queenquest.algorithms import BruteForceSolver
from queenquest.io import save_result
from queenquest.problem import NQueensProblem


def main() -> None:
    size_text = input("Board size (press Enter for 8): ").strip()
    size = int(size_text) if size_text else 8

    problem = NQueensProblem(size)
    solver = BruteForceSolver(problem)
    result = solver.solve()
    output_path = save_result(result)

    print(f"Solutions: {result.total_solutions}")
    print(f"Candidates checked: {result.iterations}")
    print(f"Elapsed: {result.elapsed_seconds:.4f}s")
    print(f"Saved result to: {output_path}")


if __name__ == "__main__":
    main()
