import tkinter as tk
from tkinter import messagebox
import networkx as nx
from PIL import Image, ImageTk
import random

# Parámetros
cell_size = 40
grid_width = 10
grid_height = 10
counter = 0
current_level = 1
max_levels = 7

# Estados del sistema
class State:
    INICIO = "Inicio"
    BUSCANDO_CAMINO = "Buscando Camino"
    MOVIENDO_JUGADOR = "Moviendo Jugador"
    LLEGADA = "Llegada"
    SIN_CAMINO = "Sin Camino"

current_state = State.INICIO
current_path = None

# Información de niveles
level_data = {
    1: {
        "name": "Miacidae",
        "description": "Carnívoro primitivo (hace 55 millones de años)",
        "player_image": "images/miacidae.jpg",
        "bg_color": "#D6EAF8",  # Azul claro - Era primitiva
        "normal_terrain": "light blue",
        "moderate_terrain": "steel blue",
        "difficult_terrain": "royal blue",
        "danger_color": "dodger blue",
        "player_start": (0, 0),
        "goal_pos": (9, 9)
    },
    2: {
        "name": "Ursavus",
        "description": "Antepasado del oso (hace 20 millones de años)",
        "player_image": "images/ursavus.jpg", 
        "bg_color": "#D5F5E3",  # Verde claro - Era de bosques primitivos
        "normal_terrain": "pale green",
        "moderate_terrain": "medium sea green",
        "difficult_terrain": "sea green",
        "danger_color": "forest green",
        "player_start": (0, 9),
        "goal_pos": (9, 0)
    },
    3: {
        "name": "Agriarctos",
        "description": "Ancestro de los osos y pandas (hace 12 millones de años)",
        "player_image": "images/agriarctos.jpg",
        "bg_color": "#FCF3CF",  # Amarillo claro - Era de praderas
        "normal_terrain": "khaki",
        "moderate_terrain": "gold",
        "difficult_terrain": "goldenrod",
        "danger_color": "dark goldenrod",
        "player_start": (5, 0),
        "goal_pos": (5, 9)
    },
    4: {
        "name": "Ailurarctos",
        "description": "Ancestro directo del panda (hace 8 millones de años)",
        "player_image": "images/ailurarctos.jpg",
        "bg_color": "#F5EEF8",  # Lavanda - Era de diversificación
        "normal_terrain": "lavender",
        "moderate_terrain": "medium purple",
        "difficult_terrain": "dark orchid",
        "danger_color": "purple",
        "player_start": (0, 5),
        "goal_pos": (9, 5)
    },
    5: {
        "name": "Ailuropoda microta",
        "description": "Panda pigmeo (hace 2 millones de años)",
        "player_image": "images/microta.jpg",
        "bg_color": "#FADBD8",  # Rosa claro - Era de bosques de bambú primitivos
        "normal_terrain": "light pink",
        "moderate_terrain": "pink",
        "difficult_terrain": "hot pink",
        "danger_color": "deep pink",
        "player_start": (9, 9),
        "goal_pos": (0, 0)
    },
    6: {
        "name": "Ailuropoda baconi",
        "description": "Panda gigante antiguo (hace 750,000 años)",
        "player_image": "images/baconi.jpg",
        "bg_color": "#F9E79F",  # Amarillo intenso - Era de expansión
        "normal_terrain": "light yellow",
        "moderate_terrain": "yellow",
        "difficult_terrain": "gold",
        "danger_color": "orange",
        "player_start": (4, 4),
        "goal_pos": (9, 0)
    },
    7: {
        "name": "Ailuropoda melanoleuca",
        "description": "Panda gigante actual (presente)",
        "player_image": "images/panda.jpg",
        "bg_color": "#E8F8F5",  # Verde menta - Era moderna
        "normal_terrain": "pale green",
        "moderate_terrain": "light green",
        "difficult_terrain": "medium spring green",
        "danger_color": "spring green",
        "player_start": (0, 0),
        "goal_pos": (9, 9)
    }
}

# Crear la ventana
window = tk.Tk()
window.title("Evolución del Panda")

main_frame = tk.Frame(window)
main_frame.pack(fill=tk.BOTH, expand=True)

info_frame = tk.Frame(window)
info_frame.pack(fill=tk.X)

