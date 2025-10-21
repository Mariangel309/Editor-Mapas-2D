"""
Sistema de herramientas del editor integrado con PyQt5 y el modelo.
"""

from abc import ABC, abstractmethod
from src.modelo import Mapa, Tile


class Herramienta(ABC):
    """Clase base abstracta para todas las herramientas."""
    
    def __init__(self, nombre):
        self.nombre = nombre
    
    @abstractmethod
    def mouse_press(self, x, y, mapa, tile_seleccionado=None):
        """Se llama cuando se presiona el mouse."""
        pass
    
    @abstractmethod
    def mouse_move(self, x, y, mapa, tile_seleccionado=None):
        """Se llama cuando se mueve el mouse."""
        pass
    
    @abstractmethod
    def mouse_release(self, x, y, mapa, tile_seleccionado=None):
        """Se llama cuando se suelta el mouse."""
        pass


class HerramientaLapiz(Herramienta):
    """Herramienta para dibujar tiles individuales."""
    
    def __init__(self):
        super().__init__("Lápiz")
        self.dibujando = False
    
    def mouse_press(self, x, y, mapa, tile_seleccionado=None):
        self.dibujando = True
        self._dibujar(x, y, mapa, tile_seleccionado)
    
    def mouse_move(self, x, y, mapa, tile_seleccionado=None):
        if self.dibujando:
            self._dibujar(x, y, mapa, tile_seleccionado)
    
    def mouse_release(self, x, y, mapa, tile_seleccionado=None):
        self.dibujando = False
    
    def _dibujar(self, x, y, mapa, tile):
        """Coloca el tile seleccionado en la posición."""
        if not tile or not mapa:
            return
        
        grid_x = x // mapa.tamano_tile
        grid_y = y // mapa.tamano_tile
        
        try:
            # Clonar el tile para que cada celda tenga su propia instancia
            tile_nuevo = tile.clonar()
            mapa.colocar_tile(grid_x, grid_y, tile_nuevo)
        except ValueError:
            pass  # Fuera del mapa


class HerramientaBorrador(Herramienta):
    """Herramienta para borrar tiles."""
    
    def __init__(self):
        super().__init__("Borrador")
        self.borrando = False
    
    def mouse_press(self, x, y, mapa, tile_seleccionado=None):
        self.borrando = True
        self._borrar(x, y, mapa)
    
    def mouse_move(self, x, y, mapa, tile_seleccionado=None):
        if self.borrando:
            self._borrar(x, y, mapa)
    
    def mouse_release(self, x, y, mapa, tile_seleccionado=None):
        self.borrando = False
    
    def _borrar(self, x, y, mapa):
        """Borra el tile en la posición."""
        if not mapa:
            return
        
        grid_x = x // mapa.tamano_tile
        grid_y = y // mapa.tamano_tile
        
        try:
            mapa.colocar_tile(grid_x, grid_y, None)
        except ValueError:
            pass


