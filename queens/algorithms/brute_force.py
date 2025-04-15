import time
import json
import os
from itertools import permutations

class BruteForce:
    """暴力求解N皇后问题，找到所有解"""
    def __init__(self, board_size=8):
        self.board_size = board_size
        self.solutions = []
        self.save_dir = "brute_force_solutions"
        
        # 创建保存目录
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            
    def is_valid_solution(self, solution):
        """检查解是否有效（无对角线冲突）"""
        for i in range(len(solution)):
            for j in range(i + 1, len(solution)):
                # 检查对角线冲突
                if abs(solution[i] - solution[j]) == abs(i - j):
                    return False
        return True
        
    def solve(self):
        """找到所有解"""
        start_time = time.time()
        print(f"开始求解 {self.board_size} 皇后问题...")
        
        # 生成所有可能的行排列
        # 因为每列只能有一个皇后，且每行也只能有一个皇后，所以解是行的排列
        all_permutations = list(permutations(range(self.board_size)))
        print(f"总共需要检查 {len(all_permutations)} 种排列...")
        
        # 筛选有效解（无对角线冲突）
        valid_count = 0
        for perm in all_permutations:
            if self.is_valid_solution(perm):
                valid_count += 1
                self.solutions.append(list(perm))
                
        elapsed_time = time.time() - start_time
        print(f"搜索完成！找到 {len(self.solutions)} 个解，用时 {elapsed_time:.2f} 秒")
        
        # 保存所有解
        self.save_solutions()
        
        return self.solutions
        
    def save_solutions(self):
        """保存所有找到的解"""
        if not self.solutions:
            print("没有找到解，不保存")
            return
            
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = os.path.abspath(os.path.join(
                self.save_dir, f"nqueens_{self.board_size}_all_{len(self.solutions)}_solutions.json"
            ))
            
            data = {
                "board_size": self.board_size,
                "total_solutions": len(self.solutions),
                "solutions": self.solutions
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
                
            print(f"已保存所有 {len(self.solutions)} 个解到文件: {filename}")
        except Exception as e:
            print(f"保存解时出错: {str(e)}")
            
    def verify_solutions(self, other_solutions):
        """验证其他算法的解是否正确"""
        if not self.solutions:
            self.solve()
            
        # 转换为集合便于比较
        correct_solutions = {tuple(s) for s in self.solutions}
        test_solutions = {tuple(s) for s in other_solutions}
        
        # 找出正确的解、缺失的解和错误的解
        correct_matches = test_solutions.intersection(correct_solutions)
        missing_solutions = correct_solutions - test_solutions
        wrong_solutions = test_solutions - correct_solutions
        
        result = {
            "correct": len(correct_matches),
            "missing": len(missing_solutions),
            "wrong": len(wrong_solutions),
            "total_expected": len(correct_solutions),
            "accuracy": len(correct_matches) / len(correct_solutions) if correct_solutions else 0
        }
        
        print(f"验证结果:")
        print(f"  正确解: {result['correct']}/{result['total_expected']} ({result['accuracy']*100:.2f}%)")
        print(f"  缺失解: {result['missing']}")
        print(f"  错误解: {result['wrong']}")
        
        if result['missing'] > 0:
            print("部分缺失的解:")
            for i, sol in enumerate(list(missing_solutions)[:5]):  # 只显示前5个
                print(f"  {i+1}. {sol}")
                
        if result['wrong'] > 0:
            print("部分错误的解:")
            for i, sol in enumerate(list(wrong_solutions)[:5]):  # 只显示前5个
                print(f"  {i+1}. {sol}")
                
        return result
        
if __name__ == "__main__":
    # 直接运行此脚本可以找到并保存所有解
    solver = BruteForce(8)  # 8皇后问题
    solutions = solver.solve()
    print(f"找到 {len(solutions)} 个解")
    
    # 如果有从其他算法保存的解，可以验证
    # import json
    # with open("other_solutions.json", "r") as f:
    #     other_solutions = json.load(f)["solutions"]
    # solver.verify_solutions(other_solutions) 