# Canvas para el juego
canvas = tk.Canvas(main_frame, width=grid_width * cell_size, height=grid_height * cell_size, bg="white")
canvas.pack(padx=10, pady=10)

# Frame para información
labels_frame = tk.Frame(info_frame)
labels_frame.pack(side=tk.LEFT, padx=10)

# Etiquetas informativas
level_label = tk.Label(labels_frame, text=f"Nivel {current_level}: {level_data[current_level]['name']}", font=("Arial", 12, "bold"))
level_label.pack(anchor=tk.W)

description_label = tk.Label(labels_frame, text=level_data[current_level]['description'], font=("Arial", 10, "italic"))
description_label.pack(anchor=tk.W)

counter_label = tk.Label(labels_frame, text=f"Movimientos: {counter}", font=("Arial", 10))
counter_label.pack(anchor=tk.W)

state_label = tk.Label(labels_frame, text=f"Estado: {current_state}", font=("Arial", 10))
state_label.pack(anchor=tk.W)

# Diccionario para almacenar las imágenes
images = {}

# Definir costes según el tipo de terreno
costs = {"normal": 1, "moderate": 3, "difficult": 5, "peligroso": 20}

# Variables globales
player_pos = level_data[current_level]["player_start"]
goal_pos = level_data[current_level]["goal_pos"]
obstacles = set()
moderate_terrain = set()
difficult_terrain = set()
grumpy_pos = (5, 3)
danger_zones = set()
player = None
goal = None
grumpy = None
graph = None

# Cargar imágenes base
def load_images():
    global images
    # Cargar la moneda
    try:
        moneda_img = Image.open("images/moneda.jpg").resize((cell_size - 10, cell_size - 10), Image.Resampling.LANCZOS)
        images["moneda"] = ImageTk.PhotoImage(moneda_img)
    except Exception as e:
        print(f"Error al cargar imagen de moneda: {e}")
        # Crear imagen de respaldo para la moneda
        backup_img = Image.new('RGB', (cell_size - 10, cell_size - 10), color=(255, 215, 0))
        images["moneda"] = ImageTk.PhotoImage(backup_img)
    
    # Cargar grumpy
    try:
        grumpy_img = Image.open("images/grumpy.jpg").resize((cell_size - 10, cell_size - 10), Image.Resampling.LANCZOS)
        images["grumpy"] = ImageTk.PhotoImage(grumpy_img)
    except Exception as e:
        print(f"Error al cargar imagen de grumpy: {e}")
        # Crear imagen de respaldo para grumpy
        backup_img = Image.new('RGB', (cell_size - 10, cell_size - 10), color=(255, 0, 0))
        images["grumpy"] = ImageTk.PhotoImage(backup_img)
    
    # Cargar imágenes de evolución para cada nivel
    for level, data in level_data.items():
        try:
            avatar_img = Image.open(data["player_image"]).resize((cell_size - 10, cell_size - 10), Image.Resampling.LANCZOS)
            images[f"level_{level}"] = ImageTk.PhotoImage(avatar_img)
        except Exception as e:
            print(f"Error al cargar imagen para nivel {level}: {e}")
            # Usar colores diferentes para cada nivel si faltan imágenes
            colors = [(0, 0, 0), (50, 50, 150), (100, 100, 0), (150, 50, 100), 
                    (50, 150, 100), (150, 100, 50), (100, 100, 100)]
            backup_img = Image.new('RGB', (cell_size - 10, cell_size - 10), color=colors[level-1])
            images[f"level_{level}"] = ImageTk.PhotoImage(backup_img)

# Heurística Manhattan
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# Verificar si existe un camino entre dos puntos
def path_exists(start, end, obstacles_set):
    temp_graph = nx.grid_2d_graph(grid_width, grid_height)
    
    # Eliminar nodos de obstáculos
    for obstacle in obstacles_set:
        if temp_graph.has_node(obstacle):
            temp_graph.remove_node(obstacle)
    
    try:
        # Intentar encontrar un camino
        path = nx.shortest_path(temp_graph, start, end)
        return True
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return False

