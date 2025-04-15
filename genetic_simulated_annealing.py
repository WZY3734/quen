import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random

class GeneticAlgorithm:
    def __init__(self, population_size, chromosome_length, mutation_rate):
        self.population_size = population_size
        self.chromosome_length = chromosome_length
        self.mutation_rate = mutation_rate
        self.population = self.initialize_population()
        
    def initialize_population(self):
        return np.random.randint(2, size=(self.population_size, self.chromosome_length))
    
    def fitness(self, chromosome):
        # 这里使用简单的适应度函数：计算1的个数
        return np.sum(chromosome)
    
    def select_parents(self):
        fitnesses = np.array([self.fitness(chromosome) for chromosome in self.population])
        total_fitness = np.sum(fitnesses)
        probabilities = fitnesses / total_fitness
        parent_indices = np.random.choice(self.population_size, size=2, p=probabilities)
        return self.population[parent_indices[0]], self.population[parent_indices[1]]
    
    def crossover(self, parent1, parent2):
        crossover_point = random.randint(1, self.chromosome_length - 1)
        child1 = np.concatenate((parent1[:crossover_point], parent2[crossover_point:]))
        child2 = np.concatenate((parent2[:crossover_point], parent1[crossover_point:]))
        return child1, child2
    
    def mutate(self, chromosome):
        for i in range(len(chromosome)):
            if random.random() < self.mutation_rate:
                chromosome[i] = 1 - chromosome[i]
        return chromosome
    
    def evolve(self):
        new_population = []
        for _ in range(self.population_size // 2):
            parent1, parent2 = self.select_parents()
            child1, child2 = self.crossover(parent1, parent2)
            child1 = self.mutate(child1)
            child2 = self.mutate(child2)
            new_population.extend([child1, child2])
        self.population = np.array(new_population)

class SimulatedAnnealing:
    def __init__(self, initial_temperature, cooling_rate, min_temperature):
        self.temperature = initial_temperature
        self.cooling_rate = cooling_rate
        self.min_temperature = min_temperature
        self.current_solution = np.random.randint(2, size=20)
        self.best_solution = self.current_solution.copy()
        
    def fitness(self, solution):
        return np.sum(solution)
    
    def get_neighbor(self):
        neighbor = self.current_solution.copy()
        index = random.randint(0, len(neighbor) - 1)
        neighbor[index] = 1 - neighbor[index]
        return neighbor
    
    def accept_solution(self, new_solution):
        current_fitness = self.fitness(self.current_solution)
        new_fitness = self.fitness(new_solution)
        
        if new_fitness > current_fitness:
            return True
        else:
            probability = np.exp((new_fitness - current_fitness) / self.temperature)
            return random.random() < probability
    
    def step(self):
        if self.temperature <= self.min_temperature:
            return False
            
        new_solution = self.get_neighbor()
        if self.accept_solution(new_solution):
            self.current_solution = new_solution
            if self.fitness(new_solution) > self.fitness(self.best_solution):
                self.best_solution = new_solution.copy()
        
        self.temperature *= self.cooling_rate
        return True

def visualize_algorithms():
    # 设置图形
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle('Genetic Algorithm and Simulated Annealing Visualization')
    
    # 初始化算法
    ga = GeneticAlgorithm(population_size=50, chromosome_length=20, mutation_rate=0.1)
    sa = SimulatedAnnealing(initial_temperature=100, cooling_rate=0.95, min_temperature=0.1)
    
    # 存储历史数据用于绘图
    ga_history = []
    sa_history = []
    
    def update(frame):
        # 更新遗传算法
        ga.evolve()
        best_fitness = max([ga.fitness(chromosome) for chromosome in ga.population])
        ga_history.append(best_fitness)
        
        # 更新模拟退火
        sa.step()
        sa_history.append(sa.fitness(sa.best_solution))
        
        # 清除之前的图形
        ax1.clear()
        ax2.clear()
        
        # 绘制遗传算法结果
        ax1.plot(ga_history, 'b-')
        ax1.set_title('Genetic Algorithm')
        ax1.set_xlabel('Generation')
        ax1.set_ylabel('Best Fitness')
        
        # 绘制模拟退火结果
        ax2.plot(sa_history, 'r-')
        ax2.set_title('Simulated Annealing')
        ax2.set_xlabel('Iteration')
        ax2.set_ylabel('Best Fitness')
        
        plt.tight_layout()
    
    # 创建动画
    ani = FuncAnimation(fig, update, frames=100, interval=200, repeat=False)
    plt.show()

if __name__ == "__main__":
    visualize_algorithms() 