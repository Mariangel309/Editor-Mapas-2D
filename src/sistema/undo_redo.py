"""
Sistema de Undo/Redo para el editor.
"""

from copy import deepcopy


class Accion:
    """Representa una acción que se puede deshacer."""
    
    def __init__(self, tipo, datos):
        self.tipo = tipo
        self.datos = datos


class GestorUndoRedo:
    """Gestor del sistema de deshacer/rehacer."""
    
    def __init__(self, limite=50):
        self.pila_undo = []
        self.pila_redo = []
        self.limite = limite
    
    def registrar_accion(self, accion):
        """Registra una acción para poder deshacerla."""
        self.pila_undo.append(accion)
        self.pila_redo.clear()
        
        if len(self.pila_undo) > self.limite:
            self.pila_undo.pop(0)
    
    def puede_deshacer(self):
        return len(self.pila_undo) > 0
    
    def puede_rehacer(self):
        return len(self.pila_redo) > 0
    
    def deshacer(self, mapa):
        """Deshace la última acción."""
        if not self.puede_deshacer():
            return False, "No hay acciones para deshacer"
        
        accion = self.pila_undo.pop()
        
        try:
            if accion.tipo == 'colocar_tile':
                x, y, capa, tile_anterior = accion.datos
                tile_actual = mapa.capas[capa][y][x]
                self.pila_redo.append(
                    Accion('colocar_tile', (x, y, capa, tile_actual))
                )
                mapa.capas[capa][y][x] = tile_anterior
                return True, "Acción deshecha"
        
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def rehacer(self, mapa):
        """Rehace la última acción deshecha."""
        if not self.puede_rehacer():
            return False, "No hay acciones para rehacer"
        
        accion = self.pila_redo.pop()
        
        try:
            if accion.tipo == 'colocar_tile':
                x, y, capa, tile_nuevo = accion.datos
                tile_actual = mapa.capas[capa][y][x]
                self.pila_undo.append(
                    Accion('colocar_tile', (x, y, capa, tile_actual))
                )
                mapa.capas[capa][y][x] = tile_nuevo
                return True, "Acción rehecha"
        
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def limpiar(self):
        """Limpia ambas pilas."""
        self.pila_undo.clear()
        self.pila_redo.clear()


# TEST
if __name__ == '__main__':
    print("✅ Módulo de undo/redo cargado correctamente")