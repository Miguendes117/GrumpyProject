import tkinter as tk
from tkinter import messagebox
import networkx as nx
from PIL import Image, ImageTk
import random
import numpy as np

# Parámetros del juego
cell_size = 40
grid_width = 10
grid_height = 10
counter = 0
nivel_actual = 1

# Variables globales para los elementos gráficos
player = None
goal = None
grumpy_dibujo = None

# Variables para el mapa
obstacles = set()
moderate_terrain = set()
difficult_terrain = set()

# Clase DNA para el algoritmo genético
class DNA:
    def __init__(self, target, mutation_rate=0.1, n_individuals=4, n_selection=2, n_generations=1):
        self.target = target
        self.mutation_rate = mutation_rate
        self.n_individuals = n_individuals
        self.n_selection = n_selection
        self.n_generations = n_generations

    def create_individual(self):
        return [
            random.randint(1, 2),   # Movilidad (1 o 2)
            random.randint(1, 3),   # Velocidad (1-3)
            random.randint(1, 9),   # Agresividad (1-9)
            random.randint(1, 3)    # Visibilidad (1-3)
        ]

    def create_population(self):
        return [self.create_individual() for _ in range(self.n_individuals)]

    def fitness(self, individual):
        score = 0
        for i in range(len(individual)):
            target_val = max(1, self.target[i])
            ratio = min(individual[i], target_val) / target_val
            score += ratio ** 2
            
            if individual[i] > target_val:
                score += 0.2 * (1 - (individual[i] - target_val)/target_val)
        return score
    
    def selection(self, population):
        fitnesses = [self.fitness(ind) for ind in population]
        total_fitness = sum(fitnesses)
        probs = [f/total_fitness for f in fitnesses]
        return random.choices(population, weights=probs, k=self.n_selection)
    
    def reproduction(self, population, selected):
        new_population = []
        for _ in range(len(population)):
            parents = random.sample(selected, 2)
            child = [
                parents[random.randint(0, 1)][0],  # Movilidad
                parents[random.randint(0, 1)][1],  # Velocidad
                parents[random.randint(0, 1)][2],  # Agresividad
                parents[random.randint(0, 1)][3]   # Visibilidad
            ]
            new_population.append(child)
        return new_population
    
    def mutation(self, population):
        for i in range(len(population)):
            if random.random() < self.mutation_rate:
                gene = random.randint(0, 3)
                if gene == 0:  # Movilidad
                    population[i][gene] = random.randint(1, 2)
                else:
                    change = random.choice([-1, 1])
                    population[i][gene] = max(1, min(3, population[i][gene] + change))
        return population
    
    def run_geneticalgo(self):
        population = self.create_population()
        for _ in range(self.n_generations):
            selected = self.selection(population)
            population = self.reproduction(population, selected)
            population = self.mutation(population)
        
        top_3 = sorted(population, key=lambda x: self.fitness(x), reverse=True)[:3]
        return random.choice(top_3)

class Grumpus:
    def __init__(self, nivel):
        self.nivel = nivel
        self.genes = self.generar_genes()
        
        # Asignar características basadas en genes
        self.movilidad = self.genes[0]  # 1 o 2 (1: no se mueve, 2: se mueve)
        self.velocidad = self.genes[1]  # 1-3
        self.agresividad = 0.1 + (self.genes[2] / 10)  # 0.2-1.0
        self.visibilidad = self.genes[3]  # 1-3
        self.movimientos_player = 0  # Contador de movimientos del jugador
        
    def generar_genes(self):
        # Definimos objetivos basados en el nivel
        target = [
            min(2, max(1, self.nivel)),  # Movilidad
            min(3, max(1, self.nivel)),  # Velocidad
            min(9, max(1, self.nivel * 2)),  # Agresividad
            min(3, max(1, self.nivel))   # Visibilidad
        ]
        
        model = DNA(target=target)
        return model.run_geneticalgo()
        
    def puede_mover(self):
        if self.movilidad == 1:  # 1 = no se mueve
            return False
            
        self.movimientos_player += 1
        
        # Lógica de velocidad
        if self.velocidad == 1 and self.movimientos_player % 3 == 0:
            self.movimientos_player = 0
            return True
        elif self.velocidad == 2 and self.movimientos_player % 2 == 0:
            self.movimientos_player = 0
            return True
        elif self.velocidad >= 3:
            self.movimientos_player = 0
            return True
            
        return False
    
    def get_rango_vision(self):
        # Devuelve el rango de visión según el nivel de visibilidad
        if self.visibilidad == 1:
            return 3  # 1 casilla alrededor
        elif self.visibilidad == 2:
            return 6  # 3 casillas alrededor
        else:
            return 15  # 7 casillas alrededor

