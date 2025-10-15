import pygame

pygame.init()

ANCHO, ALTO = 950, 600
PANEL_W = 250
COLOR_PANEL = (230, 210, 255)
COLOR_FONDO = (255, 255, 255)
COLOR_BOTON = (245, 235, 255)
COLOR_HOVER = (210, 180, 255)
COLOR_SELECCION = (180, 150, 255)

ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Panel de Herramientas")

FUENTE = pygame.font.SysFont("Comic Sans MS", 18, bold=True)
TAM_CELDA = 24
FILAS = ALTO // TAM_CELDA
COLUMNAS = (ANCHO - PANEL_W) // TAM_CELDA
mapa = [[COLOR_FONDO for _ in range(COLUMNAS)] for _ in range(FILAS)]

herramientas = ["Lápiz", "Borrador", "Relleno", "Selección", "Colisión", "Spawn"]
herramienta_actual = "Lápiz"
dibujando = False
borrando = False
seleccionando = False
bloque_seleccionado = None
inicio_sel = None
modo_pegar = False

colores = [
    (255, 100, 180), (255, 150, 80), (255, 220, 100),
    (180, 255, 150), (100, 200, 255), (180, 150, 255),
    (255, 255, 255), (0, 0, 0)
]
color_dibujo = colores[0]

COLOR_COLISION = (150, 150, 150)
COLOR_SPAWN = (120, 255, 120)

def flood_fill(mapa, fila, col, color_ant, color_nuevo):
    if color_ant == color_nuevo or mapa[fila][col] != color_ant:
        return
    pila = [(fila, col)]
    while pila:
        f, c = pila.pop()
        if 0 <= f < FILAS and 0 <= c < COLUMNAS and mapa[f][c] == color_ant:
            mapa[f][c] = color_nuevo
            pila += [(f+1, c), (f-1, c), (f, c+1), (f, c-1)]

reloj = pygame.time.Clock()
ejecutando = True

while ejecutando:
    ventana.fill(COLOR_FONDO)
    pygame.draw.rect(ventana, COLOR_PANEL, (0, 0, PANEL_W, ALTO))
    mx, my = pygame.mouse.get_pos()

    for i, herramienta in enumerate(herramientas):
        y = 30 + i * 60
        boton = pygame.Rect(20, y, 200, 45)
        color = COLOR_HOVER if boton.collidepoint((mx, my)) else COLOR_BOTON
        pygame.draw.rect(ventana, color, boton, border_radius=10)
        texto = FUENTE.render(herramienta, True, (80, 20, 120))
        ventana.blit(texto, (50, y + 10))
        if herramienta == herramienta_actual:
            pygame.draw.rect(ventana, (150, 80, 255), boton, 3, border_radius=10)

    ventana.blit(FUENTE.render("Colores:", True, (70, 30, 100)), (20, 400))
    for i, color in enumerate(colores):
        x = 20 + (i % 4) * 50
        y = 430 + (i // 4) * 50
        rect = pygame.Rect(x, y, 40, 40)
        pygame.draw.rect(ventana, color, rect)
        if rect.collidepoint((mx, my)):
            pygame.draw.rect(ventana, (120, 80, 200), rect, 3)
        if color == color_dibujo:
            pygame.draw.rect(ventana, (0, 0, 0), rect, 3)

    for f in range(FILAS):
        for c in range(COLUMNAS):
            x = PANEL_W + c * TAM_CELDA
            y = f * TAM_CELDA
            pygame.draw.rect(ventana, mapa[f][c], (x, y, TAM_CELDA, TAM_CELDA))
            pygame.draw.rect(ventana, (220, 220, 220), (x, y, TAM_CELDA, TAM_CELDA), 1)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            ejecutando = False

        elif e.type == pygame.MOUSEBUTTONDOWN:
            x, y = e.pos
            if x < PANEL_W:
                for i, herramienta in enumerate(herramientas):
                    boton = pygame.Rect(20, 30 + i * 60, 200, 45)
                    if boton.collidepoint((x, y)):
                        herramienta_actual = herramienta
                        dibujando = borrando = seleccionando = modo_pegar = False
                        bloque_seleccionado = None

                for i, color in enumerate(colores):
                    cx = 20 + (i % 4) * 50
                    cy = 430 + (i // 4) * 50
                    rect = pygame.Rect(cx, cy, 40, 40)
                    if rect.collidepoint((x, y)):
                        color_dibujo = color

            else:
                col = (x - PANEL_W) // TAM_CELDA
                fila = y // TAM_CELDA
                if not (0 <= fila < FILAS and 0 <= col < COLUMNAS):
                    continue

                if herramienta_actual == "Lápiz":
                    dibujando = True
                    mapa[fila][col] = color_dibujo

                elif herramienta_actual == "Borrador":
                    borrando = True
                    mapa[fila][col] = COLOR_FONDO

                elif herramienta_actual == "Relleno":
                    flood_fill(mapa, fila, col, mapa[fila][col], color_dibujo)

                elif herramienta_actual == "Selección":
                    if bloque_seleccionado is None and not modo_pegar:
                        seleccionando = True
                        inicio_sel = (fila, col)
                    elif bloque_seleccionado is not None:
                        for i, fila_sel in enumerate(bloque_seleccionado):
                            for j, color in enumerate(fila_sel):
                                if 0 <= fila+i < FILAS and 0 <= col+j < COLUMNAS:
                                    mapa[fila+i][col+j] = color
                        bloque_seleccionado = None
                        modo_pegar = False

                elif herramienta_actual == "Colisión":
                    mapa[fila][col] = COLOR_COLISION

                elif herramienta_actual == "Spawn":
                    mapa[fila][col] = COLOR_SPAWN

        elif e.type == pygame.MOUSEBUTTONUP:
            dibujando = borrando = False
            if seleccionando and inicio_sel:
                x, y = e.pos
                col = (x - PANEL_W) // TAM_CELDA
                fila = y // TAM_CELDA
                f1, f2 = sorted([inicio_sel[0], fila])
                c1, c2 = sorted([inicio_sel[1], col])
                bloque_seleccionado = [fila[c1:c2+1] for fila in mapa[f1:f2+1]]
                seleccionando = False
                inicio_sel = None
                for f in range(f1, f2+1):
                    for c in range(c1, c2+1):
                        mapa[f][c] = COLOR_FONDO
                modo_pegar = True

        elif e.type == pygame.MOUSEMOTION:
            x, y = e.pos
            col = (x - PANEL_W) // TAM_CELDA
            fila = y // TAM_CELDA
            if 0 <= fila < FILAS and 0 <= col < COLUMNAS:
                if dibujando:
                    mapa[fila][col] = color_dibujo
                elif borrando:
                    mapa[fila][col] = COLOR_FONDO

    if bloque_seleccionado and modo_pegar:
        mx, my = pygame.mouse.get_pos()
        f = my // TAM_CELDA
        c = (mx - PANEL_W) // TAM_CELDA
        for i, fila_sel in enumerate(bloque_seleccionado):
            for j, color in enumerate(fila_sel):
                if 0 <= f+i < FILAS and 0 <= c+j < COLUMNAS:
                    x = PANEL_W + (c+j) * TAM_CELDA
                    y = (f+i) * TAM_CELDA
                    pygame.draw.rect(ventana, color, (x, y, TAM_CELDA, TAM_CELDA))
                    pygame.draw.rect(ventana, COLOR_SELECCION, (x, y, TAM_CELDA, TAM_CELDA), 1)

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()
