"""
Snake - Juego de la serpiente con tkinter (sin instalar nada extra).

Controles:
  Flechas o W/A/S/D  -> mover
  P                  -> pausa
  Espacio o R        -> reiniciar
"""
import random
import tkinter as tk

CELDA = 25
COLUMNAS = 24
FILAS = 20
VELOCIDAD_INICIAL = 140   # milisegundos por movimiento
VELOCIDAD_MINIMA = 60

COLOR_FONDO = "#1e1e2e"
COLOR_CUADRICULA = "#262637"
COLOR_CABEZA = "#a6e3a1"
COLOR_CUERPO = "#74c786"
COLOR_COMIDA = "#f38ba8"
COLOR_TEXTO = "#cdd6f4"

DIRECCIONES = {
    "Up": (0, -1), "w": (0, -1),
    "Down": (0, 1), "s": (0, 1),
    "Left": (-1, 0), "a": (-1, 0),
    "Right": (1, 0), "d": (1, 0),
}


class Snake:
    def __init__(self, root):
        self.root = root
        root.title("Snake")
        root.resizable(False, False)

        self.record = 0
        self.etiqueta = tk.Label(
            root, text="", font=("Consolas", 14, "bold"),
            bg=COLOR_FONDO, fg=COLOR_TEXTO, anchor="w", padx=10,
        )
        self.etiqueta.pack(fill="x")

        self.canvas = tk.Canvas(
            root, width=COLUMNAS * CELDA, height=FILAS * CELDA,
            bg=COLOR_FONDO, highlightthickness=0,
        )
        self.canvas.pack()

        root.bind("<Key>", self.tecla)
        self.nuevo_juego()

    # ---------- Estado del juego ----------
    def nuevo_juego(self):
        cx, cy = COLUMNAS // 2, FILAS // 2
        self.serpiente = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direccion = (1, 0)
        self.proxima_direccion = (1, 0)
        self.puntos = 0
        self.velocidad = VELOCIDAD_INICIAL
        self.terminado = False
        self.pausado = False
        self.comida = self.nueva_comida()
        self.actualizar_marcador()
        self.dibujar()
        self.root.after(self.velocidad, self.bucle)

    def nueva_comida(self):
        libres = [
            (x, y) for x in range(COLUMNAS) for y in range(FILAS)
            if (x, y) not in self.serpiente
        ]
        return random.choice(libres) if libres else None

    def actualizar_marcador(self):
        self.etiqueta.config(
            text=f"Puntos: {self.puntos}    Récord: {self.record}"
        )

    # ---------- Entrada ----------
    def tecla(self, evento):
        k = evento.keysym
        if k in ("space", "r", "R") and self.terminado:
            self.nuevo_juego()
            return
        if k in ("p", "P") and not self.terminado:
            self.pausado = not self.pausado
            if not self.pausado:
                self.root.after(self.velocidad, self.bucle)
            self.dibujar()
            return
        if k in DIRECCIONES:
            dx, dy = DIRECCIONES[k]
            # No permitir girar 180 grados
            if (dx, dy) != (-self.direccion[0], -self.direccion[1]):
                self.proxima_direccion = (dx, dy)

    # ---------- Bucle principal ----------
    def bucle(self):
        if self.terminado or self.pausado:
            return

        self.direccion = self.proxima_direccion
        hx, hy = self.serpiente[0]
        nueva_cabeza = (hx + self.direccion[0], hy + self.direccion[1])

        # Colisiones con paredes o con el propio cuerpo
        x, y = nueva_cabeza
        if (not 0 <= x < COLUMNAS or not 0 <= y < FILAS
                or nueva_cabeza in self.serpiente[:-1]):
            self.terminado = True
            self.record = max(self.record, self.puntos)
            self.actualizar_marcador()
            self.dibujar()
            return

        self.serpiente.insert(0, nueva_cabeza)
        if nueva_cabeza == self.comida:
            self.puntos += 10
            self.velocidad = max(VELOCIDAD_MINIMA, self.velocidad - 4)
            self.comida = self.nueva_comida()
            self.actualizar_marcador()
        else:
            self.serpiente.pop()

        self.dibujar()
        self.root.after(self.velocidad, self.bucle)

    # ---------- Dibujo ----------
    def dibujar(self):
        c = self.canvas
        c.delete("all")

        for x in range(COLUMNAS + 1):
            c.create_line(x * CELDA, 0, x * CELDA, FILAS * CELDA, fill=COLOR_CUADRICULA)
        for y in range(FILAS + 1):
            c.create_line(0, y * CELDA, COLUMNAS * CELDA, y * CELDA, fill=COLOR_CUADRICULA)

        if self.comida:
            fx, fy = self.comida
            c.create_oval(
                fx * CELDA + 3, fy * CELDA + 3,
                (fx + 1) * CELDA - 3, (fy + 1) * CELDA - 3,
                fill=COLOR_COMIDA, outline="",
            )

        for i, (x, y) in enumerate(self.serpiente):
            c.create_rectangle(
                x * CELDA + 1, y * CELDA + 1,
                (x + 1) * CELDA - 1, (y + 1) * CELDA - 1,
                fill=COLOR_CABEZA if i == 0 else COLOR_CUERPO, outline="",
            )

        if self.terminado:
            self.mensaje("¡Game Over!", "Presiona ESPACIO para reiniciar")
        elif self.pausado:
            self.mensaje("Pausa", "Presiona P para continuar")

    def mensaje(self, titulo, subtitulo):
        ancho, alto = COLUMNAS * CELDA, FILAS * CELDA
        self.canvas.create_text(
            ancho // 2, alto // 2 - 15, text=titulo,
            fill=COLOR_TEXTO, font=("Consolas", 32, "bold"),
        )
        self.canvas.create_text(
            ancho // 2, alto // 2 + 25, text=subtitulo,
            fill=COLOR_TEXTO, font=("Consolas", 14),
        )


if __name__ == "__main__":
    ventana = tk.Tk()
    Snake(ventana)
    ventana.mainloop()
