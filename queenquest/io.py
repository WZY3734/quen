from __future__ import annotations

import json
from pathlib import Path

from queenquest.algorithms.base import SearchResult
from queenquest.problem import Solution


def save_result(result: SearchResult, output_dir: str | Path = "results") -> Path:
    """Save a solver result as JSON."""

    directory = Path(output_dir) / result.algorithm
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"nqueens_{result.board_size}_solutions.json"

    data = {
        "algorithm": result.algorithm,
        "board_size": result.board_size,
        "parameters": result.parameters,
        "total_solutions": result.total_solutions,
        "iterations": result.iterations,
        "elapsed_seconds": round(result.elapsed_seconds, 6),
        "solutions": result.solutions,
    }

    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def load_solutions(path: str | Path) -> list[Solution]:
    """Load the ``solutions`` field from a JSON result file."""

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [list(solution) for solution in data.get("solutions", [])]