# Función para generar el nivel con garantía de camino
def generate_level(level):
    global obstacles, moderate_terrain, difficult_terrain, grumpy_pos, danger_zones
    global player_pos, goal_pos, graph
    
    # Obtener posiciones del nivel actual
    player_pos = level_data[level]["player_start"]
    goal_pos = level_data[level]["goal_pos"]
    
    # Resetear variables
    obstacles = set()
    moderate_terrain = set()
    difficult_terrain = set()
    
    # Ubicación aleatoria de "Grumpy" para cada nivel (evitando posiciones clave)
    while True:
        grumpy_pos = (random.randint(1, grid_width - 2), random.randint(1, grid_height - 2))
        if grumpy_pos != player_pos and grumpy_pos != goal_pos:
            break
    
    # Zonas de peligro alrededor de Grumpy
    danger_zones = {
        (grumpy_pos[0] - 1, grumpy_pos[1]), (grumpy_pos[0] + 1, grumpy_pos[1]),
        (grumpy_pos[0], grumpy_pos[1] - 1), (grumpy_pos[0], grumpy_pos[1] + 1)
    }
    
    # Filtrar zonas de peligro que podrían bloquear el camino
    filtered_danger = set()
    for pos in danger_zones:
        if 0 <= pos[0] < grid_width and 0 <= pos[1] < grid_height:
            if pos != player_pos and pos != goal_pos:
                filtered_danger.add(pos)
    
    danger_zones = filtered_danger
    
    # Generar obstáculos aleatorios (diferentes para cada nivel)
    seed = level * 100  # Semilla basada en el nivel para consistencia
    random.seed(seed)
    
    # Calcular número base de obstáculos según el nivel
    base_obstacles = 5 + level  # Incrementa dificultad con cada nivel
    
    # Intentar colocar obstáculos asegurando que existe un camino
    attempts = 0
    while len(obstacles) < base_obstacles and attempts < 100:
        pos = (random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))
        
        # Evitar posiciones clave
        if (pos == player_pos or pos == goal_pos or pos == grumpy_pos or 
            pos in danger_zones or pos in obstacles):
            continue
        
        # Añadir obstáculo temporalmente
        temp_obstacles = obstacles.copy()
        temp_obstacles.add(pos)
        
        # Verificar si aún existe un camino
        if path_exists(player_pos, goal_pos, temp_obstacles):
            obstacles = temp_obstacles
        
        attempts += 1
    
    # Terrenos especiales - solo añadir si no bloquean el camino
    num_moderate = 3 + level // 2
    num_difficult = 1 + level // 2
    
    # Añadir terreno moderado
    attempts = 0
    while len(moderate_terrain) < num_moderate and attempts < 50:
        pos = (random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))
        if (pos != player_pos and pos != goal_pos and pos != grumpy_pos 
                and pos not in obstacles and pos not in danger_zones):
            moderate_terrain.add(pos)
        attempts += 1
    
    # Añadir terreno difícil
    attempts = 0
    while len(difficult_terrain) < num_difficult and attempts < 50:
        pos = (random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))
        if (pos != player_pos and pos != goal_pos and pos != grumpy_pos 
                and pos not in obstacles and pos not in moderate_terrain and pos not in danger_zones):
            difficult_terrain.add(pos)
        attempts += 1
    
    # Crear el grafo
    graph = nx.grid_2d_graph(grid_width, grid_height)
    
    # Asignar costes
    for i, j in graph.edges():
        if i in moderate_terrain or j in moderate_terrain:
            graph[i][j]['weight'] = costs["moderate"]
        elif i in difficult_terrain or j in difficult_terrain:
            graph[i][j]['weight'] = costs["difficult"]
        elif i in danger_zones or j in danger_zones:
            graph[i][j]['weight'] = costs["peligroso"]
        else:
            graph[i][j]['weight'] = costs["normal"]
    
    # Eliminar nodos de obstáculos
    for obstacle in obstacles:
        if graph.has_node(obstacle):
            graph.remove_node(obstacle)
    
    # Verificación final de que existe un camino
    try:
        test_path = nx.astar_path(graph, player_pos, goal_pos, heuristic=heuristic)
        if not test_path:
            # En caso extremo, eliminar algunos obstáculos aleatorios
            for _ in range(min(3, len(obstacles))):
                if obstacles:
                    obstacles.pop()
                    
            # Recrear el grafo sin esos obstáculos
            graph = nx.grid_2d_graph(grid_width, grid_height)
            for i, j in graph.edges():
                if i in moderate_terrain or j in moderate_terrain:
                    graph[i][j]['weight'] = costs["moderate"]
                elif i in difficult_terrain or j in difficult_terrain:
                    graph[i][j]['weight'] = costs["difficult"]
                elif i in danger_zones or j in danger_zones:
                    graph[i][j]['weight'] = costs["peligroso"]
                else:
                    graph[i][j]['weight'] = costs["normal"]
            
            for obstacle in obstacles:
                if graph.has_node(obstacle):
                    graph.remove_node(obstacle)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        # Si aún no hay camino, reducir drásticamente los obstáculos
        obstacles = set()
        # Dejar sólo algunos obstáculos básicos
        for _ in range(level):
            pos = (random.randint(2, grid_width - 3), random.randint(2, grid_height - 3))
            if pos != player_pos and pos != goal_pos:
                obstacles.add(pos)
        
        # Recrear el grafo una última vez
        graph = nx.grid_2d_graph(grid_width, grid_height)
        for i, j in graph.edges():
            if i in moderate_terrain or j in moderate_terrain:
                graph[i][j]['weight'] = costs["moderate"]
            elif i in difficult_terrain or j in difficult_terrain:
                graph[i][j]['weight'] = costs["difficult"]
            elif i in danger_zones or j in danger_zones:
                graph[i][j]['weight'] = costs["peligroso"]
            else:
                graph[i][j]['weight'] = costs["normal"]
        
        for obstacle in obstacles:
            if graph.has_node(obstacle):
                graph.remove_node(obstacle)

