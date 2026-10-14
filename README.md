# Juego-void
# 🎮 Juegos en Python

Colección de dos juegos hechos en Python: un clásico **Snake** y un shooter espacial de supervivencia llamado **Neon Void**.

| Juego | Archivo | Librería | Dificultad de instalación |
|-------|---------|----------|---------------------------|
| 🐍 Snake | `snake.py` | `tkinter` (incluida con Python) | Ninguna |
| 🚀 Neon Void | `neon_void.py` | `pygame` | `pip install pygame` |

---

## Requisitos

- Python 3.8 o superior
- Para Neon Void: [pygame](https://www.pygame.org/) 2.x

## Instalación

```bash
# 1. Descarga o clona los archivos en una carpeta
# 2. (Opcional) crea un entorno virtual
python -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate

# 3. Instala la dependencia de Neon Void
pip install pygame
```

## Cómo ejecutar

```bash
python snake.py
python neon_void.py
```

---

## 🐍 Snake

El clásico juego de la serpiente: come, crece y evita chocar con las paredes o con tu propio cuerpo.

### Controles

| Tecla | Acción |
|-------|--------|
| Flechas o `W` `A` `S` `D` | Mover la serpiente |
| `P` | Pausar / continuar |
| `Espacio` o `R` | Reiniciar tras perder |

### Características

- Cada comida suma 10 puntos y acelera un poco el juego.
- Marcador de puntos y récord de la sesión.
- No permite girar 180° sobre sí misma.

> El récord de Snake se mantiene solo mientras la ventana esté abierta.

---

## 🚀 Neon Void

Shooter espacial *twin-stick*: te mueves con el teclado, apuntas con el ratón y sobrevives a oleadas de enemigos cada vez más duras.

### Controles

| Control | Acción |
|---------|--------|
| `W` `A` `S` `D` o flechas | Mover la nave |
| Ratón | Apuntar |
| Clic izquierdo o `J` | Disparar |
| `Espacio` | Dash (esquiva con invulnerabilidad breve) |
| `P` o `ESC` | Pausa |
| `R` | Reiniciar en Game Over |

### Enemigos

| Enemigo | Comportamiento |
|---------|----------------|
| 🔺 Perseguidor | Rápido, te persigue y choca contra ti |
| ◆ Tirador | Mantiene la distancia y dispara balas |
| ⬢ Tanque | Lento pero con mucha vida |
| ⯃ Jefe | Aparece cada 5 oleadas: dispara anillos de balas, invoca perseguidores y se enfurece al bajar de la mitad de vida |

### Power-ups

Los enemigos pueden soltarlos al morir (el jefe siempre suelta uno).

| Icono | Efecto | Duración |
|-------|--------|----------|
| `+` | Recupera vida | Instantáneo |
| `R` | Disparo rápido | 10 s |
| `3` | Disparo triple | 10 s |
| `S` | Escudo que absorbe un golpe | 15 s |

### Mecánicas

- **Oleadas:** cada una trae más enemigos y más resistentes. Al completarla recuperas algo de vida.
- **Combo:** matar enemigos seguidos sube el multiplicador de puntos hasta **x5**; si pasas 2 segundos sin matar, se reinicia.
- **Récord:** se guarda automáticamente en `neon_void_record.json`, junto al juego. Bórralo si quieres reiniciar el récord.

---

## Estructura del proyecto

```
.
├── snake.py                  # Juego Snake
├── neon_void.py              # Juego Neon Void
├── neon_void_record.json     # Se crea solo al batir un récord
└── README.md
```

## Personalización rápida

Ambos juegos tienen constantes al inicio del archivo que puedes cambiar sin tocar la lógica:

**`snake.py`**
- `CELDA`, `COLUMNAS`, `FILAS`: tamaño del tablero.
- `VELOCIDAD_INICIAL`, `VELOCIDAD_MINIMA`: ritmo del juego en milisegundos.
- `COLOR_*`: paleta de colores.

**`neon_void.py`**
- `W`, `H`: tamaño de la ventana.
- `ENEMY_TYPES`: vida, velocidad, daño y puntos de cada enemigo.
- `POWERUPS`: colores y símbolos de los power-ups.

## Solución de problemas

**`ModuleNotFoundError: No module named 'pygame'`**
Instálalo con `pip install pygame` (o `pip3 install pygame`).

**`ModuleNotFoundError: No module named 'tkinter'`** (sobre todo en Linux)
```bash
sudo apt install python3-tk       # Debian / Ubuntu
sudo dnf install python3-tkinter  # Fedora
```

**Neon Void va lento**
Cierra otras aplicaciones pesadas o reduce `W` y `H` en `neon_void.py`.

**El comando `python` no funciona**
Prueba con `python3 snake.py` y `python3 neon_void.py`.

---

## Ideas para ampliar

- Sonido y música
- Más armas y mejoras entre oleadas
- Modo cooperativo local
- Tabla de mejores puntuaciones
- Más tipos de enemigos y jefes
