import pygame
pygame.init()


ANCHO, ALTO = 900, 600
TAM_CELDA = 30
COLUMNAS = (ANCHO - 230) // TAM_CELDA 
FILAS = ALTO // TAM_CELDA

ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption(" Editor de Mapas - Herramientas Gaby 💖")


LILA = (220, 200, 255)
ROSA = (255, 180, 200)
CELESTE = (180, 220, 255)
BLANCO = (255, 255, 255)
GRIS_CLARO = (240, 240, 240)
NEGRO = (50, 50, 50)
COLOR_LAPIZ = (255, 105, 180)
COLOR_BORRADO = BLANCO


fuente = pygame.font.SysFont("Sangria", 24)


herramientas = [" Lápiz", " Borrador"]
herramienta_actual = herramientas[0]


mapa = [[BLANCO for _ in range(COLUMNAS)] for _ in range(FILAS)]


def dibujar_panel():
    pygame.draw.rect(ventana, LILA, (0, 0, 230, ALTO))
    titulo = fuente.render(" Herramientas", True, NEGRO)
    ventana.blit(titulo, (40, 15))
    for i, nombre in enumerate(herramientas):
        y = 70 + i * 80
        color = ROSA if nombre == herramienta_actual else BLANCO
        pygame.draw.rect(ventana, color, (30, y, 170, 50), border_radius=15)
        texto = fuente.render(nombre, True, NEGRO)
        ventana.blit(texto, (45, y + 10))

def dibujar_cuadricula():
    for fila in range(FILAS):
        for col in range(COLUMNAS):
            x = 230 + col * TAM_CELDA
            y = fila * TAM_CELDA
            pygame.draw.rect(ventana, mapa[fila][col], (x, y, TAM_CELDA, TAM_CELDA))
            pygame.draw.rect(ventana, GRIS_CLARO, (x, y, TAM_CELDA, TAM_CELDA), 1)


ejecutando = True
pintando = False  

while ejecutando:
    ventana.fill(BLANCO)
    dibujar_panel()
    dibujar_cuadricula()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

        elif evento.type == pygame.MOUSEBUTTONDOWN:
            x, y = evento.pos
            if x < 230:  
                for i, nombre in enumerate(herramientas):
                    if 30 <= x <= 200 and (70 + i * 80) <= y <= (120 + i * 80):
                        herramienta_actual = nombre
            else:
                pintando = True  

        elif evento.type == pygame.MOUSEBUTTONUP:
            pintando = False 

    
    if pintando:
        x, y = pygame.mouse.get_pos()
        if x > 230:  
            col = (x - 230) // TAM_CELDA
            fila = y // TAM_CELDA
            if 0 <= fila < FILAS and 0 <= col < COLUMNAS:
                if herramienta_actual == " Lápiz":
                    mapa[fila][col] = COLOR_LAPIZ
                elif herramienta_actual == " Borrador":
                    mapa[fila][col] = COLOR_BORRADO

    #
    texto_act = fuente.render(f"Herramienta: {herramienta_actual}", True, NEGRO)
    ventana.blit(texto_act, (250, 20))

    pygame.display.flip()

pygame.quit()