# Dibujar el tablero
def draw_board():
    global player, goal, grumpy
    
    # Limpiar el canvas
    canvas.delete("all")
    
    # Configurar el fondo del canvas según el nivel
    canvas.config(bg=level_data[current_level]["bg_color"])
    
    # Dibujar cuadrícula
    for i in range(grid_width):
        for j in range(grid_height):
            x1, y1 = i * cell_size, j * cell_size
            x2, y2 = x1 + cell_size, y1 + cell_size
            
            if (i, j) in obstacles:
                color = "black"  # Obstáculo
            elif (i, j) in moderate_terrain:
                color = level_data[current_level]["moderate_terrain"]
            elif (i, j) in difficult_terrain:
                color = level_data[current_level]["difficult_terrain"]
            elif (i, j) in danger_zones:
                color = level_data[current_level]["danger_color"]
            else:
                color = level_data[current_level]["normal_terrain"]
            
            # Dibujar la celda
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
            
            # Si la celda es de peligro, agregar la ❌
            if (i, j) in danger_zones:
                canvas.create_text(x1 + cell_size / 2, y1 + cell_size / 2, text="❌", font=("Arial", 18, "bold"), fill="red")
            
            # Agregar números de coordenadas pequeños para depuración
            canvas.create_text(x1 + 10, y1 + 10, text=f"{i},{j}", font=("Arial", 7), fill="gray")
    
    # Dibujar jugador (imagen de evolución según nivel)
    player = canvas.create_image(
        player_pos[0] * cell_size + cell_size // 2,
        player_pos[1] * cell_size + cell_size // 2,
        image=images[f"level_{current_level}"]
    )
    
    # Dibujar meta (imagen de la moneda)
    goal = canvas.create_image(
        goal_pos[0] * cell_size + cell_size // 2,
        goal_pos[1] * cell_size + cell_size // 2,
        image=images["moneda"]
    )
    
    # Dibujar "Grumpy"
    grumpy = canvas.create_image(
        grumpy_pos[0] * cell_size + cell_size // 2,
        grumpy_pos[1] * cell_size + cell_size // 2,
        image=images["grumpy"]
    )

# Cambiar estado
def change_state(new_state):
    global current_state, current_path
    current_state = new_state
    state_label.config(text=f"Estado: {current_state}")
    
    if current_state == State.BUSCANDO_CAMINO:
        window.after(100, find_path)
    elif current_state == State.MOVIENDO_JUGADOR and current_path is not None:
        window.after(100, lambda: move_player(current_path))
    elif current_state == State.LLEGADA:
        print(f"¡Completaste el nivel {current_level}!")
        window.after(500, next_level)
    elif current_state == State.SIN_CAMINO:
        print("No hay camino disponible.")
        regenerate_level()  # Regenerar nivel si no hay camino

