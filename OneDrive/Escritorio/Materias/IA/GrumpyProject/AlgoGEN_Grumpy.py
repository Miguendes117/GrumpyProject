import tkinter as tk
from tkinter import messagebox
import random
import numpy as np
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import logging

# Configuración de logging
logging.basicConfig(filename='path_finder.log', level=logging.INFO)

# Parámetros
cell_size = 40
grid_width = 10
grid_height = 10
counter = 0

# Estados del sistema
class State:
    INICIO = "Inicio"
    BUSCANDO_CAMINO = "Buscando Camino (Genético)"
    MOVIENDO_JUGADOR = "Moviendo Jugador"
    LLEGADA = "Llegada"
    SIN_CAMINO = "Sin Camino"

current_state = State.INICIO
current_path = None

# Parámetros del algoritmo genético
POPULATION_SIZE = 100
GENERATIONS = 200
MUTATION_RATE = 0.15
ELITISM_RATE = 0.2
MAX_ATTEMPTS = 3

# Definir costes según el tipo de terreno
costs = {"normal": 1, "moderate": 3, "difficult": 5, "peligroso": 20}

# Crear la ventana
window = tk.Tk()
window.title("Grumpy - Algoritmo Genético con Posición Aleatoria")

canvas = tk.Canvas(window, width=grid_width * cell_size, height=grid_height * cell_size, bg="white")
canvas.pack()

# Contador
counter_label = tk.Label(window, text=f"Contador: {counter}", font=("Arial", 12))
counter_label.pack()

# Estado del sistema
state_label = tk.Label(window, text=f"Estado: {current_state}", font=("Arial", 12))
state_label.pack()

# Gráfica de evolución
fig, ax = plt.subplots(figsize=(5, 3))
ax.set_title("Evolución del Fitness")
ax.set_xlabel("Generación")
ax.set_ylabel("Mejor Fitness")
canvas_plot = FigureCanvasTkAgg(fig, master=window)
canvas_plot.get_tk_widget().pack()

# Función para cargar imágenes
def load_image(path, size):
    try:
        img = Image.open(path).resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        logging.error(f"Error cargando imagen {path}: {e}")
        img = Image.new('RGB', size, color='gray')
        return ImageTk.PhotoImage(img)

img_size = (cell_size - 10, cell_size - 10)
panda_img = load_image("images/panda.jpg", img_size)
moneda_img = load_image("images/moneda.jpg", img_size)
grumpy_img = load_image("images/grumpy.jpg", img_size)

# Configuración del terreno
obstacles = {(2, 3), (4, 7), (6, 2), (8, 6)}
moderate_terrain = {(1, 4), (3, 3), (9, 5), (6, 8)}
difficult_terrain = {(4, 8), (7, 7), (5, 5)}
grumpy_pos = (5, 3)
danger_zones = {(grumpy_pos[0] - 1, grumpy_pos[1]), (grumpy_pos[0] + 1, grumpy_pos[1]),
                (grumpy_pos[0], grumpy_pos[1] - 1), (grumpy_pos[0], grumpy_pos[1] + 1)}

# Posiciones fijas
goal_pos = (9, 9)
player_pos = None  # Se asignará aleatoriamente

# Función para generar posición aleatoria válida para el panda
def generate_random_position():
    # Celdas prohibidas: obstáculos, meta, grumpy y sus adyacentes
    forbidden_positions = (
        obstacles | 
        {goal_pos} | 
        {(goal_pos[0] + dx, goal_pos[1] + dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1]} |
        {grumpy_pos} |
        {(grumpy_pos[0] + dx, grumpy_pos[1] + dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1]}
    )
    
    # Generar todas las posiciones posibles
    all_positions = [(x, y) for x in range(grid_width) for y in range(grid_height)]
    
    # Filtrar posiciones válidas
    valid_positions = [pos for pos in all_positions if pos not in forbidden_positions]
    
    if not valid_positions:
        logging.error("No hay posiciones válidas para el panda")
        return None
    
    return random.choice(valid_positions)