# Función para generar un mapa aleatorio
def generar_mapa_aleatorio():
    global obstacles, moderate_terrain, difficult_terrain
    
    # Limpiar los conjuntos existentes
    obstacles.clear()
    moderate_terrain.clear()
    difficult_terrain.clear()
    
    # Generar obstáculos (10-15% del mapa)
    num_obstacles = random.randint(10, 15)
    for _ in range(num_obstacles):
        x = random.randint(0, grid_width-1)
        y = random.randint(0, grid_height-1)
        # No colocar obstáculos en las posiciones iniciales o finales
        if (x, y) != (0, 0) and (x, y) != (9, 9):
            obstacles.add((x, y))
    
    # Generar terreno moderado (5-10% del mapa)
    num_moderate = random.randint(5, 10)
    for _ in range(num_moderate):
        x = random.randint(0, grid_width-1)
        y = random.randint(0, grid_height-1)
        if (x, y) not in obstacles and (x, y) != (0, 0) and (x, y) != (9, 9):
            moderate_terrain.add((x, y))
    
    # Generar terreno difícil (3-6% del mapa)
    num_difficult = random.randint(3, 6)
    for _ in range(num_difficult):
        x = random.randint(0, grid_width-1)
        y = random.randint(0, grid_height-1)
        if (x, y) not in obstacles and (x, y) not in moderate_terrain and (x, y) != (0, 0) and (x, y) != (9, 9):
            difficult_terrain.add((x, y))

# Configuración inicial
grumpus = Grumpus(nivel_actual)

# Crear ventana
window = tk.Tk()
window.title(f"Grumpy - Nivel {nivel_actual}")

# Configuración del canvas
canvas = tk.Canvas(window, width=grid_width*cell_size, height=grid_height*cell_size, bg="white")
canvas.pack()

# Etiquetas de información
info_frame = tk.Frame(window)
info_frame.pack()

tk.Label(info_frame, text=f"Nivel: {nivel_actual}", font=("Arial", 12)).grid(row=0, column=0)
tk.Label(info_frame, text=f"Contador: {counter}", font=("Arial", 12)).grid(row=0, column=1)
genes_text = f"Grumpus - Mov: {'Sí' if grumpus.movilidad == 2 else 'No'} Vel: {grumpus.velocidad} Agr: {grumpus.agresividad:.1f} Vis: {grumpus.visibilidad}"
tk.Label(info_frame, text=genes_text, font=("Arial", 10)).grid(row=1, column=0, columnspan=2)

# Crear grafo del mapa
graph = nx.grid_2d_graph(grid_width, grid_height)

# Posiciones iniciales
player_pos = (0, 0)
goal_pos = (9, 9)
grumpy_pos = (5, 3)
danger_zones = set()

# Función para actualizar el grafo con el mapa actual
def actualizar_grafo():
    global graph, danger_zones
    
    # Reiniciar el grafo
    graph = nx.grid_2d_graph(grid_width, grid_height)
    
    # Configurar pesos del grafo
    for i, j in graph.edges():
        if i in moderate_terrain or j in moderate_terrain:
            graph[i][j]['weight'] = 3
        elif i in difficult_terrain or j in difficult_terrain:
            graph[i][j]['weight'] = 5
        elif i in danger_zones or j in danger_zones:
            graph[i][j]['weight'] = 20
        else:
            graph[i][j]['weight'] = 1

    # Eliminar nodos obstáculos
    for obstacle in obstacles:
        if graph.has_node(obstacle):
            graph.remove_node(obstacle)

# Dibujar el mapa
def dibujar_mapa():
    for i in range(grid_width):
        for j in range(grid_height):
            x1, y1 = i * cell_size, j * cell_size
            x2, y2 = x1 + cell_size, y1 + cell_size

            if (i, j) in obstacles:
                color = "black"  # Obstáculo
            elif (i, j) in moderate_terrain:
                color = "yellow"  # Terreno mediano
            elif (i, j) in difficult_terrain:
                color = "red"  # Terreno difícil
            elif (i, j) in danger_zones:  # Celdas naranjas
                color = "orange"
            else:
                color = "light green"  # Terreno normal

            # Dibujar la celda
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

            # Si la celda es naranja, agregar la ❌
            if (i, j) in danger_zones:
                canvas.create_text(x1 + cell_size / 2, y1 + cell_size / 2, text="❌", font=("Arial", 18, "bold"), fill="red")

