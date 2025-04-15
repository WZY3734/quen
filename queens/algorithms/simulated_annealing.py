import random
import math
from typing import List, Optional
import time
import json
import os

class SimulatedAnnealing:
    def __init__(self, initial_temperature=100, cooling_rate=0.95, min_temperature=0.01, problem=None):
        self.problem = problem
        self.board_size = problem.board_size
        self.initial_temperature = initial_temperature
        self.temperature = initial_temperature
        self.cooling_rate = cooling_rate
        self.min_temperature = min_temperature
        
        self.current_solution = None
        self.best_solution = None
        self.current_fitness = 0
        self.best_fitness = 0
        self.start_time = None
        self.generation_count = 0
        self.solutions = []  # 添加保存所有找到的解的列表
        
        # 性能优化
        self.fitness_cache = {}
        self.reheat_count = 0
        self.max_reheat = 3
        self.no_improvement_count = 0
        self.max_no_improvement = 1000
        
        # 创建保存目录
        self.algorithm_name = self.__class__.__name__
        self.save_dir = os.path.join("solutions", self.algorithm_name)
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        
    def initialize_solution(self):
        """初始化解，使用贪心策略"""
        solution = [0] * self.board_size
        
        # 使用对角线策略初始化
        for i in range(self.board_size):
            best_row = 0
            best_conflicts = float('inf')
            
            for row in range(self.board_size):
                solution[i] = row
                conflicts = 0
                
                for j in range(i):
                    if solution[j] == row or abs(solution[j] - row) == abs(j - i):
                        conflicts += 1
                        
                if conflicts < best_conflicts:
                    best_conflicts = conflicts
                    best_row = row
                    
            solution[i] = best_row
            
        return solution
        
    def get_fitness(self, solution):
        """获取适应度，使用缓存"""
        solution_tuple = tuple(solution)
        if solution_tuple in self.fitness_cache:
            return self.fitness_cache[solution_tuple]
            
        fitness = self.problem.fitness(solution)
        self.fitness_cache[solution_tuple] = fitness
        return fitness
        
    def get_neighbor(self, solution):
        """生成邻居解，根据温度动态调整搜索范围"""
        neighbor = solution.copy()
        
        # 根据温度计算变异数量
        temp_ratio = self.temperature / self.initial_temperature
        mutation_count = max(1, int(temp_ratio * 3))
        
        for _ in range(mutation_count):
            if random.random() < 0.5 and self.temperature < self.initial_temperature * 0.5:
                # 低温时，有针对性地改变最有冲突的皇后
                max_conflicts = 0
                max_conflict_col = 0
                
                for col in range(self.board_size):
                    conflicts = self.get_conflicts(solution, col)
                    if conflicts > max_conflicts:
                        max_conflicts = conflicts
                        max_conflict_col = col
                        
                if max_conflicts > 0:
                    neighbor[max_conflict_col] = random.randint(0, self.board_size - 1)
            else:
                # 随机改变位置
                col = random.randint(0, self.board_size - 1)
                neighbor[col] = random.randint(0, self.board_size - 1)
                
        return neighbor
        
    def get_conflicts(self, solution, col):
        """计算特定位置的冲突数"""
        conflicts = 0
        row = solution[col]
        
        for i in range(self.board_size):
            if i == col:
                continue
                
            if solution[i] == row:  # 同行冲突
                conflicts += 1
                
            # 对角线冲突
            if abs(solution[i] - row) == abs(i - col):
                conflicts += 1
                
        return conflicts
        
    def accept_solution(self, current_fitness, new_fitness):
        """接受解的概率函数"""
        if new_fitness >= current_fitness:
            return True
            
        # 根据温度和适应度差异计算接受概率
        delta = new_fitness - current_fitness
        probability = math.exp(delta * 20 / self.temperature)
        
        return random.random() < probability
        
    def step(self):
        """执行一步模拟退火"""
        if self.current_solution is None:
            # 初始化
            self.start_time = time.time()
            self.current_solution = self.initialize_solution()
            self.current_fitness = self.get_fitness(self.current_solution)
            self.best_solution = self.current_solution.copy()
            self.best_fitness = self.current_fitness
            self.temperature = self.initial_temperature
            self.generation_count = 0
            self.reheat_count = 0
            self.no_improvement_count = 0
            self.solutions = []  # 重置解列表
            return
            
        # 执行多步以加快速度
        steps_per_frame = 100
        for _ in range(steps_per_frame):
            if self.temperature < self.min_temperature:
                if self.reheat_count < self.max_reheat:
                    # 重新加热
                    self.temperature = self.initial_temperature * 0.8
                    self.reheat_count += 1
                    self.no_improvement_count = 0
                else:
                    # 终止搜索
                    return
                    
            self.generation_count += 1
            
            # 生成新解
            new_solution = self.get_neighbor(self.current_solution)
            new_fitness = self.get_fitness(new_solution)
            
            # 检查新解是否是有效解
            if self.problem.is_valid_solution(new_solution):
                # 转换为元组以便于比较
                solution_tuple = tuple(new_solution)
                # 检查是否已经找到过这个解
                if solution_tuple not in [tuple(s) for s in self.solutions]:
                    self.solutions.append(new_solution.copy())
                    print(f"模拟退火找到新解! 总数: {len(self.solutions)}")
            
            # 决定是否接受新解
            if self.accept_solution(self.current_fitness, new_fitness):
                self.current_solution = new_solution
                self.current_fitness = new_fitness
                
                # 更新最佳解
                if new_fitness > self.best_fitness:
                    self.best_solution = new_solution.copy()
                    self.best_fitness = new_fitness
                    self.no_improvement_count = 0
                else:
                    self.no_improvement_count += 1
            else:
                self.no_improvement_count += 1
                
            # 如果长时间没有改进，动态调整冷却率
            if self.no_improvement_count > self.max_no_improvement:
                if self.cooling_rate > 0.85:
                    self.cooling_rate = max(0.8, self.cooling_rate - 0.01)
                else:
                    self.cooling_rate = min(0.99, self.cooling_rate + 0.01)
                self.no_improvement_count = 0
                
            # 降温
            self.temperature *= self.cooling_rate
            
    def get_best_solution(self):
        """获取当前最佳解"""
        if self.best_solution is None:
            return [0] * self.board_size
        return self.best_solution
        
    def get_best_fitness(self):
        """获取当前最佳解的适应度"""
        return self.best_fitness
        
    def save_solutions(self):
        """保存找到的解，替换之前保存的解"""
        if not self.solutions:
            return
            
        try:
            # 创建保存目录（如果不存在）
            if not os.path.exists(self.save_dir):
                os.makedirs(self.save_dir)
            
            # 使用固定文件名，覆盖之前的文件
            filename = os.path.abspath(os.path.join(
                self.save_dir, f"nqueens_{self.board_size}_solutions.json"
            ))
            
            data = {
                "board_size": self.board_size,
                "algorithm": self.algorithm_name,
                "parameters": {
                    "initial_temperature": self.initial_temperature,
                    "cooling_rate": self.cooling_rate,
                    "min_temperature": self.min_temperature
                },
                "total_solutions": len(self.solutions),
                "generations": self.generation_count,
                "time_taken": time.time() - self.start_time if self.start_time else 0,
                "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
                "solutions": self.solutions
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"已更新并保存 {len(self.solutions)} 个解到文件: {filename}")
        except Exception as e:
            print(f"保存解时出错: {str(e)}") 