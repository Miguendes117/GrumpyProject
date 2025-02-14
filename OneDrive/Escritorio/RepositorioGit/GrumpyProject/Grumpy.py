import tkinter as tk

# Crear la ventana principal
window = tk.Tk()
window.title("mapa de grumpy")
window.geometry("440x300")  # Ajusta el tamaño según necesites

# Crear el lienzo (Canvas)
canvas = tk.Canvas(window, width=440, height=300, bg="white")
canvas.pack() #muestra


# Tamaño de las celdas
cell_size = 40

# Dibujar la cuadrícula
for i in range(11):
    for j in range(11):
        x1 = i * cell_size # definimos que el tamaño de las celdas de 40 px
        y1 = j * cell_size
        x2 = x1 + cell_size
        y2 = y1 + cell_size
        canvas.create_rectangle(x1, y1, x2, y2, outline="black")

# Dibujar las celdas negras (obstáculos)
obstacles = [(0, 0), (1, 0), (7, 3), (5, 5), (10, 1), (4, 4)]
for x, y in obstacles:
    x1 = x * cell_size
    y1 = y * cell_size
    x2 = x1 + cell_size
    y2 = y1 + cell_size
    canvas.create_rectangle(x1, y1, x2, y2, fill="black")

# Dibujar el círculo (meta)
canvas.create_oval(4 * cell_size + 10, 1 * cell_size + 10, 5 * cell_size - 10, 2 * cell_size - 10, fill="green")

# Dibujar el cuadrado (jugador)
canvas.create_rectangle(10 * cell_size + 10, 4 * cell_size + 10, 11 * cell_size - 10, 5 * cell_size - 10, fill="blue")

# Iniciar el bucle principal
window.mainloop()