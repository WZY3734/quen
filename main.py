from queens.problem import QueensProblem
from queens.algorithms.genetic_algorithm import GeneticAlgorithm
from queens.algorithms.simulated_annealing import SimulatedAnnealing
from queens.algorithms.hill_climbing import HillClimbing
from queens.algorithms.backtracking import Backtracking
from queens.visualization import QueensVisualizer

def main():
    # 创建问题实例
    problem = QueensProblem()
    
    # 创建算法实例，优化参数
    ga = GeneticAlgorithm(
        population_size=100,  # 减小种群规模，提高收敛速度
        mutation_rate=0.3,    # 增加变异率，提高探索能力
        problem=problem
    )
    
    sa = SimulatedAnnealing(
        initial_temperature=100,  # 降低初始温度
        cooling_rate=0.95,        # 加快冷却速度
        min_temperature=0.01,     # 降低最小温度
        problem=problem
    )
    
    hc = HillClimbing(problem)  # 添加爬山法
    
    bt = Backtracking(problem)  # 添加回溯法
    
    # 创建并显示可视化
    visualizer = QueensVisualizer(problem, [ga, sa, hc, bt])
    visualizer.show()

if __name__ == "__main__":
    main() 