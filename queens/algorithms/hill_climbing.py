import random
import time
import json
import os
from typing import List, Optional

class HillClimbing:
    def __init__(self, problem):
        self.problem = problem
        self.board_size = problem.board_size
        self.current_solution = self.initialize_solution()
        self.current_fitness = self.problem.fitness(self.current_solution)
        self.best_solution = self.current_solution.copy()
        self.best_fitness = self.current_fitness
        self.start_time = None
        self.generation_count = 0
        self.no_improvement_count = 0
        self.max_no_improvement = 100
        self.restarts = 0
        self.max_restarts = 10
        self.fitness_cache = {}
        self.solutions = []  # 添加保存所有找到的解的列表
        
        # 创建保存目录
        self.algorithm_name = self.__class__.__name__
        self.save_dir = os.path.join("solutions", self.algorithm_name)
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            
    def initialize_solution(self):
        """使用启发式方法初始化解"""
        solution = [0] * self.board_size
        
        # 使用对角线策略
        if random.random() < 0.5:
            # 主对角线启发式
            for i in range(self.board_size):
                solution[i] = (i + random.randint(0, self.board_size // 2)) % self.board_size
        else:
            # 随机初始化
            for i in range(self.board_size):
                solution[i] = random.randint(0, self.board_size - 1)
                
        return solution
        
    def get_fitness(self, solution):
        """计算适应度，使用缓存"""
        solution_tuple = tuple(solution)
        if solution_tuple in self.fitness_cache:
            return self.fitness_cache[solution_tuple]
            
        fitness = self.problem.fitness(solution)
        self.fitness_cache[solution_tuple] = fitness
        return fitness
        
    def get_neighbors(self, solution):
        """生成所有邻居解"""
        neighbors = []
        
        # 生成有针对性的邻居
        for col in range(self.board_size):
            # 找出当前列的冲突
            conflicts = self.get_conflicts(solution, col)
            if conflicts > 0:
                # 尝试移动这个皇后到其他行
                current_row = solution[col]
                for row in range(self.board_size):
                    if row != current_row:
                        neighbor = solution.copy()
                        neighbor[col] = row
                        neighbors.append(neighbor)
        
        # 如果没有冲突的列，生成随机邻居
        if not neighbors:
            for _ in range(min(10, self.board_size * 2)):
                col = random.randint(0, self.board_size - 1)
                row = random.randint(0, self.board_size - 1)
                if solution[col] != row:
                    neighbor = solution.copy()
                    neighbor[col] = row
                    neighbors.append(neighbor)
                    
        return neighbors
        
    def get_conflicts(self, solution, col):
        """计算指定列的皇后与其他列的冲突数"""
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
        
    def step(self):
        """执行一步爬山搜索"""
        if self.start_time is None:
            self.start_time = time.time()
            self.solutions = []  # 重置解列表
            
        # 执行多步以加快速度
        steps_per_frame = 10
        for _ in range(steps_per_frame):
            self.generation_count += 1
            
            # 获取所有邻居
            neighbors = self.get_neighbors(self.current_solution)
            
            # 找到最佳邻居
            best_neighbor = None
            best_neighbor_fitness = 0
            
            for neighbor in neighbors:
                fitness = self.get_fitness(neighbor)
                if fitness > best_neighbor_fitness:
                    best_neighbor = neighbor
                    best_neighbor_fitness = fitness
                    
            # 如果找到更好的解，更新当前解
            if best_neighbor_fitness > self.current_fitness:
                self.current_solution = best_neighbor
                self.current_fitness = best_neighbor_fitness
                self.no_improvement_count = 0
                
                # 更新最佳解
                if best_neighbor_fitness > self.best_fitness:
                    self.best_solution = best_neighbor.copy()
                    self.best_fitness = best_neighbor_fitness
                    
                # 检查是否找到有效解
                if self.problem.is_valid_solution(best_neighbor):
                    # 转换为元组以便于比较
                    solution_tuple = tuple(best_neighbor)
                    # 检查是否已经找到过这个解
                    if solution_tuple not in [tuple(s) for s in self.solutions]:
                        self.solutions.append(best_neighbor.copy())
                        print(f"爬山法找到新解! 总数: {len(self.solutions)}")
            else:
                self.no_improvement_count += 1
                
            # 如果长时间没有改进，重新开始
            if self.no_improvement_count >= self.max_no_improvement:
                if self.restarts < self.max_restarts:
                    self.current_solution = self.initialize_solution()
                    self.current_fitness = self.get_fitness(self.current_solution)
                    self.no_improvement_count = 0
                    self.restarts += 1
                else:
                    break
                    
    def get_best_solution(self):
        """获取最佳解"""
        return self.best_solution
        
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
                    "max_no_improvement": self.max_no_improvement,
                    "max_restarts": self.max_restarts
                },
                "total_solutions": len(self.solutions),
                "generations": self.generation_count,
                "restarts": self.restarts,
                "time_taken": time.time() - self.start_time if self.start_time else 0,
                "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
                "solutions": self.solutions
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"已更新并保存 {len(self.solutions)} 个解到文件: {filename}")
        except Exception as e:
            print(f"保存解时出错: {str(e)}") 