# Cargar imágenes (simuladas)
try:
    panda_img = Image.open("images/panda.jpg").resize((cell_size-10, cell_size-10))
    panda_img = ImageTk.PhotoImage(panda_img)
    moneda_img = Image.open("images/moneda.jpg").resize((cell_size-10, cell_size-10))
    moneda_img = ImageTk.PhotoImage(moneda_img)
    grumpy_img = Image.open("images/grumpy.jpg").resize((cell_size-10, cell_size-10))
    grumpy_img = ImageTk.PhotoImage(grumpy_img)
except:
    # Imágenes de respaldo
    panda_img = Image.new('RGB', (cell_size-10, cell_size-10), 'blue')
    panda_img = ImageTk.PhotoImage(panda_img)
    moneda_img = Image.new('RGB', (cell_size-10, cell_size-10), 'gold')
    moneda_img = ImageTk.PhotoImage(moneda_img)
    grumpy_img = Image.new('RGB', (cell_size-10, cell_size-10), 'red')
    grumpy_img = ImageTk.PhotoImage(grumpy_img)

# Función de movimiento del Grumpus
def mover_grumpus():
    global grumpy_pos, danger_zones
    
    if not grumpus.puede_mover():
        return
    
    distancia = abs(player_pos[0] - grumpy_pos[0]) + abs(player_pos[1] - grumpy_pos[1])
    rango_vision = grumpus.get_rango_vision()
    
    # Comportamiento basado en agresividad
    if grumpus.agresividad <= 0.4:
        # Movimiento aleatorio a casillas adyacentes (no diagonales)
        movimientos_posibles = [
            (grumpy_pos[0]+1, grumpy_pos[1]),  # Derecha
            (grumpy_pos[0]-1, grumpy_pos[1]),  # Izquierda
            (grumpy_pos[0], grumpy_pos[1]+1),  # Abajo
            (grumpy_pos[0], grumpy_pos[1]-1)   # Arriba
        ]
        # Filtrar movimientos válidos (no obstáculos)
        movimientos_validos = [m for m in movimientos_posibles if graph.has_node(m)]
        if movimientos_validos:
            grumpy_pos = random.choice(movimientos_validos)
    elif distancia <= rango_vision:  # Jugador dentro del rango de visión
        if random.random() < grumpus.agresividad:  # Decide si atacar
            # Perseguir al jugador (movimiento no diagonal)
            dx = 1 if player_pos[0] > grumpy_pos[0] else -1 if player_pos[0] < grumpy_pos[0] else 0
            dy = 1 if player_pos[1] > grumpy_pos[1] else -1 if player_pos[1] < grumpy_pos[1] else 0
            
            # Priorizar dirección con mayor diferencia
            if abs(player_pos[0] - grumpy_pos[0]) >= abs(player_pos[1] - grumpy_pos[1]):
                if dx != 0:
                    new_pos = (grumpy_pos[0]+dx, grumpy_pos[1])
                elif dy != 0:
                    new_pos = (grumpy_pos[0], grumpy_pos[1]+dy)
            else:
                if dy != 0:
                    new_pos = (grumpy_pos[0], grumpy_pos[1]+dy)
                elif dx != 0:
                    new_pos = (grumpy_pos[0]+dx, grumpy_pos[1])
            
            # Verificar si el movimiento es válido
            if graph.has_node(new_pos):
                grumpy_pos = new_pos
    
    # Actualizar posición gráfica
    canvas.coords(grumpy_dibujo, 
                grumpy_pos[0]*cell_size+cell_size//2, 
                grumpy_pos[1]*cell_size+cell_size//2)
    
    # Actualizar zonas de peligro
    danger_zones = {
        (grumpy_pos[0]-1, grumpy_pos[1]), (grumpy_pos[0]+1, grumpy_pos[1]),
        (grumpy_pos[0], grumpy_pos[1]-1), (grumpy_pos[0], grumpy_pos[1]+1)
    }
    
    # Actualizar el grafo con las nuevas zonas de peligro
    actualizar_grafo()
    
    # Verificar si atrapó al jugador
    if grumpy_pos == player_pos:
        messagebox.showinfo("Game Over", "¡El Grumpus te atrapó!")
        reiniciar_nivel()

# Función de movimiento del jugador
def mover_jugador(path, index=1):
    global player_pos, counter
    
    if index < len(path):
        new_pos = path[index]
        canvas.coords(player, new_pos[0]*cell_size+cell_size//2, new_pos[1]*cell_size+cell_size//2)
        player_pos = new_pos
        
        # Actualizar contador según terreno
        if new_pos in moderate_terrain:
            counter += 3
        elif new_pos in difficult_terrain:
            counter += 5
        elif new_pos in danger_zones:
            counter += 100
        else:
            counter += 1
        
        info_frame.children['!label2'].config(text=f"Contador: {counter}")
        
        # Mover Grumpus después de cada movimiento del jugador
        mover_grumpus()
        
        # Continuar movimiento si no ha sido atrapado
        if grumpy_pos != player_pos:
            window.after(300, lambda: mover_jugador(path, index+1))
        else:
            messagebox.showinfo("Game Over", "¡El Grumpus te atrapó!")
            reiniciar_nivel()
    else:
        nivel_completado()

# Función para encontrar camino
def encontrar_camino():
    try:
        camino = nx.astar_path(graph, player_pos, goal_pos, heuristic=lambda a, b: abs(a[0]-b[0]) + abs(a[1]-b[1]))
        mover_jugador(camino)
    except:
        messagebox.showinfo("Error", "No hay camino disponible")
        reiniciar_nivel()

# Funciones de gestión del juego
def nivel_completado():
    global nivel_actual, grumpus, counter
    
    respuesta = messagebox.askyesno("Nivel Completado", 
                                  f"¡Completaste el nivel {nivel_actual}!\n¿Quieres continuar al siguiente nivel?")
    if respuesta:
        nivel_actual += 1
        counter = 0
        grumpus = Grumpus(nivel_actual)
        window.title(f"Grumpy - Nivel {nivel_actual}")
        info_frame.children['!label'].config(text=f"Nivel: {nivel_actual}")
        info_frame.children['!label2'].config(text=f"Contador: {counter}")
        genes_text = f"Grumpus - Mov: {'Sí' if grumpus.movilidad == 2 else 'No'} Vel: {grumpus.velocidad} Agr: {grumpus.agresividad:.1f} Vis: {grumpus.visibilidad}"
        info_frame.children['!label3'].config(text=genes_text)
        reiniciar_nivel()
    else:
        window.quit()

def reiniciar_nivel():
    global player_pos, grumpy_pos, counter, danger_zones, player, goal, grumpy_dibujo
    
    # Generar un nuevo mapa aleatorio
    generar_mapa_aleatorio()
    
    player_pos = (0, 0)
    # Colocar al Grumpus en una posición aleatoria que no sea (0,0) o (9,9)
    while True:
        grumpy_pos = (random.randint(0, grid_width-1), random.randint(0, grid_height-1))
        if grumpy_pos != (0, 0) and grumpy_pos != (9, 9) and grumpy_pos not in obstacles:
            break
    
    counter = 0
    danger_zones = {
        (grumpy_pos[0]-1, grumpy_pos[1]), (grumpy_pos[0]+1, grumpy_pos[1]),
        (grumpy_pos[0], grumpy_pos[1]-1), (grumpy_pos[0], grumpy_pos[1]+1)
    }
    
    # Actualizar el grafo con el nuevo mapa
    actualizar_grafo()
    
    # Reiniciar el contador de movimientos del Grumpus
    grumpus.movimientos_player = 0
    
    canvas.delete("all")
    dibujar_mapa()
    
    # Recrear los elementos gráficos con las variables globales
    player = canvas.create_image(player_pos[0]*cell_size+cell_size//2, player_pos[1]*cell_size+cell_size//2, image=panda_img)
    goal = canvas.create_image(goal_pos[0]*cell_size+cell_size//2, goal_pos[1]*cell_size+cell_size//2, image=moneda_img)
    grumpy_dibujo = canvas.create_image(grumpy_pos[0]*cell_size+cell_size//2, grumpy_pos[1]*cell_size+cell_size//2, image=grumpy_img)
    
    info_frame.children['!label2'].config(text=f"Contador: {counter}")
    
    window.after(500, encontrar_camino)

# Generar el primer mapa aleatorio
generar_mapa_aleatorio()
actualizar_grafo()

# Dibujar elementos del juego iniciales
dibujar_mapa()
player = canvas.create_image(player_pos[0]*cell_size+cell_size//2, player_pos[1]*cell_size+cell_size//2, image=panda_img)
goal = canvas.create_image(goal_pos[0]*cell_size+cell_size//2, goal_pos[1]*cell_size+cell_size//2, image=moneda_img)
grumpy_dibujo = canvas.create_image(grumpy_pos[0]*cell_size+cell_size//2, grumpy_pos[1]*cell_size+cell_size//2, image=grumpy_img)

# Iniciar el juego
window.after(1000, encontrar_camino)
window.mainloop()