# Dibujar cuadrícula
def draw_grid():
    canvas.delete("all")
    
    for i in range(grid_width):
        for j in range(grid_height):
            x1, y1 = i * cell_size, j * cell_size
            x2, y2 = x1 + cell_size, y1 + cell_size
            color = "light green"

            if (i, j) in obstacles:
                color = "black"
            elif (i, j) in moderate_terrain:
                color = "yellow"
            elif (i, j) in difficult_terrain:
                color = "red"
            elif (i, j) in danger_zones:
                color = "orange"

            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
            if (i, j) in danger_zones:
                canvas.create_text(x1 + cell_size / 2, y1 + cell_size / 2, 
                                 text="❌", font=("Arial", 18, "bold"), fill="red")
    
    # Dibujar elementos fijos
    canvas.create_image(
        goal_pos[0] * cell_size + cell_size // 2,
        goal_pos[1] * cell_size + cell_size // 2,
        image=moneda_img
    )
    
    canvas.create_image(
        grumpy_pos[0] * cell_size + cell_size // 2,
        grumpy_pos[1] * cell_size + cell_size // 2,
        image=grumpy_img
    )

# Función para verificar si la meta es alcanzable
def is_goal_reachable(start_pos):
    visited = set()
    queue = [start_pos]
    
    while queue:
        current = queue.pop(0)
        if current == goal_pos:
            return True
            
        if current in visited:
            continue
            
        visited.add(current)
        
        moves = [
            (current[0], current[1] + 1),  # Abajo
            (current[0], current[1] - 1),  # Arriba
            (current[0] + 1, current[1]),  # Derecha
            (current[0] - 1, current[1])   # Izquierda
        ]
        
        for move in moves:
            if (0 <= move[0] < grid_width and 0 <= move[1] < grid_height and 
                move not in obstacles and move not in visited):
                queue.append(move)
    
    return False

# Función para calcular costo de movimiento
def calculate_move_cost(pos):
    if pos in obstacles:
        return float('inf')
    elif pos in moderate_terrain:
        return costs["moderate"]
    elif pos in difficult_terrain:
        return costs["difficult"]
    elif pos in danger_zones:
        return costs["peligroso"]
    else:
        return costs["normal"]

