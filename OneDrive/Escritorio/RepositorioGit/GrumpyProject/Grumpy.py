import tkinter as tk
import networkx as nx

# Parámetros
tamaño_celda = 40
ancho = 10
alto = 10

# Estados del sistema
class Estado:
    INICIO = "Inicio"
    BUSCANDO_CAMINO = "Buscando Camino"
    MOVIENDO_JUGADOR = "Moviendo Jugador"
    LLEGADA = "Llegada"
    SIN_CAMINO = "Sin Camino"

estado_actual = Estado.INICIO
camino_actual = None  # Variable global para almacenar el camino encontrado

# Crear ventana y canvas
ventana = tk.Tk()
ventana.title("Grupmy")

lienzo = tk.Canvas (
    ventana, 
    width=ancho * tamaño_celda, 
    height=alto * tamaño_celda, 
    bg="white"
)

lienzo.pack()

# Etiqueta para mostrar el estado
etiqueta_estado = tk.Label (
    ventana, 
    text=f"Estado: {estado_actual}", 
    font=("Arial", 12)
)

etiqueta_estado.pack()

# Crear el grafo
grafo = nx.grid_2d_graph(ancho, alto)

# Obstáculos
obstaculos = {(1, 1), (2, 3), (3, 5), (4, 7), (5, 9), (6, 2), (7, 4), (8, 6), (9, 8), (0, 9)}
for obst in obstaculos:
    if grafo.has_node(obst):
        grafo.remove_node(obst)

# Dibujar cuadrícula
for i in range(ancho):
    for j in range(alto):
        x1, y1 = i * tamaño_celda, j * tamaño_celda
        x2, y2 = x1 + tamaño_celda, y1 + tamaño_celda
        color = "black" if (i, j) in obstaculos else "white"
        lienzo.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")

# Posiciones inicial y final
pos_jugador = (0, 0)
pos_meta = (9, 9)

# Dibujar jugador
jugador = lienzo.create_rectangle (
    pos_jugador[0] * tamaño_celda + 5, 
    pos_jugador[1] * tamaño_celda + 5,
    (pos_jugador[0] + 1) * tamaño_celda - 5, 
    (pos_jugador[1] + 1) * tamaño_celda - 5,
    fill="blue"
)

# Dibujar meta
lienzo.create_oval (
    pos_meta[0] * tamaño_celda + 10, 
    pos_meta[1] * tamaño_celda + 10,
    (pos_meta[0] + 1) * tamaño_celda - 10, 
    (pos_meta[1] + 1) * tamaño_celda - 10,
    fill="green"
)

# Función heurística
def heuristica(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# Máquina de estados
def cambiar_estado(nuevo_estado):
    global estado_actual, camino_actual
    estado_actual = nuevo_estado
    etiqueta_estado.config(text=f"Estado: {estado_actual}")
    print(f"Estado actual: {estado_actual}")

    if estado_actual == Estado.BUSCANDO_CAMINO:
        buscar_camino()
    elif estado_actual == Estado.MOVIENDO_JUGADOR and camino_actual is not None:
        mover_jugador(camino_actual)
    elif estado_actual == Estado.LLEGADA:
        print("¡Llegaste a la meta!")
    elif estado_actual == Estado.SIN_CAMINO:
        print("No hay camino disponible.")

# Búsqueda del camino
def buscar_camino():
    global camino_actual
    try:
        camino_actual = nx.astar_path(grafo, pos_jugador, pos_meta, heuristic=heuristica)
        cambiar_estado(Estado.MOVIENDO_JUGADOR)
    except nx.NetworkXNoPath:
        cambiar_estado(Estado.SIN_CAMINO)

# Movimiento del jugador
def mover_jugador(camino, indice=1):
    global pos_jugador
    if indice < len(camino):
        nueva_pos = camino[indice]
        dx = (nueva_pos[0] - pos_jugador[0]) * tamaño_celda
        dy = (nueva_pos[1] - pos_jugador[1]) * tamaño_celda
        lienzo.move(jugador, dx, dy)
        pos_jugador = nueva_pos
        ventana.after(200, lambda: mover_jugador(camino, indice + 1))
    else:
        cambiar_estado(Estado.LLEGADA)

# Botón de inicio
boton_iniciar = tk.Button (
    ventana, 
    text="Iniciar A*", 
    command=lambda: cambiar_estado(Estado.BUSCANDO_CAMINO)
)

boton_iniciar.pack()

ventana.mainloop()
