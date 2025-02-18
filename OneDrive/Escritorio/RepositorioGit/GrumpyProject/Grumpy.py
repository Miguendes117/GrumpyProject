import tkinter as tk
import networkx as nx

# Parámetros
cell_size = 40
grid_width = 20
grid_height = 8

# Crear la ventana y el canvas
window = tk.Tk()
window.title("Movimiento con A*")
canvas = tk.Canvas(window, width=grid_width * cell_size, height=grid_height * cell_size, bg="white")
canvas.pack()

# Crear el grafo de nodos
graph = nx.grid_2d_graph(grid_width, grid_height)

# Obstáculos (coordenadas de celdas negras)
obstacles = {(3, 0), (4, 0), (5, 0), (6, 0), (7, 0), 
             (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), 
             (10, 3), (11, 3), (12, 3), (13, 3), (14, 3), 
             (14, 4), (14, 5), (14, 6), (14, 7)}

# Eliminar nodos en los obstáculos
for obstacle in obstacles:
    if graph.has_node(obstacle):
        graph.remove_node(obstacle)

# Dibujar la cuadrícula
for i in range(grid_width):
    for j in range(grid_height):
        x1, y1 = i * cell_size, j * cell_size
        x2, y2 = x1 + cell_size, y1 + cell_size
        color = "black" if (i, j) in obstacles else "white"
        canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

# Posición inicial del jugador y meta
player_pos = (1, 1)
goal_pos = (18, 2)

# Dibujar jugador
player = canvas.create_rectangle(player_pos[0] * cell_size + 5, player_pos[1] * cell_size + 5, 
                                 (player_pos[0] + 1) * cell_size - 5, (player_pos[1] + 1) * cell_size - 5, 
                                 fill="blue")

# Dibujar meta
canvas.create_oval(goal_pos[0] * cell_size + 10, goal_pos[1] * cell_size + 10, 
                   (goal_pos[0] + 1) * cell_size - 10, (goal_pos[1] + 1) * cell_size - 10, 
                   fill="green")


# Función para calcular la distancia heurística (Manhattan)
def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)


# Encontrar el camino con A*
def find_path():
    try:
        path = nx.astar_path(graph, player_pos, goal_pos, heuristic=heuristic)
        move_player(path)
    except nx.NetworkXNoPath:
        print("No hay camino disponible")


# Función para mover al jugador paso a paso
def move_player(path, index=1):
    global player_pos
    if index < len(path):
        new_pos = path[index]
        dx = (new_pos[0] - player_pos[0]) * cell_size
        dy = (new_pos[1] - player_pos[1]) * cell_size
        canvas.move(player, dx, dy)
        player_pos = new_pos
        window.after(200, lambda: move_player(path, index + 1))  # Retraso para animación


# Botón para iniciar el movimiento con A*
button = tk.Button(window, text="Iniciar A*", command=find_path)
button.pack()

# Iniciar el loop de Tkinter
window.mainloop()