# Algoritmo Genético
class GeneticPathFinder:
    def __init__(self, start, end, max_steps=30):
        self.start = start
        self.end = end
        self.max_steps = max_steps
        self.population = []
        self.best_fitness_history = []
        
    def initialize_population(self):
        self.population = []
        for _ in range(POPULATION_SIZE):
            path = [self.start]
            current = self.start
            
            for _ in range(self.max_steps - 1):
                if current == self.end:
                    break
                    
                moves = [
                    (current[0], current[1] + 1),  # Abajo
                    (current[0], current[1] - 1),  # Arriba
                    (current[0] + 1, current[1]),  # Derecha
                    (current[0] - 1, current[1])   # Izquierda
                ]
                
                valid_moves = []
                for move in moves:
                    if (0 <= move[0] < grid_width and 0 <= move[1] < grid_height and 
                        move not in obstacles):
                        valid_moves.append(move)
                
                if not valid_moves:
                    break
                    
                next_pos = random.choice(valid_moves)
                path.append(next_pos)
                current = next_pos
                
                if current == self.end:
                    break
                    
            self.population.append(path)
    
    def fitness(self, path):
        if not path:
            return 0.001
            
        end_bonus = 3 if path[-1] == self.end else 0
        
        total_cost = 0
        visited = set()
        repeated = 0
        
        for i in range(len(path) - 1):
            current = path[i]
            next_pos = path[i + 1]
            total_cost += calculate_move_cost(next_pos)
            
            if next_pos in visited:
                repeated += 2
            visited.add(next_pos)
            
            if abs(current[0] - next_pos[0]) + abs(current[1] - next_pos[1]) != 1:
                total_cost += 50
        
        fitness = (1 / (total_cost + len(path) * 0.05 + repeated + 0.1)) * (1 + end_bonus)
        return fitness
    
    def selection(self):
        tournament_size = max(3, POPULATION_SIZE // 10)
        selected = []
        
        for _ in range(POPULATION_SIZE):
            contestants = random.sample(self.population, tournament_size)
            winner = max(contestants, key=lambda x: self.fitness(x))
            selected.append(winner.copy())
            
        return selected
    
    def crossover(self, parent1, parent2):
        min_len = min(len(parent1), len(parent2))
        if min_len <= 1:
            return parent1, parent2
            
        crossover_point = random.randint(1, min_len - 1)
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        
        return child1, child2
    
    def mutate(self, path):
        if len(path) <= 1 or random.random() > MUTATION_RATE:
            return path
            
        mut_point = random.randint(1, len(path) - 1)
        prev_pos = path[mut_point - 1]
        
        moves = [
            (prev_pos[0], prev_pos[1] + 1),  # Abajo
            (prev_pos[0], prev_pos[1] - 1),  # Arriba
            (prev_pos[0] + 1, prev_pos[1]),  # Derecha
            (prev_pos[0] - 1, prev_pos[1])   # Izquierda
        ]
        
        valid_moves = []
        for move in moves:
            if (0 <= move[0] < grid_width and 0 <= move[1] < grid_height and 
                move not in obstacles):
                valid_moves.append(move)
        
        if valid_moves:
            def distance_to_goal(move):
                return abs(move[0] - self.end[0]) + abs(move[1] - self.end[1])
            
            valid_moves.sort(key=distance_to_goal)
            path[mut_point] = valid_moves[0]
            
        return path
    
    def evolve(self):
        self.population.sort(key=lambda x: self.fitness(x), reverse=True)
        elite_size = int(POPULATION_SIZE * ELITISM_RATE)
        new_population = self.population[:elite_size]
        
        selected = self.selection()
        
        for i in range(0, len(selected) - 1, 2):
            parent1, parent2 = selected[i], selected[i + 1]
            child1, child2 = self.crossover(parent1, parent2)
            new_population.extend([child1, child2])
        
        for i in range(elite_size, len(new_population)):
            new_population[i] = self.mutate(new_population[i])
            
        self.population = new_population
        
        best_fitness = max(self.fitness(p) for p in self.population)
        self.best_fitness_history.append(best_fitness)
        
        return best_fitness
    
    def find_best_path(self):
        self.initialize_population()
        best_path = None
        best_fitness = 0
        
        for generation in range(GENERATIONS):
            current_fitness = self.evolve()
            
            ax.clear()
            ax.plot(self.best_fitness_history, 'b-')
            ax.set_title("Evolución del Fitness")
            ax.set_xlabel("Generación")
            ax.set_ylabel("Mejor Fitness")
            canvas_plot.draw()
            window.update()
            
            current_best = max(self.population, key=lambda x: self.fitness(x))
            current_best_fitness = self.fitness(current_best)
            
            if current_best_fitness > best_fitness:
                best_path = current_best
                best_fitness = current_best_fitness
            
            if best_path and best_path[-1] == self.end and generation > 20:
                if best_fitness > 0.8 * max(self.best_fitness_history):
                    break
        
        return best_path if best_path and best_fitness > 0.1 else None

# Funciones del juego
def change_state(new_state):
    global current_state, current_path
    current_state = new_state
    state_label.config(text=f"Estado: {current_state}")
    logging.info(f"Cambio de estado a: {current_state}")
    
    if current_state == State.BUSCANDO_CAMINO:
        window.after(100, find_path)
    elif current_state == State.MOVIENDO_JUGADOR and current_path:
        window.after(100, lambda: move_player(current_path))
    elif current_state == State.LLEGADA:
        messagebox.showinfo("Éxito", f"¡Llegaste a la meta con puntuación {counter}!")
        show_restart_dialog()
    elif current_state == State.SIN_CAMINO:
        show_restart_dialog()

def change_counter(new_pos):
    global counter
    if new_pos in moderate_terrain:
        counter += 3
    elif new_pos in difficult_terrain:
        counter += 5
    elif new_pos in danger_zones:
        counter += 10
    else:
        counter += 1
    counter_label.config(text=f"Contador: {counter}")

def find_path():
    global current_path, player_pos
    attempt = 0
    
    if not is_goal_reachable(player_pos):
        messagebox.showwarning("Meta inalcanzable", 
                             "No hay camino posible desde la posición actual.")
        change_state(State.SIN_CAMINO)
        return
    
    while attempt < MAX_ATTEMPTS:
        logging.info(f"Intento {attempt + 1} de encontrar camino desde {player_pos}")
        finder = GeneticPathFinder(player_pos, goal_pos)
        current_path = finder.find_best_path()
        
        if current_path:
            logging.info(f"Camino encontrado: {current_path}")
            canvas.delete("path")
            for i in range(len(current_path) - 1):
                x1, y1 = current_path[i][0] * cell_size + cell_size // 2, current_path[i][1] * cell_size + cell_size // 2
                x2, y2 = current_path[i+1][0] * cell_size + cell_size // 2, current_path[i+1][1] * cell_size + cell_size // 2
                canvas.create_line(x1, y1, x2, y2, fill="blue", width=2, tags="path")
            
            change_state(State.MOVIENDO_JUGADOR)
            return
        
        attempt += 1
        logging.warning(f"Intento {attempt} fallido. Reintentando...")
    
    logging.error("No se pudo encontrar un camino después de varios intentos")
    change_state(State.SIN_CAMINO)

def move_player(path, index=1):
    global player_pos
    if index < len(path):
        new_pos = path[index]
        new_x = new_pos[0] * cell_size + cell_size // 2
        new_y = new_pos[1] * cell_size + cell_size // 2
        change_counter(new_pos)
        canvas.coords(player, new_x, new_y)
        player_pos = new_pos
        window.after(300, lambda: move_player(path, index + 1))
    else:
        change_state(State.LLEGADA)

def show_restart_dialog():
    result = messagebox.askyesno("Juego terminado", 
                               "¿Quieres jugar otra vez con una nueva posición inicial?")
    if result:
        reset_game()
    else:
        window.quit()

def reset_game():
    global player_pos, counter, current_state, current_path, player
    counter = 0
    current_path = None
    
    # Generar nueva posición aleatoria para el panda
    player_pos = generate_random_position()
    if player_pos is None:
        messagebox.showerror("Error", "No se pudo encontrar una posición válida para el panda.")
        window.quit()
        return
    
    # Redibujar todo
    draw_grid()
    
    # Dibujar al panda en su nueva posición
    player = canvas.create_image(
        player_pos[0] * cell_size + cell_size // 2,
        player_pos[1] * cell_size + cell_size // 2,
        image=panda_img
    )
    
    counter_label.config(text=f"Contador: {counter}")
    change_state(State.INICIO)
    window.after(1000, lambda: change_state(State.BUSCANDO_CAMINO))

# Inicialización del juego
def initialize_game():
    global player_pos, player
    
    player_pos = generate_random_position()
    if player_pos is None:
        messagebox.showerror("Error", "No hay posiciones válidas para el panda.")
        window.quit()
        return
    
    draw_grid()
    
    player = canvas.create_image(
        player_pos[0] * cell_size + cell_size // 2,
        player_pos[1] * cell_size + cell_size // 2,
        image=panda_img
    )
    
    if is_goal_reachable(player_pos):
        change_state(State.BUSCANDO_CAMINO)
    else:
        messagebox.showwarning("Configuración inválida", 
                             "No hay camino posible desde la posición inicial.")
        change_state(State.SIN_CAMINO)

initialize_game()
window.mainloop()