# Regenerar nivel si no hay camino disponible
def regenerate_level():
    print(f"Regenerando nivel {current_level} para garantizar un camino...")
    generate_level(current_level)
    draw_board()
    change_state(State.BUSCANDO_CAMINO)

# Cambiar contador
def change_counter(new_pos):
    global counter
    if new_pos in moderate_terrain:
        counter += 3
    elif new_pos in difficult_terrain:
        counter += 5
    elif new_pos in danger_zones:
        counter += 10  # Penalización alta si pasa por zona de peligro
    else:
        counter += 1
    counter_label.config(text=f"Movimientos: {counter}")

# Algoritmo A*
def find_path():
    global current_path
    try:
        current_path = nx.astar_path(graph, player_pos, goal_pos, weight="weight", heuristic=heuristic)
        print(f"Camino encontrado en nivel {current_level} con longitud {len(current_path)}")
        change_state(State.MOVIENDO_JUGADOR)
    except (nx.NetworkXNoPath, nx.NodeNotFound) as e:
        print(f"Error al buscar camino: {e}")
        print(f"Posición del jugador: {player_pos}, Meta: {goal_pos}")
        print(f"Obstáculos: {len(obstacles)}")
        # Intentar regenerar el nivel
        regenerate_level()

# Mover el jugador
def move_player(path, index=1):
    global player_pos
    if index < len(path):
        new_pos = path[index]
        new_x = new_pos[0] * cell_size + cell_size // 2
        new_y = new_pos[1] * cell_size + cell_size // 2
        change_counter(new_pos)
        canvas.coords(player, new_x, new_y)
        player_pos = new_pos
        window.after(200, lambda: move_player(path, index + 1))
    else:
        change_state(State.LLEGADA)

# Avanzar al siguiente nivel
def next_level():
    global current_level
    
    if current_level < max_levels:
        current_level += 1
        level_transition()
    else:
        show_victory_dialog()

# Transición entre niveles
def level_transition():
    global player_pos
    
    # Actualizar etiquetas
    level_label.config(text=f"Nivel {current_level}: {level_data[current_level]['name']}")
    description_label.config(text=level_data[current_level]['description'])
    
    # Generar nuevo nivel
    generate_level(current_level)
    
    # Dibujar nuevo tablero
    draw_board()
    
    # Reiniciar estado para el nuevo nivel
    change_state(State.INICIO)
    
    # Iniciar la búsqueda del camino automáticamente
    window.after(500, lambda: change_state(State.BUSCANDO_CAMINO))

# Mostrar cuadro de diálogo de victoria
def show_victory_dialog():
    result = messagebox.askyesno("¡Victoria!", 
                               f"¡Felicidades! Has completado todos los niveles de evolución del panda con {counter} movimientos totales.\n\n"
                               f"Has recorrido toda la historia evolutiva del panda, desde Miacidae hasta el Panda Gigante actual (Ailuropoda melanoleuca).\n\n"
                               f"¿Quieres volver a jugar?")
    if result:
        reset_game()  # Volver a empezar el juego si la respuesta es sí
    else:
        window.quit()  # Terminar la ejecución si la respuesta es no

# Reiniciar el juego
def reset_game():
    global player_pos, counter, current_state, current_path, current_level
    
    current_level = 1
    counter = 0
    current_path = None
    
    # Actualizar etiquetas
    level_label.config(text=f"Nivel {current_level}: {level_data[current_level]['name']}")
    description_label.config(text=level_data[current_level]['description'])
    counter_label.config(text=f"Movimientos: {counter}")
    
    # Generar nivel inicial
    generate_level(current_level)
    
    # Dibujar tablero
    draw_board()
    
    # Cambiar estado
    change_state(State.INICIO)
    
    # Iniciar automáticamente
    window.after(500, lambda: change_state(State.BUSCANDO_CAMINO))

# Inicializar el juego
def init_game():
    load_images()
    generate_level(current_level)
    draw_board()
    change_state(State.BUSCANDO_CAMINO)

# Iniciar el juego
init_game()
window.mainloop()