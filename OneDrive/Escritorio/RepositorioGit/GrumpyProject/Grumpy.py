import tkinter as tk
import networkx as nx
from PIL import Image, ImageTk  # Para cargar imágenes

# Parámetros
cell_size = 40
grid_width = 10
grid_height = 10
counter = 0

# Estados del sistema
class State:
    INICIO = "Inicio"
    BUSCANDO_CAMINO = "Buscando Camino"
    MOVIENDO_JUGADOR = "Moviendo Jugador"
    LLEGADA = "Llegada"
    SIN_CAMINO = "Sin Camino"

current_state = State.INICIO
current_path = None  

# Definir costes según el tipo de terreno
costs = {"normal": 1, "moderate": 3, "difficult": 5}

# Crear la ventana
window = tk.Tk()
window.title("Grupmy")

canvas = tk.Canvas(window, width=grid_width * cell_size, height=grid_height * cell_size, bg="white")
canvas.pack()

# Contador
counter_label = tk.Label(window, text=f"Contador: {counter}", font=("Arial", 12))
counter_label.pack()

# Estado del sistema
state_label = tk.Label(window, text=f"Estado: {current_state}", font=("Arial", 12))
state_label.pack()

# Cargar imagen del panda
panda_img = Image.open("panda.jpg")
panda_img = panda_img.resize((cell_size - 10, cell_size - 10), Image.LANCZOS)
panda_img = ImageTk.PhotoImage(panda_img)
window.panda_img = panda_img  # Evitar que se borre por el recolector de basura

# Crear el grafo
graph = nx.grid_2d_graph(grid_width, grid_height)

# Obstáculos
obstacles = {(1, 1), (2, 3), (3, 5), (4, 7), (5, 9), (6, 2), (7, 4), (8, 6), (9, 8), (0, 9)}
moderate_terrain = {(1, 4), (3, 3), (9, 5), (6, 8)}
difficult_terrain = {(4, 8), (7, 7), (5, 5)}

# Asignar costes
for i, j in graph.edges():
    if i in moderate_terrain or j in moderate_terrain:
        graph[i][j]['weight'] = costs["moderate"]
    elif i in difficult_terrain or j in difficult_terrain:
        graph[i][j]['weight'] = costs["difficult"]
    else:
        graph[i][j]['weight'] = costs["normal"]

# Eliminar nodos de obstáculos
for obstacle in obstacles:
    if graph.has_node(obstacle):
        graph.remove_node(obstacle)

# Dibujar cuadrícula
for i in range(grid_width):
    for j in range(grid_height):
        x1, y1 = i * cell_size, j * cell_size
        x2, y2 = x1 + cell_size, y1 + cell_size

        if (i, j) in obstacles:
            color = "black"
        elif (i, j) in moderate_terrain:
            color = "yellow"
        elif (i, j) in difficult_terrain:
            color = "red"
        else:
            color = "white"

        canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

# Posición inicial del jugador y meta
player_pos = (0, 0)
goal_pos = (9, 9)

# Dibujar jugador (imagen del panda)
player = canvas.create_image(
    player_pos[0] * cell_size + cell_size // 2,
    player_pos[1] * cell_size + cell_size // 2,
    image=window.panda_img
)

# Dibujar meta
canvas.create_oval(
    goal_pos[0] * cell_size + 10, 
    goal_pos[1] * cell_size + 10,
    (goal_pos[0] + 1) * cell_size - 10, 
    (goal_pos[1] + 1) * cell_size - 10,
    fill="green"
)

# Heurística Manhattan
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# Cambiar estado
def change_state(new_state):
    global current_state, current_path
    current_state = new_state
    state_label.config(text=f"Estado: {current_state}")
    print(f"Estado actual: {current_state}")

    if current_state == State.BUSCANDO_CAMINO:
        find_path()
    elif current_state == State.MOVIENDO_JUGADOR and current_path is not None:
        move_player(current_path)
    elif current_state == State.LLEGADA:
        print("¡Llegaste a la meta!")
    elif current_state == State.SIN_CAMINO:
        print("No hay camino disponible.")

# Cambiar contador
def change_counter(new_pos):
    global counter
    if new_pos in moderate_terrain:
        counter += 3
    elif new_pos in difficult_terrain:
        counter += 5
    else:
        counter += 1
    counter_label.config(text=f"Contador: {counter}")

# Algoritmo A*
def find_path():
    global current_path
    try:
        current_path = nx.astar_path(graph, player_pos, goal_pos, weight="weight", heuristic=heuristic)
        change_state(State.MOVIENDO_JUGADOR)
    except nx.NetworkXNoPath:
        change_state(State.SIN_CAMINO)

# Mover el panda
def move_player(path, index=1):
    global player_pos
    if index < len(path):
        new_pos = path[index]
        new_x = new_pos[0] * cell_size + cell_size // 2
        new_y = new_pos[1] * cell_size + cell_size // 2
        change_counter(new_pos)
        canvas.coords(player, new_x, new_y)  # Mueve la imagen del panda
        player_pos = new_pos
        window.after(200, lambda: move_player(path, index + 1))
    else:
        change_state(State.LLEGADA)

# Botón para iniciar el movimiento con A*
start_button = tk.Button(window, text="Iniciar A*", command=lambda: change_state(State.BUSCANDO_CAMINO))
start_button.pack()

# Iniciar loop de Tkinter
window.mainloop()