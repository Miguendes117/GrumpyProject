import tkinter as tk
from tkinter import messagebox
import networkx as nx
from PIL import Image, ImageTk
import random
import math
import winsound  # Para efectos de sonido en Windows
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Parámetros del juego
cell_size = 40
grid_width = 15
grid_height = 15
counter = 0
nivel = 1
poblacion_size = 15
mejores_rutas = []

# Estados del sistema
class State:
    INICIO = "Inicio"
    BUSCANDO_CAMINO = "Buscando Camino"
    MOVIENDO_PANDA = "Moviendo Panda"
    MOVIENDO_GRUMPY = "Moviendo Grumpy"
    LLEGADA = "Llegada"
    SIN_CAMINO = "Sin Camino"
    PANDA_ATRAPADO = "Panda Atrapado"

current_state = State.INICIO
current_path = None

# Configuración de costos
costs = {
    "normal": 1,
    "moderate": 3,
    "difficult": 5,
    "peligroso": 20,
    "bloqueado": float('inf')
}

# Crear ventana principal
window = tk.Tk()
window.title("Grumpy Dinámico Pro - Nivel 1")
window.geometry(f"{grid_width * cell_size + 450}x{grid_height * cell_size + 150}")

# Área de juego
canvas = tk.Canvas(
    window, 
    width=grid_width * cell_size, 
    height=grid_height * cell_size, 
    bg="white"
)
canvas.pack(side=tk.LEFT, padx=10, pady=10)

# Panel de información y controles
info_panel = tk.Frame(window, width=300)
info_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

# Contadores y estados
tk.Label(info_panel, text="Estado del Juego:", font=("Arial", 12, "bold")).pack(pady=5)
state_label = tk.Label(info_panel, text=f"Estado: {current_state}", font=("Arial", 12))
state_label.pack()

tk.Label(info_panel, text="\nEstadísticas:", font=("Arial", 12, "bold")).pack(pady=5)
counter_label = tk.Label(info_panel, text=f"Contador: {counter}", font=("Arial", 12))
counter_label.pack()
level_label = tk.Label(info_panel, text=f"Nivel: {nivel}", font=("Arial", 12))
level_label.pack()

tk.Label(info_panel, text="\nInteligencia de Grumpy:", font=("Arial", 12, "bold")).pack(pady=5)
grumpy_info = tk.Label(info_panel, text="Grumpy: Inactivo", font=("Arial", 10))
grumpy_info.pack()

# Gráfico de evolución del fitness
fig, ax = plt.subplots(figsize=(4, 2))
ax.set_title("Evolución del Fitness")
ax.set_xlabel("Generación")
ax.set_ylabel("Fitness")
canvas_plot = FigureCanvasTkAgg(fig, master=info_panel)
canvas_plot.get_tk_widget().pack(pady=10)

# Carga de imágenes
def load_image(path, size):
    try:
        img = Image.open(path).resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Error cargando imagen {path}: {e}")
        img = Image.new('RGB', size, color='gray')
        return ImageTk.PhotoImage(img)

img_size = (cell_size - 10, cell_size - 10)
panda_img = load_image("images/panda.jpg", img_size)
moneda_img = load_image("images/moneda.jpg", img_size)
grumpy_img = load_image("images/grumpy.jpg", img_size)

# Efectos de sonido
def play_sound(sound_type):
    try:
        if sound_type == "move":
            winsound.PlaySound("sounds/move.wav", winsound.SND_ASYNC)
        elif sound_type == "win":
            winsound.PlaySound("sounds/win.wav", winsound.SND_ASYNC)
        elif sound_type == "lose":
            winsound.PlaySound("sounds/lose.wav", winsound.SND_ASYNC)
        elif sound_type == "danger":
            winsound.PlaySound("sounds/danger.wav", winsound.SND_ASYNC)
    except:
        pass  # Continuar sin sonido si hay error

