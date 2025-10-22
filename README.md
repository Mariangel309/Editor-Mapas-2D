# 🎮 Editor de Mapas 2D para Videojuegos

**Laboratorio 1 - Estructura de Datos I**  
Desarrollado por: Maria Angel Martinez, Santiago Jimenez, Paulo Poveda y Gabriela Hernandez

## 📝 Descripción:

Este es un editor de mapas tipo tile-based hecho en Python con PyQt5. Básicamente permite diseñar niveles para videojuegos 2D dibujando en una cuadrícula, similar a lo que hacen editores como Tiled pero más sencillo.

El proyecto lo hicimos en equipo dividiendo el trabajo en módulos:

- **Modelo**: La lógica del mapa y los tiles
- **Herramientas**: Las funciones de dibujo
- **Exportación**: Guardar y cargar mapas
- **Sistema**: Integración de todo y la interfaz gráfica

-----

## 🚀 Cómo ejecutar el proyecto

### Requisitos previos

Necesitas tener instalado:

- Python 3.8 o superior
- pip (viene con Python)

### Instalación

1. Clona el repositorio o descarga el proyecto:

```bash
git clone https://github.com/Mariangel309/Editor-Mapas-2D.git
cd Editor-Mapas-2D
```

1. Instala las dependencias:

```bash
pip install PyQt5 Pillow
```

1. Ejecuta el programa:

```bash
cd src
python main.py
```

Y listo, se abre la ventana del editor.

## 🎨 Cómo usar el editor

### Crear un nuevo mapa

1. Archivo → Nuevo mapa (o Ctrl+N)
1. Elige las dimensiones:
- Ancho y alto en tiles
- Tamaño de cada tile en píxeles (recomiendo 32px)
1. Click en OK

### Dibujar en el mapa

**Panel izquierdo** - Selecciona tiles:

- Hay diferentes tipos: pasto, tierra, agua, piedra, etc.
- Los que tienen 🚫 son tiles con colisión (bloquean el paso)

**Herramientas disponibles**:

1. **Lápiz** (tecla 1): Dibuja tile por tile
1. **Borrador** (tecla 2): Borra tiles
1. **Relleno** (tecla 3): Rellena áreas del mismo color (tipo paint bucket)
1. **Colisión** (tecla 4): Marca zonas donde el jugador no puede pasar

**Capas**:

- Fondo: La capa base del mapa
- Objetos: Para poner cosas encima
- Colisión: Marca colisiones (se ven en rojo transparente)

### Guardar y cargar

- **Guardar**: Archivo → Guardar (Ctrl+S)
  - Primera vez te pide un nombre
  - Se guarda en la carpeta `maps/` como JSON
- **Cargar**: Archivo → Abrir (Ctrl+O)
  - Selecciona el archivo .json del mapa

### Exportar

**Para el motor del juego**:

- Exportar → Exportar para motor de juego (Ctrl+E)
- Genera un JSON optimizado en `exports/`
- Este archivo es el que usarías en tu juego

**Como imagen PNG** (Del Bono):

- Exportar → Exportar como PNG (Ctrl+P)
- Te genera una imagen del mapa completo
- Útil para mostrar o documentar

### Otros atajos útiles

- `Ctrl+Z`: Deshacer
- `Ctrl+Y`: Rehacer
- `G`: Mostrar/ocultar cuadrícula
- `Ctrl++`: Zoom in
- `Ctrl+-`: Zoom out
- `Ctrl+0`: Resetear zoom

Aparte de la paleta de colores disponibles, también importar tus propios assets de tiles para dibujar en la carpeta de assets/tiles

## 🔧 Decisiones de diseño

### Estructuras de datos usadas

**1. Matrices bidimensionales** (para las capas del mapa)

```python
# Cada capa es una matriz de tiles
capas = {
    'fondo': [[2. Instala las dependencias:
```bash
pip install PyQt5 Pillow
``` for _ in range(ancho)] for _ in range(alto)],
    'objetos': [[None for _ in range(ancho)] for _ in range(alto)],
    'colision': [[False for _ in range(ancho)] for _ in range(alto)]
}
```

