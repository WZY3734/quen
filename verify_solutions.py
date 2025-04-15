#!/usr/bin/env python
import os
import json
import glob
from queens.problem import QueensProblem
from queens.algorithms.brute_force import BruteForce

def main():
    print("="*50)
    print("N皇后问题 - 分算法验证解的正确性")
    print("="*50)
    
    # 1. 加载标准解决方案
    board_size = 8  # 8皇后问题
    print(f"\n1. 加载 {board_size} 皇后问题的标准解...")
    brute_force = BruteForce(board_size)
    
    # 检查是否已有保存的标准解
    standard_files = glob.glob(os.path.join(brute_force.save_dir, f"nqueens_{board_size}_all_*_solutions.json"))
    if standard_files:
        print(f"发现标准解文件: {standard_files[0]}")
        with open(standard_files[0], 'r') as f:
            standard_data = json.load(f)
            brute_force.solutions = standard_data["solutions"]
        print(f"已加载 {len(brute_force.solutions)} 个标准解")
    else:
        print("错误: 未找到标准解文件，请先运行brute_force.py生成标准解")
        return
    
    # 2. 检查solutions目录
    solutions_base_dir = "solutions"
    if not os.path.exists(solutions_base_dir):
        print(f"错误: 未找到解决方案基础目录 '{solutions_base_dir}'")
        return
        
    # 3. 获取算法目录列表
    algorithm_dirs = [d for d in os.listdir(solutions_base_dir) 
                    if os.path.isdir(os.path.join(solutions_base_dir, d))]
    
    if not algorithm_dirs:
        print(f"错误: 在 '{solutions_base_dir}' 目录中未找到任何算法子目录")
        return
        
    print(f"\n2. 找到 {len(algorithm_dirs)} 个算法目录: {', '.join(algorithm_dirs)}")
    
    # 4. 验证每个算法的解决方案
    for algorithm_name in algorithm_dirs:
        algorithm_dir = os.path.join(solutions_base_dir, algorithm_name)
        # 使用固定文件名查找
        solution_file = os.path.join(algorithm_dir, f"nqueens_{board_size}_solutions.json")
        
        if not os.path.exists(solution_file):
            print(f"\n算法 '{algorithm_name}' 目录下未找到解决方案文件，跳过")
            continue
            
        print(f"\n3. 验证算法 '{algorithm_name}' 的解决方案:")
        
        try:
            with open(solution_file, 'r') as f:
                solution_data = json.load(f)
                
            # 检查解决方案格式
            if "solutions" not in solution_data:
                print("  错误: 文件格式不正确，缺少'solutions'字段")
                continue
                
            solutions = solution_data["solutions"]
            if not isinstance(solutions, list):
                print("  错误: 'solutions'字段不是列表类型")
                continue
                
            # 提取文件信息
            last_updated = solution_data.get("last_updated", "未知")
            total_solutions = solution_data.get("total_solutions", len(solutions))
            time_taken = solution_data.get("time_taken", 0)
            generations = solution_data.get("generations", 0)
            parameters = solution_data.get("parameters", {})
            
            # 显示文件信息
            print(f"  文件信息: ")
            print(f"    上次更新时间: {last_updated}")
            print(f"    迭代次数: {generations}")
            print(f"    运行时间: {time_taken:.2f}秒")
            if parameters:
                print(f"    算法参数: {', '.join([f'{k}={v}' for k, v in parameters.items()])}")
            
            # 验证解决方案数量
            print(f"  文件包含 {len(solutions)} 个解")
            
            # 验证解
            problem = QueensProblem(board_size)
            valid_count = 0
            for solution in solutions:
                if problem.is_valid_solution(solution):
                    valid_count += 1
            
            valid_percentage = valid_count/len(solutions)*100 if solutions else 0
            print(f"  有效解数量: {valid_count}/{len(solutions)} ({valid_percentage:.2f}%)")
            
            # 与标准解比较
            print("  与标准解比较:")
            verify_result = brute_force.verify_solutions(solutions)
            
        except Exception as e:
            print(f"  处理文件时出错: {str(e)}")
    
    print("\n验证完成!")
    print("="*50)
    input("按回车键退出...")

if __name__ == "__main__":
    main() 