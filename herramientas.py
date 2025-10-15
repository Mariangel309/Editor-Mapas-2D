import pygame
pygame.init()


ANCHO, ALTO = 900, 600
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption(" Panel de Herramientas")


ROSA_CLARO = (255, 192, 203)
ROSA = (255, 160, 180)
LILA = (220, 200, 255)
CELESTE = (180, 220, 255)
BLANCO = (255, 255, 255)
GRIS_SUAVE = (245, 245, 245)
NEGRO = (50, 50, 50)


fuente = pygame.font.SysFont("Sangria", 25, bold=False)


herramientas = ["Lápiz", "Borrador", "Cuadro", " Círculo"]
herramienta_actual = herramientas[0]


ejecutando = True
while ejecutando:
    ventana.fill(GRIS_SUAVE)

    
    pygame.draw.rect(ventana, LILA, (0, 0, 230, ALTO))
    titulo = fuente.render("Herramientas", True, NEGRO)
    ventana.blit(titulo, (35, 15))

    for i, nombre in enumerate(herramientas):
        y = 80 + i * 80
       
        if nombre == herramienta_actual:
            pygame.draw.rect(ventana, ROSA, (30, y, 170, 50), border_radius=20)
        else:
            pygame.draw.rect(ventana, BLANCO, (30, y, 170, 50), border_radius=20)
            pygame.draw.rect(ventana, CELESTE, (30, y, 170, 50), 2, border_radius=20)
        texto = fuente.render(nombre, True, NEGRO)
        ventana.blit(texto, (45, y + 10))

    
    texto_act = fuente.render(f"Herramienta actual: {herramienta_actual}", True, NEGRO)
    ventana.blit(texto_act, (270, 20))

    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            x, y = evento.pos
            if x < 230:
                for i, nombre in enumerate(herramientas):
                    if 30 <= x <= 200 and (80 + i * 80) <= y <= (130 + i * 80):
                        herramienta_actual = nombre

    pygame.display.flip()

pygame.quit()



