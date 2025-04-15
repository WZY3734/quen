from typing import List, Optional
import time
import json
import os

class Backtracking:
    def __init__(self, problem):
        self.problem = problem
        self.board_size = problem.board_size
        self.solutions = []
        self.current_solution = [0] * self.board_size
        self.start_time = None
        self.solution_count = 0
        self.is_solving = False
        self.generation_count = 0
        
        # 搜索状态
        self.stack = []
        
        # 创建保存目录
        self.algorithm_name = self.__class__.__name__
        self.save_dir = os.path.join("solutions", self.algorithm_name)
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            
    def save_solutions(self):
        """保存所有找到的解，替换之前保存的解"""
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
            
            # 准备要保存的数据
            data = {
                "board_size": self.board_size,
                "algorithm": self.algorithm_name,
                "parameters": {},
                "total_solutions": len(self.solutions),
                "generations": self.generation_count,
                "time_taken": time.time() - self.start_time if self.start_time else 0,
                "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
                "solutions": [list(s) for s in self.solutions]  # 确保列表可序列化
            }
            
            # 保存文件
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"已更新并保存 {len(self.solutions)} 个解到文件: {filename}")
        except Exception as e:
            print(f"保存解时出错: {str(e)}")
            
    def solve(self):
        """初始化回溯搜索"""
        if not self.is_solving:
            self.start_time = time.time()
            self.solutions = []
            self.current_solution = [0] * self.board_size
            self.solution_count = 0
            self.generation_count = 0
            self.is_solving = True
            
            # 初始化栈 (col, row_index)
            self.stack = [(0, 0)]
            
        return self.solutions
        
    def is_safe(self, col, row):
        """检查位置是否安全"""
        for i in range(col):
            if self.current_solution[i] == row:  # 同行
                return False
            if abs(self.current_solution[i] - row) == abs(i - col):  # 对角线
                return False
        return True
        
    def step(self):
        """迭代式执行一步回溯搜索"""
        if not self.is_solving:
            self.solve()
            return
            
        # 执行多步以加快速度，但保持界面响应
        steps_per_frame = 100
        steps_done = 0
        
        while steps_done < steps_per_frame and self.stack and self.is_solving:
            steps_done += 1
            
            # 获取当前位置
            col, row = self.stack.pop()
            
            # 尝试所有行，从当前行开始
            while row < self.board_size:
                self.generation_count += 1
                
                # 检查是否可以放置皇后
                if self.is_safe(col, row):
                    # 放置皇后
                    self.current_solution[col] = row
                    
                    # 如果是最后一列，找到一个解
                    if col == self.board_size - 1:
                        new_solution = self.current_solution.copy()
                        self.solutions.append(new_solution)
                        self.solution_count += 1
                        row += 1  # 继续尝试下一行
                        break  # 跳出内循环，让外循环处理下一个栈项
                    
                    # 保存当前状态，并前进到下一列
                    self.stack.append((col, row + 1))  # 记录当前列的下一行，用于回溯
                    col += 1
                    row = 0  # 在新列中从第0行开始
                    continue  # 跳过row+=1，直接处理新列
                
                row += 1
            
            # 如果已经找到了所有解（对于8皇后，总共92个解）
            if len(self.solutions) >= 92:
                self.is_solving = False
                self.save_solutions()
                break
                
        # 如果栈为空，搜索结束
        if not self.stack and self.is_solving:
            self.is_solving = False
            self.save_solutions()
            print(f"搜索完成，找到 {len(self.solutions)} 个解")
            
    def get_best_solution(self):
        """获取最佳解"""
        if self.solutions:
            return self.solutions[-1]
        return self.current_solution
        
    def get_best_fitness(self):
        """获取最佳解的适应度"""
        solution = self.get_best_solution()
        return self.problem.fitness(solution)
        
    def get_progress(self):
        """获取搜索进度"""
        return {
            "solutions_found": len(self.solutions),
            "generations": self.generation_count,
            "time_elapsed": time.time() - self.start_time if self.start_time else 0,
            "is_solving": self.is_solving
        }

    def solve_all(self):
        """找到所有解并返回，用于验证"""
        print("开始回溯算法搜索所有解...")
        
        # 重置状态
        self.solutions = []
        self.current_solution = [0] * self.board_size
        self.start_time = time.time()
        self.solution_count = 0
        self.generation_count = 0
        
        # 使用递归回溯一次性找到所有解
        def backtrack(col):
            # 如果到达最后一列，找到一个解
            if col == self.board_size:
                self.solutions.append(self.current_solution.copy())
                self.solution_count += 1
                return
            
            # 尝试每一行
            for row in range(self.board_size):
                self.generation_count += 1
                
                # 检查是否可以放置皇后
                if self.is_safe(col, row):
                    # 放置皇后
                    self.current_solution[col] = row
                    
                    # 递归搜索下一列
                    backtrack(col + 1)
                
        # 开始回溯
        backtrack(0)
        
        elapsed = time.time() - self.start_time
        print(f"回溯算法完成，找到 {len(self.solutions)} 个解，用时 {elapsed:.2f} 秒")
        
        return self.solutions 