class HerramientaRelleno(Herramienta):
    """Herramienta de flood fill (relleno)."""
    
    def __init__(self):
        super().__init__("Relleno")
    
    def mouse_press(self, x, y, mapa, tile_seleccionado=None):
        if not tile_seleccionado or not mapa:
            return
        
        grid_x = x // mapa.tamano_tile
        grid_y = y // mapa.tamano_tile
        
        if not mapa._validar_coordenadas(grid_x, grid_y):
            return
        
        capa = mapa.capa_activa
        tile_original = mapa.obtener_tile(grid_x, grid_y, capa)
        
        # No hacer nada si es el mismo tipo
        if tile_original and tile_original.tipo == tile_seleccionado.tipo:
            return
        
        # Flood fill
        self._flood_fill(mapa, grid_x, grid_y, tile_original, tile_seleccionado, capa)
    
    def mouse_move(self, x, y, mapa, tile_seleccionado=None):
        pass  # Relleno no se activa con movimiento
    
    def mouse_release(self, x, y, mapa, tile_seleccionado=None):
        pass
    
    def _flood_fill(self, mapa, x, y, tile_original, tile_nuevo, capa):
        """Algoritmo de flood fill iterativo."""
        tipo_original = tile_original.tipo if tile_original else None
        
        pila = [(x, y)]
        visitados = set()
        
        while pila:
            cx, cy = pila.pop()
            
            if (cx, cy) in visitados:
                continue
            
            if not mapa._validar_coordenadas(cx, cy):
                continue
            
            tile_actual = mapa.obtener_tile(cx, cy, capa)
            tipo_actual = tile_actual.tipo if tile_actual else None
            
            if tipo_actual != tipo_original:
                continue
            
            # Colocar nuevo tile
            tile_clon = tile_nuevo.clonar()
            mapa.colocar_tile(cx, cy, tile_clon, capa)
            visitados.add((cx, cy))
            
            # Agregar vecinos
            pila.extend([
                (cx + 1, cy),
                (cx - 1, cy),
                (cx, cy + 1),
                (cx, cy - 1)
            ])


class HerramientaColision(Herramienta):
    """Herramienta para marcar colisiones."""
    
    def __init__(self):
        super().__init__("Colisión")
        self.pintando = False
    
    def mouse_press(self, x, y, mapa, tile_seleccionado=None):
        self.pintando = True
        self._marcar(x, y, mapa)
    
    def mouse_move(self, x, y, mapa, tile_seleccionado=None):
        if self.pintando:
            self._marcar(x, y, mapa)
    
    def mouse_release(self, x, y, mapa, tile_seleccionado=None):
        self.pintando = False
    
    def _marcar(self, x, y, mapa):
        """Marca colisión en la posición."""
        if not mapa:
            return
        
        grid_x = x // mapa.tamano_tile
        grid_y = y // mapa.tamano_tile
        
        if mapa._validar_coordenadas(grid_x, grid_y):
            mapa.capas['colision'][grid_y][grid_x] = True

class HerramientaMover(Herramienta):
    def __init__(self):
        super().__init__("Mover")
        self.origen = None
        self.tile_copiado = None

    def mouse_press(self, x, y, mapa, tile_seleccionado=None):
        grid_x = x
        grid_y = y

        if mapa._validar_coordenadas(grid_x, grid_y):
            self.tile_copiado = mapa.obtener_tile(grid_x, grid_y, mapa.capa_activa)
            self.origen = (grid_x, grid_y)

    def mouse_release(self, x, y, mapa, tile_seleccionado=None):
        if self.tile_copiado and self.origen:
            grid_x = x
            grid_y = y

            if mapa._validar_coordenadas(grid_x, grid_y):
                mapa.colocar_tile(self.origen[0], self.origen[1], None)
                mapa.colocar_tile(grid_x, grid_y, self.tile_copiado)

        self.tile_copiado = None
        self.origen = None
class GestorHerramientas:
    """Gestor que maneja todas las herramientas."""
    
    def __init__(self):
        self.herramientas = {
            'lapiz': HerramientaLapiz(),
            'borrador': HerramientaBorrador(),
            'relleno': HerramientaRelleno(),
            'colision': HerramientaColision()
        }
        self.herramienta_actual = self.herramientas['lapiz']
    
    def cambiar_herramienta(self, nombre):
        """Cambia la herramienta activa."""
        if nombre in self.herramientas:
            self.herramienta_actual = self.herramientas[nombre]
            return True
        return False
    
    def obtener_herramienta_actual(self):
        """Retorna la herramienta actualmente activa."""
        return self.herramienta_actual


# TEST
if __name__ == '__main__':
    print("✅ Módulo de herramientas cargado correctamente")
    gestor = GestorHerramientas()
    print(f"Herramientas disponibles: {list(gestor.herramientas.keys())}")