import random
import math
from typing import List, Tuple
import time
import json
import os

class GeneticAlgorithm:
    def __init__(self, population_size=100, mutation_rate=0.3, problem=None):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.problem = problem
        self.population = []
        self.fitness_cache = {}
        self.best_solution = None
        self.best_fitness = 0
        self.start_time = None
        self.generation_count = 0
        self.no_improvement_count = 0
        self.solutions = []  # 添加保存所有找到的解的列表
        
        # 预计算
        self.board_size = problem.board_size
        self.positions = list(range(self.board_size))
        
        # 创建保存目录
        self.algorithm_name = self.__class__.__name__
        self.save_dir = os.path.join("solutions", self.algorithm_name)
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        
    def initialize_population(self):
        """初始化种群，使用启发式方法"""
        self.population = []
        self.fitness_cache = {}
        
        # 随机初始化部分种群
        for _ in range(self.population_size // 4):
            # 完全随机解
            solution = [0] * self.board_size
            for i in range(self.board_size):
                solution[i] = random.randint(0, self.board_size - 1)
            self.population.append(solution)
            
        # 使用贪婪方法初始化部分种群
        for _ in range(self.population_size // 4):
            solution = [0] * self.board_size
            for i in range(self.board_size):
                best_row = random.randint(0, self.board_size - 1)
                best_conflicts = float('inf')
                
                for row in range(self.board_size):
                    solution[i] = row
                    conflicts = self.get_conflicts_at(solution, i)
                    if conflicts < best_conflicts:
                        best_conflicts = conflicts
                        best_row = row
                        
                solution[i] = best_row
            self.population.append(solution)
            
        # 对角线启发式
        for _ in range(self.population_size // 4):
            solution = [0] * self.board_size
            for i in range(self.board_size):
                solution[i] = (i + random.randint(0, self.board_size - 1)) % self.board_size
            self.population.append(solution)
            
        # 反对角线启发式
        for _ in range(self.population_size // 4):
            solution = [0] * self.board_size
            for i in range(self.board_size):
                solution[i] = (self.board_size - 1 - i + random.randint(0, self.board_size - 1)) % self.board_size
            self.population.append(solution)
            
        # 评估种群
        for solution in self.population:
            self.get_fitness(solution)
            
        # 找到最佳解
        self.update_best_solution()
        
    def get_conflicts_at(self, solution, col):
        """计算指定列的皇后与其他列的冲突数"""
        conflicts = 0
        row = solution[col]
        
        for i in range(self.board_size):
            if i == col:
                continue
            if solution[i] == row:  # 同行冲突
                conflicts += 1
            if abs(solution[i] - row) == abs(i - col):  # 对角线冲突
                conflicts += 1
                
        return conflicts
            
    def get_fitness(self, solution):
        """获取适应度，使用缓存"""
        solution_tuple = tuple(solution)
        if solution_tuple in self.fitness_cache:
            return self.fitness_cache[solution_tuple]
            
        fitness = self.problem.fitness(solution)
        self.fitness_cache[solution_tuple] = fitness
        return fitness
        
    def select_parents(self):
        """使用锦标赛选择父母"""
        tournament_size = 5
        
        # 选择父亲
        father_candidates = random.sample(self.population, tournament_size)
        father = max(father_candidates, key=self.get_fitness)
        
        # 选择母亲
        mother_candidates = random.sample(self.population, tournament_size)
        mother = max(mother_candidates, key=self.get_fitness)
        
        return father, mother
        
    def crossover(self, father, mother):
        """交叉操作，使用二点交叉"""
        if random.random() < 0.9:  # 交叉概率
            point1 = random.randint(0, self.board_size - 2)
            point2 = random.randint(point1 + 1, self.board_size - 1)
            
            child1 = father[:point1] + mother[point1:point2] + father[point2:]
            child2 = mother[:point1] + father[point1:point2] + mother[point2:]
            
            return child1, child2
        else:
            return father.copy(), mother.copy()
        
    def mutate(self, solution):
        """变异操作，使用适应性变异"""
        fitness = self.get_fitness(solution)
        
        # 根据适应度调整变异率
        mutation_rate = self.mutation_rate
        if fitness < 0.3:  # 低适应度，增加变异率
            mutation_rate = min(0.8, self.mutation_rate * 2)
        elif fitness > 0.7:  # 高适应度，降低变异率
            mutation_rate = max(0.1, self.mutation_rate / 2)
            
        mutated = solution.copy()
        
        # 基于冲突的有针对性变异
        if random.random() < 0.5:
            # 找出冲突最多的皇后
            max_conflicts = 0
            max_conflict_col = 0
            
            for col in range(self.board_size):
                conflicts = self.get_conflicts_at(solution, col)
                if conflicts > max_conflicts:
                    max_conflicts = conflicts
                    max_conflict_col = col
                    
            # 变异冲突最多的皇后
            if max_conflicts > 0:
                best_row = solution[max_conflict_col]
                best_conflicts = max_conflicts
                
                for row in range(self.board_size):
                    mutated[max_conflict_col] = row
                    conflicts = self.get_conflicts_at(mutated, max_conflict_col)
                    if conflicts < best_conflicts:
                        best_conflicts = conflicts
                        best_row = row
                        
                mutated[max_conflict_col] = best_row
        else:
            # 随机变异
            for i in range(self.board_size):
                if random.random() < mutation_rate:
                    mutated[i] = random.randint(0, self.board_size - 1)
                    
        return mutated
        
    def evolve(self):
        """进化一代"""
        if not self.population:
            self.start_time = time.time()
            self.initialize_population()
            self.generation_count = 0
            self.no_improvement_count = 0
            self.solutions = []  # 重置解列表
            return
            
        self.generation_count += 1
        
        # 精英保留
        elite_size = max(1, self.population_size // 10)
        elites = sorted(self.population, key=self.get_fitness, reverse=True)[:elite_size]
        
        # 生成新一代
        new_population = elites.copy()
        
        # 检查当前种群中是否有有效解
        for individual in self.population:
            if self.problem.is_valid_solution(individual):
                if individual not in self.solutions:
                    self.solutions.append(individual.copy())
        
        # 生成新个体直到种群大小满足要求
        while len(new_population) < self.population_size:
            # 选择父母
            father, mother = self.select_parents()
            
            # 交叉
            child1, child2 = self.crossover(father, mother)
            
            # 变异
            child1 = self.mutate(child1)
            child2 = self.mutate(child2)
            
            # 添加到新种群
            new_population.append(child1)
            if len(new_population) < self.population_size:
                new_population.append(child2)
                
        self.population = new_population
        
        # 更新最佳解
        old_best_fitness = self.best_fitness
        self.update_best_solution()
        
        # 检查是否有改进
        if self.best_fitness <= old_best_fitness:
            self.no_improvement_count += 1
        else:
            self.no_improvement_count = 0
            
        # 如果长时间没有改进，重置部分种群
        if self.no_improvement_count >= 20:
            self.reset_population()
            
    def update_best_solution(self):
        """更新最佳解"""
        for solution in self.population:
            fitness = self.get_fitness(solution)
            if fitness > self.best_fitness:
                self.best_fitness = fitness
                self.best_solution = solution.copy()
                
    def reset_population(self):
        """重置部分种群"""
        # 保留最好的20%个体
        elite_size = max(1, self.population_size // 5)
        elites = sorted(self.population, key=self.get_fitness, reverse=True)[:elite_size]
        
        # 重新初始化剩余80%
        self.population = elites
        self.initialize_population()
        self.population = self.population[:self.population_size - elite_size] + elites
        self.no_improvement_count = 0
        
    def step(self):
        """执行一步进化"""
        self.evolve()
        
    def get_best_solution(self):
        """获取最佳解"""
        return self.best_solution if self.best_solution else [0] * self.board_size
        
    def get_best_fitness(self):
        """获取最佳适应度"""
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
                    "population_size": self.population_size,
                    "mutation_rate": self.mutation_rate
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