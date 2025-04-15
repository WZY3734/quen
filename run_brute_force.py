#!/usr/bin/env python
"""
N皇后问题暴力求解器
使用递归方法找到所有有效的解
"""
from queens.algorithms.brute_force import BruteForce

if __name__ == "__main__":
    print("="*50)
    print("N皇后问题 - 暴力求解器")
    print("="*50)
    
    board_size = 8  # 默认8皇后问题
    
    # 可以根据输入更改棋盘大小
    try:
        input_size = input("请输入棋盘大小 (默认为8): ")
        if input_size.strip():
            board_size = int(input_size)
            if board_size < 4:
                print("警告: 棋盘大小小于4时解较少或不存在")
            elif board_size > 10:
                print("警告: 棋盘大小大于10时计算可能非常耗时")
    except ValueError:
        print("输入无效，使用默认值8")
        
    print(f"开始求解 {board_size} 皇后问题...")
    solver = BruteForce(board_size)
    solutions = solver.solve()
    
    print("\n求解统计:")
    print(f"棋盘大小: {board_size} x {board_size}")
    print(f"找到的解数量: {len(solutions)}")
    
    # 显示部分解
    if solutions:
        print("\n前3个解:")
        for i, sol in enumerate(solutions[:3]):
            print(f"解 {i+1}: {sol}")
            
            # 打印棋盘可视化
            print("棋盘:")
            for row in range(board_size):
                line = ""
                for col in range(board_size):
                    if sol[col] == row:
                        line += "Q "
                    else:
                        line += ". "
                print(line)
            print()
            
    print("所有解已保存到文件中。")
    print("="*50) 