import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, RadioButtons, CheckButtons
import time
from .algorithms.genetic_algorithm import GeneticAlgorithm
from .algorithms.simulated_annealing import SimulatedAnnealing
from .algorithms.hill_climbing import HillClimbing
from .algorithms.backtracking import Backtracking

class QueensVisualizer:
    def __init__(self, problem, algorithms):
        self.problem = problem
        self.algorithms = algorithms
        self.current_algorithm = None
        self.solutions_found = set()
        self.start_time = None
        self.generation_count = 0
        
        # 初始化算法进度
        self.algorithm_progress = {}
        for alg in algorithms:
            self.algorithm_progress[alg.__class__.__name__] = {
                'solutions': set(),
                'generation_count': 0,
                'running': False,
                'animation': None,
                'start_time': None,
                'params': self._get_algorithm_params(alg)  # 添加参数保存
            }
        
        # Setup figure with custom style
        plt.style.use('default')
        plt.rcParams['figure.facecolor'] = '#f0f0f0'
        plt.rcParams['axes.facecolor'] = 'white'
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.color'] = '#d0d0d0'
        
        self.fig = plt.figure(figsize=(12, 8))
        self.fig.patch.set_facecolor('#f0f0f0')
        
        # Create main layout
        self.gs = plt.GridSpec(2, 2, width_ratios=[2, 1], height_ratios=[4, 1])
        
        # Chessboard subplot
        self.ax_board = plt.subplot(self.gs[0, 0])
        self.ax_board.set_aspect('equal')
        self.ax_board.axis('off')
        
        # Statistics subplot
        self.ax_stats = plt.subplot(self.gs[0, 1])
        self.ax_stats.axis('off')
        
        # Control panel
        self.ax_controls = plt.subplot(self.gs[1, :])
        self.ax_controls.axis('off')
        
        # Add algorithm selection radio buttons with custom style
        self.radio_buttons = RadioButtons(
            self.ax_controls, 
            [alg.__class__.__name__ for alg in algorithms],
            active=0
        )
        self.radio_buttons.on_clicked(self.select_algorithm)
        
        # Add start/stop button with custom style
        self.button_ax = plt.axes([0.4, 0.05, 0.2, 0.075])
        self.button = Button(self.button_ax, 'Start')
        self.button.on_clicked(self.toggle_animation)
        
        # Add reset button
        reset_ax = plt.axes([0.4, 0.15, 0.2, 0.1])
        self.reset_button = Button(reset_ax, 'Reset', color='#e74c3c', hovercolor='#c0392b')
        self.reset_button.on_clicked(self.reset_algorithm)
        
        # Set initial algorithm
        self.select_algorithm(algorithms[0].__class__.__name__)
        
        # 调整布局
        self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2)
        
    def _get_algorithm_params(self, algorithm):
        """获取算法的初始化参数"""
        if isinstance(algorithm, GeneticAlgorithm):
            return {
                'population_size': algorithm.population_size,
                'mutation_rate': algorithm.mutation_rate
            }
        elif isinstance(algorithm, SimulatedAnnealing):
            return {
                'initial_temperature': algorithm.initial_temperature,
                'cooling_rate': algorithm.cooling_rate,
                'min_temperature': algorithm.min_temperature
            }
        elif isinstance(algorithm, HillClimbing):
            return {}
        elif isinstance(algorithm, Backtracking):
            return {}
        return {}
        
    def _create_algorithm(self, algorithm_class, params):
        """根据参数创建新的算法实例"""
        if algorithm_class == GeneticAlgorithm:
            return GeneticAlgorithm(
                population_size=params['population_size'],
                mutation_rate=params['mutation_rate'],
                problem=self.problem
            )
        elif algorithm_class == SimulatedAnnealing:
            return SimulatedAnnealing(
                initial_temperature=params['initial_temperature'],
                cooling_rate=params['cooling_rate'],
                min_temperature=params['min_temperature'],
                problem=self.problem
            )
        elif algorithm_class == HillClimbing:
            return HillClimbing(self.problem)
        elif algorithm_class == Backtracking:
            return Backtracking(self.problem)
        return None
        
    def select_algorithm(self, label):
        """选择要显示的算法"""
        # 停止当前算法的动画
        if self.current_algorithm:
            current_label = self.current_algorithm.__class__.__name__
            self.algorithm_progress[current_label]['running'] = False
            if self.algorithm_progress[current_label]['animation']:
                self.algorithm_progress[current_label]['animation'].event_source.stop()
                self.algorithm_progress[current_label]['animation'] = None
            
        # 选择新算法
        for alg in self.algorithms:
            if alg.__class__.__name__ == label:
                self.current_algorithm = alg
                break
            
        # 更新按钮状态
        progress = self.algorithm_progress[label]
        self.button.label.set_text('Start' if not progress['running'] else 'Stop')
        
        # 更新显示
        self.draw_board(self.current_algorithm.get_best_solution())
        self.update_stats()
        
    def toggle_animation(self, event):
        """开始或停止当前算法的动画"""
        if not self.current_algorithm:
            return
        
        label = self.current_algorithm.__class__.__name__
        progress = self.algorithm_progress[label]
        
        if progress['running']:
            # 停止当前算法
            progress['running'] = False
            self.button.label.set_text('Start')
            if progress['animation']:
                progress['animation'].event_source.stop()
                progress['animation'] = None
            
            # 保存找到的解
            if hasattr(self.current_algorithm, 'save_solutions'):
                self.current_algorithm.save_solutions()
        else:
            # 启动当前算法
            progress['running'] = True
            self.button.label.set_text('Stop')
            if progress['start_time'] is None:
                progress['start_time'] = time.time()
                
            # 创建新的动画
            def update(frame):
                self.update(frame, label)
                return self.ax_board, self.ax_stats
                
            progress['animation'] = FuncAnimation(
                self.fig, 
                update,
                interval=100,
                cache_frame_data=False,
                save_count=1000,
                blit=True
            )
            
    def reset_algorithm(self, event):
        """重置当前算法的进度"""
        if not self.current_algorithm:
            return
            
        label = self.current_algorithm.__class__.__name__
        progress = self.algorithm_progress[label]
        
        # 停止当前动画
        if progress['running']:
            progress['running'] = False
            self.button.label.set_text('Start')
            if progress['animation']:
                progress['animation'].event_source.stop()
                progress['animation'] = None
                
        # 创建新的算法实例
        algorithm_class = type(self.current_algorithm)
        new_algorithm = self._create_algorithm(algorithm_class, progress['params'])
        
        # 更新算法实例
        for i, alg in enumerate(self.algorithms):
            if alg.__class__.__name__ == label:
                self.algorithms[i] = new_algorithm
                self.current_algorithm = new_algorithm
                break
                
        # 重置进度
        progress['solutions'] = set()
        progress['generation_count'] = 0
        progress['start_time'] = None
        
        # 更新显示
        self.draw_board(self.current_algorithm.get_best_solution())
        self.update_stats()
        
    def draw_board(self, solution):
        """绘制棋盘和皇后"""
        self.ax_board.clear()
        board = np.zeros((self.problem.board_size, self.problem.board_size))
        
        # 创建棋盘图案
        for i in range(self.problem.board_size):
            for j in range(self.problem.board_size):
                if (i + j) % 2 == 0:
                    board[i, j] = 1
                    
        self.ax_board.imshow(board, cmap='binary', vmin=0, vmax=1)
        
        # 放置皇后
        for col, row in enumerate(solution):
            self.ax_board.text(col, row, '♛', fontsize=24, 
                             ha='center', va='center', color='#e74c3c')
            
        self.ax_board.set_xticks([])
        self.ax_board.set_yticks([])
        self.ax_board.grid(True, color='black', linewidth=1)
        
    def update_stats(self):
        """更新统计信息显示"""
        self.ax_stats.clear()
        if self.current_algorithm:
            label = self.current_algorithm.__class__.__name__
            progress = self.algorithm_progress[label]
            
            # 计算运行时间
            elapsed_time = 0.0
            if progress['start_time'] is not None:
                elapsed_time = time.time() - progress['start_time']
                
            # 获取算法特定信息
            if isinstance(self.current_algorithm, GeneticAlgorithm):
                algorithm_info = f"Population: {self.current_algorithm.population_size}, Mutation: {self.current_algorithm.mutation_rate:.2f}"
                # 同步解计数
                if hasattr(self.current_algorithm, 'solutions'):
                    progress['solutions'] = set(map(tuple, self.current_algorithm.solutions))
            elif isinstance(self.current_algorithm, SimulatedAnnealing):
                algorithm_info = f"Temp: {self.current_algorithm.temperature:.2f}, Cooling: {self.current_algorithm.cooling_rate:.2f}"
                # 同步解计数
                if hasattr(self.current_algorithm, 'solutions'):
                    progress['solutions'] = set(map(tuple, self.current_algorithm.solutions))
            elif isinstance(self.current_algorithm, HillClimbing):
                algorithm_info = f"Restarts: {self.current_algorithm.restarts}/{self.current_algorithm.max_restarts}"
                # 同步解计数 
                if hasattr(self.current_algorithm, 'solutions'):
                    progress['solutions'] = set(map(tuple, self.current_algorithm.solutions))
            elif isinstance(self.current_algorithm, Backtracking):
                algorithm_info = f"Using iterative backtracking"
                # 同步解计数到可视化类
                progress['solutions'] = set(map(tuple, self.current_algorithm.solutions))
            else:
                algorithm_info = ""
                
            stats = [
                f"Algorithm: {label}",
                algorithm_info,
                f"Solutions found: {len(progress['solutions'])}",
                f"Generations/Iterations: {progress['generation_count']}",
                f"Time elapsed: {elapsed_time:.2f}s",
                f"Current fitness: {self.current_algorithm.get_best_fitness():.2f}"
            ]
            
            for i, stat in enumerate(stats):
                self.ax_stats.text(0.1, 0.9 - i*0.15, stat, fontsize=12,
                                 bbox=dict(facecolor='white', alpha=0.8,
                                         edgecolor='none', boxstyle='round,pad=0.5'))
                
        self.ax_stats.axis('off')
        
    def update(self, frame, label):
        """更新动画"""
        if not self.algorithm_progress[label]['running']:
            return
        
        # 限制更新频率
        if frame % 5 != 0:  # 每5帧更新一次
            return
        
        # 执行算法步骤
        self.current_algorithm.step()
        
        # 获取当前解
        solution = self.current_algorithm.get_best_solution()
        
        # 检查算法是否仍在求解 (安全检查is_solving属性)
        if hasattr(self.current_algorithm, 'is_solving') and not self.current_algorithm.is_solving:
            self.algorithm_progress[label]['running'] = False
            self.button.label.set_text('Start')
            if self.algorithm_progress[label]['animation']:
                self.algorithm_progress[label]['animation'].event_source.stop()
                self.algorithm_progress[label]['animation'] = None
        
        # 更新显示
        self.draw_board(solution)
        self.update_stats()
        
        # 同步解计数
        if hasattr(self.current_algorithm, 'solutions'):
            self.algorithm_progress[label]['solutions'] = set(map(tuple, self.current_algorithm.solutions))
        else:
            # 记录找到的解
            if self.problem.is_valid_solution(solution):
                solution_tuple = tuple(solution)
                if solution_tuple not in self.algorithm_progress[label]['solutions']:
                    self.algorithm_progress[label]['solutions'].add(solution_tuple)
        
        # 更新迭代次数
        if isinstance(self.current_algorithm, Backtracking):
            self.algorithm_progress[label]['generation_count'] = self.current_algorithm.generation_count
        else:
            self.algorithm_progress[label]['generation_count'] += 1
        
    def show(self):
        """显示可视化界面"""
        plt.show() 