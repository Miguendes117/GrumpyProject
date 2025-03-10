import tkinter as tk
from tkinter import messagebox
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
costs = {"normal": 1, "moderate": 3, "difficult": 5, "peligroso": 20}  # Peligroso = costoso para evitarlo

# Crear la ventana
window = tk.Tk()
window.title("Grumpy")

canvas = tk.Canvas(window, width=grid_width * cell_size, height=grid_height * cell_size, bg="white")
canvas.pack()

# Contador
counter_label = tk.Label(window, text=f"Contador: {counter}", font=("Arial", 12))
counter_label.pack()

# Estado del sistema
state_label = tk.Label(window, text=f"Estado: {current_state}", font=("Arial", 12))
state_label.pack()

# Cargar imágenes
panda_img = Image.open("images/panda.jpg").resize((cell_size - 10, cell_size - 10), Image.Resampling.LANCZOS)
panda_img = ImageTk.PhotoImage(panda_img)
window.panda_img = panda_img  

moneda_img = Image.open("images/moneda.jpg").resize((cell_size - 10, cell_size - 10), Image.Resampling.LANCZOS)
moneda_img = ImageTk.PhotoImage(moneda_img)
window.moneda_img = moneda_img  

grumpy_img = Image.open("images/grumpy.jpg").resize((cell_size - 10, cell_size - 10), Image.Resampling.LANCZOS)
grumpy_img = ImageTk.PhotoImage(grumpy_img)
window.grumpy_img = grumpy_img  

# Crear el grafo
graph = nx.grid_2d_graph(grid_width, grid_height)

# Obstáculos
obstacles = {(1, 1), (2, 3), (3, 5), (4, 7), (5, 9), (6, 2), (7, 4), (8, 6), (9, 8), (0, 9)}
moderate_terrain = {(1, 4), (3, 3), (9, 5), (6, 8)}
difficult_terrain = {(4, 8), (7, 7), (5, 5)}

# 🟠 Ubicación de "Grumpy" y sus celdas de peligro
grumpy_pos = (5, 3)
danger_zones = {(grumpy_pos[0] - 1, grumpy_pos[1]), (grumpy_pos[0] + 1, grumpy_pos[1]),
                (grumpy_pos[0], grumpy_pos[1] - 1), (grumpy_pos[0], grumpy_pos[1] + 1)}

# Asignar costes
for i, j in graph.edges():
    if i in moderate_terrain or j in moderate_terrain:
        graph[i][j]['weight'] = costs["moderate"]
    elif i in difficult_terrain or j in difficult_terrain:
        graph[i][j]['weight'] = costs["difficult"]
    elif i in danger_zones or j in danger_zones:
        graph[i][j]['weight'] = costs["peligroso"]  # Coste alto para evitar estas celdas
    else:
        graph[i][j]['weight'] = costs["normal"]

# Eliminar nodos de obstáculos
for obstacle in obstacles:
    if graph.has_node(obstacle):
        graph.remove_node(obstacle)

# Dibujar cuadrícula
# Dibujar cuadrícula con colores y agregar ❌ en celdas naranjas
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


# Posición inicial del jugador y meta
player_pos = (6, 0)
goal_pos = (9, 9)

# Dibujar jugador (imagen del panda)
player = canvas.create_image(
    player_pos[0] * cell_size + cell_size // 2,
    player_pos[1] * cell_size + cell_size // 2,
    image=window.panda_img
)

# Dibujar meta (imagen de la moneda)
goal = canvas.create_image(
    goal_pos[0] * cell_size + cell_size // 2,
    goal_pos[1] * cell_size + cell_size // 2,
    image=window.moneda_img
)

# Dibujar "Grumpy"
grumpy = canvas.create_image(
    grumpy_pos[0] * cell_size + cell_size // 2,
    grumpy_pos[1] * cell_size + cell_size // 2,
    image=window.grumpy_img
)

# Heurística Manhattan
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# Cambiar estado
def change_state(new_state):
    global current_state, current_path
    current_state = new_state
    state_label.config(text=f"Estado: {current_state}")

    if current_state == State.BUSCANDO_CAMINO:
        find_path()
    elif current_state == State.MOVIENDO_JUGADOR and current_path is not None:
        move_player(current_path)
    elif current_state == State.LLEGADA:
        print("¡Llegaste a la meta!")
        show_restart_dialog()  # Mostrar cuadro de diálogo al llegar a la meta
    elif current_state == State.SIN_CAMINO:
        print("No hay camino disponible.")
        show_restart_dialog()  # Mostrar cuadro de diálogo si no hay camino disponible

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
        canvas.coords(player, new_x, new_y)
        player_pos = new_pos
        window.after(200, lambda: move_player(path, index + 1))
    else:
        change_state(State.LLEGADA)

# Mostrar cuadro de diálogo
def show_restart_dialog():
    result = messagebox.askyesno("Reiniciar", "¿Quieres volver a ejecutarlo?")
    if result:
        reset_game()  # Reiniciar el juego si la respuesta es sí
    else:
        window.quit()  # Cerrar la ventana si la respuesta es no

# Reiniciar el juego
def reset_game():
    global player_pos, counter, current_state, current_path
    player_pos = (0, 0)
    counter = 0
    current_path = None
    change_state(State.INICIO)
    canvas.coords(player, player_pos[0] * cell_size + cell_size // 2, player_pos[1] * cell_size + cell_size // 2)
    counter_label.config(text=f"Contador: {counter}")
    state_label.config(text=f"Estado: {current_state if current_state else 'Desconocido'}")


    # 🔥 Aquí se vuelve a iniciar la búsqueda automáticamente
    change_state(State.BUSCANDO_CAMINO)

change_state(State.BUSCANDO_CAMINO)  # Iniciar la búsqueda del camino
window.mainloop()