import numpy as np
from typing import List, Tuple
import time

class QueensProblem:
    def __init__(self, board_size=8):
        self.board_size = board_size
        self.positions = list(range(board_size))
        self.diagonals = [0] * (2 * board_size - 1)
        self.anti_diagonals = [0] * (2 * board_size - 1)
        self.rows = [0] * board_size
        
        # 预计算所有可能的位置
        self.positions = np.arange(board_size)
        
        # 预计算对角线索引
        self.diag_indices = np.zeros((board_size, board_size), dtype=int)
        self.anti_diag_indices = np.zeros((board_size, board_size), dtype=int)
        for i in range(board_size):
            for j in range(board_size):
                self.diag_indices[i, j] = i + j
                self.anti_diag_indices[i, j] = i - j + board_size - 1
                
    def is_valid_solution(self, solution):
        """使用位运算快速检查解是否有效"""
        # 重置掩码
        self.diagonals = [0] * (2 * self.board_size - 1)
        self.anti_diagonals = [0] * (2 * self.board_size - 1)
        self.rows = [0] * self.board_size
        
        for col, row in enumerate(solution):
            # 检查行冲突
            if self.rows[row]:
                return False
            self.rows[row] = 1
            
            # 检查对角线冲突
            diag = self.diag_indices[col, row]
            anti_diag = self.anti_diag_indices[col, row]
            if self.diagonals[diag] or self.anti_diagonals[anti_diag]:
                return False
            self.diagonals[diag] = 1
            self.anti_diagonals[anti_diag] = 1
            
        return True
        
    def fitness(self, solution):
        """快速计算适应度"""
        conflicts = 0
        # 重置掩码
        self.diagonals = [0] * (2 * self.board_size - 1)
        self.anti_diagonals = [0] * (2 * self.board_size - 1)
        self.rows = [0] * self.board_size
        
        for col, row in enumerate(solution):
            # 检查行冲突
            if self.rows[row]:
                conflicts += 1
            self.rows[row] = 1
            
            # 检查对角线冲突
            diag = self.diag_indices[col, row]
            anti_diag = self.anti_diag_indices[col, row]
            if self.diagonals[diag]:
                conflicts += 1
            if self.anti_diagonals[anti_diag]:
                conflicts += 1
            self.diagonals[diag] = 1
            self.anti_diagonals[anti_diag] = 1
            
        return 1.0 / (1.0 + conflicts)
        
    def get_all_solutions(self):
        """使用优化的回溯算法获取所有解"""
        solutions = []
        stack = [(0, [0] * self.board_size)]
        
        while stack:
            col, solution = stack.pop()
            if col == self.board_size:
                solutions.append(solution.copy())
                continue
                
            for row in range(self.board_size):
                if self._is_safe(col, row, solution):
                    solution[col] = row
                    stack.append((col + 1, solution.copy()))
                    
        return solutions
        
    def _is_safe(self, col, row, solution):
        """快速检查位置是否安全"""
        for i in range(col):
            if solution[i] == row or \
               abs(solution[i] - row) == abs(i - col):
                return False
        return True
        
    def get_conflicts(self, solution):
        """获取解的冲突数"""
        conflicts = 0
        for i in range(len(solution)):
            for j in range(i + 1, len(solution)):
                if solution[i] == solution[j] or \
                   abs(solution[i] - solution[j]) == abs(i - j):
                    conflicts += 1
        return conflicts
        
    def get_solution_quality(self, solution):
        """评估解的质量"""
        conflicts = self.get_conflicts(solution)
        max_conflicts = self.board_size * (self.board_size - 1) // 2
        return 1.0 - conflicts / max_conflicts
        
    def get_symmetrical_solutions(self, solution):
        """获取对称解"""
        symmetrical = []
        n = self.board_size
        
        # 水平翻转
        horizontal = [n - 1 - row for row in solution]
        if horizontal != solution:
            symmetrical.append(horizontal)
            
        # 垂直翻转
        vertical = solution[::-1]
        if vertical != solution:
            symmetrical.append(vertical)
            
        # 对角线翻转
        diagonal = [solution.index(i) for i in range(n)]
        if diagonal != solution:
            symmetrical.append(diagonal)
            
        # 反对角线翻转
        anti_diagonal = [n - 1 - solution.index(n - 1 - i) for i in range(n)]
        if anti_diagonal != solution:
            symmetrical.append(anti_diagonal)
            
        return symmetrical