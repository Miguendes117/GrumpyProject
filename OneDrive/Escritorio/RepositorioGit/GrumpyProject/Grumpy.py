import tkinter as tk
import networkx as nx

# Parámetros
cell_size = 40
grid_width = 10
grid_height = 10

# Estados del sistema
class State:
    INICIO = "Inicio"
    BUSCANDO_CAMINO = "Buscando Camino"
    MOVIENDO_JUGADOR = "Moviendo Jugador"
    LLEGADA = "Llegada"
    SIN_CAMINO = "Sin Camino"

current_state = State.INICIO
current_path = None  # Variable global para almacenar el camino encontrado

# Crear la ventana y el canvas
window = tk.Tk()
window.title("Grupmy")

canvas = tk.Canvas (
    window, 
    width=grid_width * cell_size, 
    height=grid_height * cell_size, 
    bg="white"
)

canvas.pack()

# Etiqueta para mostrar el estado
state_label = tk.Label (
    window, 
    text=f"Estado: {current_state}", 
    font=("Arial", 12)
)

state_label.pack()

# Crear el grafo de nodos
graph = nx.grid_2d_graph(grid_width, grid_height)

# Obstáculos (coordenadas de celdas negras)
obstacles = {(1, 1), (2, 3), (3, 5), (4, 7), (5, 9), 
             (6, 2), (7, 4), (8, 6), (9, 8), (0, 9)}

# Eliminar nodos en los obstáculos
for obstacle in obstacles:
    if graph.has_node(obstacle):
        graph.remove_node(obstacle)

# Dibujar cuadrícula
for i in range(grid_width):
    for j in range(grid_height):
        x1, y1 = i * cell_size, j * cell_size
        x2, y2 = x1 + cell_size, y1 + cell_size
        color = "black" if (i, j) in obstacles else "white"
        canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

# Posición inicial del jugador y meta
player_pos = (0, 0)
goal_pos = (9, 9) # Ajustado para que esté dentro de la nueva cuadrícula

# Dibujar jugador
player = canvas.create_rectangle (
    player_pos[0] * cell_size + 5, 
    player_pos[1] * cell_size + 5,
    (player_pos[0] + 1) * cell_size - 5, 
    (player_pos[1] + 1) * cell_size - 5,
    fill="blue"
)

# Dibujar meta
canvas.create_oval (
    goal_pos[0] * cell_size + 10, 
    goal_pos[1] * cell_size + 10,
    (goal_pos[0] + 1) * cell_size - 10, 
    (goal_pos[1] + 1) * cell_size - 10,
    fill="green"
)

# Función para calcular la distancia heurística (Manhattan)
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# Función para cambiar el estado del agente
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

# Encontrar el camino con A*
def find_path():
    global current_path
    try:
        current_path = nx.astar_path(graph, player_pos, goal_pos, heuristic=heuristic)
        change_state(State.MOVIENDO_JUGADOR)
    except nx.NetworkXNoPath:
        change_state(State.SIN_CAMINO)

# Función para mover al jugador paso a paso
def move_player(path, index=1):
    global player_pos
    if index < len(path):
        new_pos = path[index]
        dx = (new_pos[0] - player_pos[0]) * cell_size
        dy = (new_pos[1] - player_pos[1]) * cell_size
        canvas.move(player, dx, dy)
        player_pos = new_pos
        window.after(200, lambda: move_player(path, index + 1))
    else:
        change_state(State.LLEGADA)

# Botón para iniciar el movimiento con A*
start_button = tk.Button (
    window, 
    text="Iniciar A*", 
    command=lambda: change_state(State.BUSCANDO_CAMINO)
)

start_button.pack()

# Iniciar el loop de Tkinter
window.mainloop()