¿Por qué? Porque el mapa es básicamente una cuadrícula 2D, entonces usar una lista de listas es lo más natural. El acceso a cualquier posición es O(1) con `mapa[y][x]`.

**2. Pilas** (para undo/redo)

```python
pila_undo = []  # Guarda acciones hechas
pila_redo = []  # Guarda acciones deshechas
```

Usamos pilas porque necesitamos deshacer en orden LIFO (Last In, First Out). La última acción que hiciste es la primera que se deshace. Así funciona en cualquier editor.

**3. Cola (lista)** (para flood fill)

```python
pila = [(start_x, start_y)]
while pila:
    x, y = pila.pop()
    # ... agregar vecinos
    pila.extend([(x+1, y), (x-1, y), ...])
```

Para el relleno usamos una pila iterativa en vez de recursión para evitar stack overflow en mapas grandes. Va visitando cada celda vecina del mismo color.

**4. Diccionarios** (para configuración)

```python
TILES_CONFIG = {
    'pasto': {'nombre': 'Pasto', 'color': '#7CFC00', ...},
    'agua': {'nombre': 'Agua', 'color': '#1E90FF', ...}
}
```

Los diccionarios son perfectos para mapear tipos de tiles a su configuración. Búsqueda O(1) por clave.

### Complejidad

- **Colocar tile**: O(1) - acceso directo a la matriz
- **Flood fill**: O(n) donde n = número de celdas del área rellenada
- **Guardar mapa**: O(ancho × alto) - recorre toda la matriz
- **Deshacer/Rehacer**: O(1) - pop/push en pila

### Por qué PyQt5 y no Pygame

Al principio uno de los compañeros hizo su parte en Pygame pero tuvimos que cambiarlo a PyQt5 porque:

- PyQt5 tiene widgets ya hechos (menús, botones, diálogos)
- Pygame es más para juegos, no para hacer herramientas
- PyQt5 se ve más profesional y es más fácil hacer UI complejas


## 🧪 Casos de prueba

Probamos el editor con:

1. **Mapa pequeño** (10×10): Funciona perfecto, todas las herramientas
1. **Mapa grande** (100×100):
- Tarda un poco en guardar pero funciona
- El relleno puede ser lento en áreas muy grandes
- El undo/redo se limita a 50 acciones para no llenar la memoria
1. **Archivo corrupto**:
- Probamos cargar un JSON con errores
- El programa muestra error y no crashea
1. **Múltiples capas**:
- Puedes dibujar en fondo, objetos y colisión sin problemas
- Cada capa es independiente


## 🐛 Problemas que tuvimos (y cómo los resolvimos)

### Error 1: Imports no funcionaban

**Problema**: Python no encontraba los módulos  
**Solución**: Configuramos los imports relativos correctamente y agregamos `__init__.py` en cada carpeta

### Error 2: La ñ en “tamaño_tile”

**Problema**: Problemas de encoding con caracteres especiales  
**Solución**: Cambiamos todo a `tamano_tile` sin ñ para evitar issues

### Error 3: Flood fill hacía stack overflow

**Problema**: Con recursión en mapas grandes se llenaba la pila  
**Solución**: Lo cambiamos a iterativo con una pila manual

### Error 4: Capa de colisión no se veía

**Problema**: Al dibujar colisiones no se veía nada  
**Solución**: Agregamos overlay rojo semi-transparente

-----

## Lo que aprendimos

- **Trabajo en equipo**: Dividir el proyecto en módulos y luego integrarlos
- **Git/GitHub**: Usar branches y hacer pull requests
- **Estructuras de datos**: Aplicar pilas, matrices y diccionarios en un proyecto real
- **PyQt5**: Hacer interfaces gráficas con Qt
- **Serialización**: Guardar estructuras complejas en JSON
- **Manejo de errores**: Try-catch y validaciones

-----

## Mejoras futuras

Si tuviéramos más tiempo agregaríamos:

- [ ] Múltiples spawn points (ahora solo soporta la lista pero no hay UI)
- [ ] Tiles animados (la estructura está pero no se usa)
- [ ] Copiar/pegar selecciones rectangulares
- [ ] Layers con opacidad ajustable
- [ ] Vista previa del mapa en miniatura
- [ ] Modo oscuro en la interfaz