# Configuración de terreno y obstáculos
def setup_terrain():
    global obstacles, moderate_terrain, difficult_terrain
    
    # Base + obstáculos adicionales por nivel
    base_obstacles = {(3, 3), (7, 8), (12, 5), (4, 10)}
    extra_obstacles = min(nivel * 2, 10)  # Máximo 10 obstáculos extra
    
    obstacles = base_obstacles | {
        (random.randint(0, grid_width-1), random.randint(0, grid_height-1))
        for _ in range(extra_obstacles)
    }
    
    # Terreno moderado y difícil también aumentan con el nivel
    moderate_terrain = {
        (random.randint(0, grid_width-1), random.randint(0, grid_height-1))
        for _ in range(2 + nivel)
    }
    
    difficult_terrain = {
        (random.randint(0, grid_width-1), random.randint(0, grid_height-1))
        for _ in range(1 + nivel//2)
    }

# Inicialización del grafo
graph = nx.grid_2d_graph(grid_width, grid_height)

# Posiciones iniciales
goal_pos = (14, 14)
player_pos = (0, 0)
grumpy_pos = (7, 7)
danger_zones = set()

# Actualización de zonas de peligro
def update_danger_zones():
    global danger_zones
    danger_zones = {
        (grumpy_pos[0] + dx, grumpy_pos[1] + dy)
        for dx in [-1, 0, 1] 
        for dy in [-1, 0, 1]
        if (dx, dy) != (0, 0)
    }

# Actualización de costos del grafo
def update_graph_costs():
    for u, v in graph.edges():
        cost = costs["normal"]
        
        if u in obstacles or v in obstacles:
            cost = costs["bloqueado"]
        elif u in moderate_terrain or v in moderate_terrain:
            cost = costs["moderate"]
        elif u in difficult_terrain or v in difficult_terrain:
            cost = costs["difficult"]
        elif u in danger_zones or v in danger_zones:
            cost = costs["peligroso"]
            
        graph[u][v]['weight'] = cost

    # Eliminar nodos obstáculos
    for obstacle in obstacles:
        if graph.has_node(obstacle):
            graph.remove_node(obstacle)

# Dibujar el grid con colores
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
                canvas.create_text(x1 + cell_size/2, y1 + cell_size/2, 
                                text="❌", font=("Arial", 14), fill="red")

    # Dibujar elementos
    canvas.create_image(
        goal_pos[0] * cell_size + cell_size//2,
        goal_pos[1] * cell_size + cell_size//2,
        image=moneda_img, tags="goal"
    )
    
    canvas.create_image(
        player_pos[0] * cell_size + cell_size//2,
        player_pos[1] * cell_size + cell_size//2,
        image=panda_img, tags="panda"
    )
    
    canvas.create_image(
        grumpy_pos[0] * cell_size + cell_size//2,
        grumpy_pos[1] * cell_size + cell_size//2,
        image=grumpy_img, tags="grumpy"
    )

# Heurística para A*
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# Cambiar estado del juego
def change_state(new_state):
    global current_state
    current_state = new_state
    state_label.config(text=f"Estado: {current_state}")
    window.title(f"Grumpy Dinámico Pro - Nivel {nivel}")
    
    if current_state == State.BUSCANDO_CAMINO:
        find_path()
    elif current_state == State.MOVIENDO_PANDA:
        move_panda()
    elif current_state == State.MOVIENDO_GRUMPY:
        move_grumpy_ai()
    elif current_state == State.LLEGADA:
        play_sound("win")
        show_restart_dialog()
    elif current_state == State.PANDA_ATRAPADO:
        play_sound("lose")
        show_restart_dialog()
    elif current_state == State.SIN_CAMINO:
        show_restart_dialog()

# Actualizar contador y dificultad
def change_counter(new_pos):
    global counter, nivel
    
    if new_pos in moderate_terrain:
        counter += 3
    elif new_pos in difficult_terrain:
        counter += 5
    elif new_pos in danger_zones:
        counter += 10
        play_sound("danger")
    else:
        counter += 1
        play_sound("move")
    
    counter_label.config(text=f"Contador: {counter}")
    
    # Aumentar nivel cada 20 puntos
    new_level = counter // 20 + 1
    if new_level > nivel:
        nivel = new_level
        level_label.config(text=f"Nivel: {nivel}")
        setup_terrain()
        update_graph_costs()
        draw_grid()

# Buscar camino con A*
def find_path():
    global current_path
    
    try:
        current_path = nx.astar_path(
            graph, 
            player_pos, 
            goal_pos, 
            heuristic=heuristic,
            weight="weight"
        )
        
        # Dibujar camino
        canvas.delete("path")
        for i in range(len(current_path)-1):
            x1, y1 = current_path[i][0] * cell_size + cell_size//2, current_path[i][1] * cell_size + cell_size//2
            x2, y2 = current_path[i+1][0] * cell_size + cell_size//2, current_path[i+1][1] * cell_size + cell_size//2
            canvas.create_line(x1, y1, x2, y2, fill="blue", width=2, tags="path")
        
        change_state(State.MOVIENDO_PANDA)
        
    except nx.NetworkXNoPath:
        change_state(State.SIN_CAMINO)

# Mover al panda
def move_panda(step=1):
    global player_pos, current_path
    
    if step < len(current_path):
        new_pos = current_path[step]
        player_pos = new_pos
        
        # Actualizar gráficos
        canvas.coords("panda", 
                     new_pos[0] * cell_size + cell_size//2,
                     new_pos[1] * cell_size + cell_size//2)
        
        change_counter(new_pos)
        
        # Verificar colisión con Grumpy
        if (player_pos == grumpy_pos or 
            (heuristic(player_pos, grumpy_pos) == 1 and random.random() < 0.3)):
            change_state(State.PANDA_ATRAPADO)
            return
            
        # Mover Grumpy cada 2 pasos del panda
        if step % 2 == 0:
            window.after(300, lambda: move_panda(step+1))
            change_state(State.MOVIENDO_GRUMPY)
        else:
            window.after(300, lambda: move_panda(step+1))
    else:
        change_state(State.LLEGADA)

# Algoritmo Genético para Grumpy (mejorado)
def generar_poblacion():
    poblacion = []
    for _ in range(poblacion_size):
        ruta = [grumpy_pos]
        for _ in range(3 + nivel//2):  # Longitud de ruta aumenta con nivel
            x, y = ruta[-1]
            movimientos = [
                (x+dx, y+dy) 
                for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]
                if (x+dx, y+dy) in graph.nodes
            ]
            
            if movimientos:
                # Inteligencia adaptativa por nivel
                if random.random() < 0.6 + nivel*0.05:  # Más inteligente en niveles altos
                    movimientos.sort(key=lambda m: heuristic(m, player_pos))
                    ruta.append(movimientos[0])
                else:
                    ruta.append(random.choice(movimientos))
            else:
                break
                
        poblacion.append(ruta)
    return poblacion

def evaluar_fitness(ruta):
    score = 0
    
    # Recompensar acercamiento al panda
    distancia_final = heuristic(ruta[-1], player_pos)
    score += (grid_width + grid_height - distancia_final) * 2
    
    # Recompensar interceptar camino del panda
    if current_path:
        for pos in ruta:
            if pos in current_path:
                score += 30 + nivel*5  # Más importante en niveles altos
                
        # Extra bonus si bloquea el próximo movimiento del panda
        if len(current_path) > 1 and ruta[-1] == current_path[1]:
            score += 50
    
    # Recompensar estar en zonas estratégicas
    center_x, center_y = grid_width//2, grid_height//2
    score -= abs(ruta[-1][0] - center_x) + abs(ruta[-1][1] - center_y)
    
    # Penalizar estar en bordes
    x, y = ruta[-1]
    if x == 0 or x == grid_width-1 or y == 0 or y == grid_height-1:
        score -= 20
        
    return score

def seleccionar_mejores(poblacion, n=5):
    scores = [evaluar_fitness(r) for r in poblacion]
    indices_mejores = np.argsort(scores)[-n:]
    return [poblacion[i] for i in indices_mejores], [scores[i] for i in indices_mejores]

def cruzar_y_mutar(mejores):
    nueva_gen = list(mejores)
    
    while len(nueva_gen) < poblacion_size:
        padre1, padre2 = random.sample(mejores, 2)
        
        # Cruzamiento
        min_len = min(len(padre1), len(padre2))
        if min_len > 1:
            punto = random.randint(1, min_len-1)
            hijo = padre1[:punto] + padre2[punto:]
        else:
            hijo = padre1 if random.random() < 0.5 else padre2
        
        # Mutación (más agresiva en niveles altos)
        if random.random() < 0.3 + nivel*0.02:
            idx = random.randint(0, len(hijo)-1)
            x, y = hijo[idx]
            movimientos = [
                (x+dx, y+dy) 
                for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]
                if (x+dx, y+dy) in graph.nodes
            ]
            if movimientos:
                hijo[idx] = random.choice(movimientos)
        
        nueva_gen.append(hijo)
    
    return nueva_gen

def move_grumpy_ai():
    global grumpy_pos, mejores_rutas
    
    # Generar y evolucionar población
    poblacion = generar_poblacion()
    mejores, scores = seleccionar_mejores(poblacion)
    nueva_gen = cruzar_y_mutar(mejores)
    
    # Actualizar gráfico de fitness
    ax.clear()
    ax.plot(scores, 'b-')
    ax.set_title(f"Fitness (Nivel {nivel})")
    canvas_plot.draw()
    
    # Elegir mejor movimiento
    mejor_ruta = max(nueva_gen, key=evaluar_fitness)
    mejores_rutas = nueva_gen  # Guardar para visualización
    
    if len(mejor_ruta) > 1:
        grumpy_pos = mejor_ruta[1]
    
    # Actualizar zonas de peligro
    update_danger_zones()
    update_graph_costs()
    draw_grid()
    
    # Mostrar información de decisión
    grumpy_info.config(text=f"Grumpy: {grumpy_pos}\n"
                          f"Fitness: {max(scores):.1f}\n"
                          f"Población: {poblacion_size}")
    
    # Volver a mover al panda
    change_state(State.MOVIENDO_PANDA)

# Visualización de rutas consideradas por Grumpy
def show_grumpy_paths():
    canvas.delete("grumpy_paths")
    
    for i, ruta in enumerate(mejores_rutas[:5]):  # Mostrar solo top 5
        color = "#{:02x}{:02x}{:02x}".format(
            255, 150 - i*30, 150 - i*30)  # Degradado de rojo
        
        for j in range(len(ruta)-1):
            x1, y1 = ruta[j][0] * cell_size + cell_size//2, ruta[j][1] * cell_size + cell_size//2
            x2, y2 = ruta[j+1][0] * cell_size + cell_size//2, ruta[j+1][1] * cell_size + cell_size//2
            canvas.create_line(x1, y1, x2, y2, fill=color, width=1, tags="grumpy_paths")
            
            if j == 0:
                canvas.create_oval(
                    x1-3, y1-3, x1+3, y1+3,
                    fill=color, outline=color, tags="grumpy_paths"
                )

# Diálogo de reinicio
def show_restart_dialog():
    result = messagebox.askyesno(
        "Juego Terminado",
        f"Estado: {current_state}\nPuntuación: {counter}\nNivel alcanzado: {nivel}\n\n¿Jugar de nuevo?"
    )
    if result:
        reset_game()
    else:
        window.quit()

# Reiniciar juego
def reset_game():
    global player_pos, grumpy_pos, counter, nivel, current_path, danger_zones
    
    # Posiciones iniciales aleatorias pero equilibradas
    player_pos = (
        random.randint(0, grid_width//3),
        random.randint(0, grid_height//3)
    )
    
    grumpy_pos = (
        random.randint(2*grid_width//3, grid_width-1),
        random.randint(2*grid_height//3, grid_height-1)
    )
    
    # Asegurar distancia mínima
    while heuristic(player_pos, grumpy_pos) < 6:
        grumpy_pos = (
            random.randint(2*grid_width//3, grid_width-1),
            random.randint(2*grid_height//3, grid_height-1)
        )
    
    # Resetear variables
    counter = 0
    nivel = 1
    current_path = None
    
    # Configurar terreno según nivel
    setup_terrain()
    update_danger_zones()
    update_graph_costs()
    
    # Redibujar
    draw_grid()
    counter_label.config(text=f"Contador: {counter}")
    level_label.config(text=f"Nivel: {nivel}")
    
    # Comenzar juego
    change_state(State.BUSCANDO_CAMINO)

# Botón para ver rutas de Grumpy
show_paths_btn = tk.Button(
    info_panel, 
    text="Ver rutas de Grumpy",
    command=show_grumpy_paths
)
show_paths_btn.pack(pady=10)

# Inicialización del juego
setup_terrain()
update_graph_costs()
draw_grid()
reset_game()

window.mainloop()