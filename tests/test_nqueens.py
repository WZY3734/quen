import unittest

from queenquest.algorithms import BacktrackingSolver
from queenquest.problem import NQueensProblem
from queenquest.tracing import ALGORITHMS, TraceSettings, build_trace


class NQueensProblemTest(unittest.TestCase):
    def test_valid_solution_has_no_conflicts(self) -> None:
        problem = NQueensProblem(8)
        solution = [0, 4, 7, 5, 2, 6, 1, 3]

        self.assertTrue(problem.is_valid(solution))
        self.assertEqual(problem.count_conflicts(solution), 0)

    def test_invalid_solution_has_conflicts(self) -> None:
        problem = NQueensProblem(4)
        solution = [0, 1, 2, 3]

        self.assertFalse(problem.is_valid(solution))
        self.assertGreater(problem.count_conflicts(solution), 0)


class BacktrackingSolverTest(unittest.TestCase):
    def test_backtracking_finds_all_8_queen_solutions(self) -> None:
        problem = NQueensProblem(8)
        result = BacktrackingSolver(problem).solve()

        self.assertEqual(result.total_solutions, 92)
        self.assertTrue(all(problem.is_valid(solution) for solution in result.solutions))


class SearchTraceTest(unittest.TestCase):
    def test_every_algorithm_builds_a_trace(self) -> None:
        for algorithm in ALGORITHMS:
            with self.subTest(algorithm=algorithm):
                trace = build_trace(
                    TraceSettings(
                        board_size=4,
                        algorithm=algorithm,
                        max_steps=200,
                        generations=50,
                        population_size=30,
                    )
                )

                self.assertEqual(trace.algorithm, algorithm)
                self.assertGreater(len(trace.frames), 0)
                self.assertEqual(trace.board_size, 4)

    def test_backtracking_trace_reaches_a_solution(self) -> None:
        trace = build_trace(TraceSettings(board_size=4, algorithm="Backtracking"))

        self.assertEqual(trace.solutions[0], [1, 3, 0, 2])
        self.assertTrue(trace.final_frame.is_solution)


if __name__ == "__main__":
    unittest.main()
