"""
Sistema de Undo/Redo para el editor.
"""
from copy import deepcopy


class Accion:
    #Representa una acción que se puede deshacer
    
    def __init__(self, tipo, datos):
        self.tipo = tipo
        self.datos = datos
    
    def __repr__(self):
        return f"Accion({self.tipo})"


class GestorUndoRedo:
    
    def __init__(self, limite=50):
        self.pila_undo = []
        self.pila_redo = []
        self.limite = limite
    
    def registrar_accion(self, accion):
        self.pila_undo.append(accion)
        self.pila_redo.clear()
        
        if len(self.pila_undo) > self.limite:
            self.pila_undo.pop(0)
    
    def puede_deshacer(self):
        return len(self.pila_undo) > 0
    
    def puede_rehacer(self):
        return len(self.pila_redo) > 0
    
    def deshacer(self, mapa):
        if not self.puede_deshacer():
            return False, "No hay acciones para deshacer"
        
        accion = self.pila_undo.pop()
        
        try:
            if accion.tipo == 'colocar_tile':
                x, y, capa, tile_anterior = accion.datos
                
                # Guardar estado actual para redo
                tile_actual = mapa.capas[capa][y][x]
                self.pila_redo.append(
                    Accion('colocar_tile', (x, y, capa, tile_actual))
                )
                
                # Restaurar estado anterior
                mapa.capas[capa][y][x] = tile_anterior
                return True, "✅ Acción deshecha"
            
            elif accion.tipo == 'toggle_colision':
                x, y, estado_anterior = accion.datos
                
                estado_actual = mapa.capas['colision'][y][x]
                self.pila_redo.append(
                    Accion('toggle_colision', (x, y, estado_actual))
                )
                
                mapa.capas['colision'][y][x] = estado_anterior
                return True, "✅ Colisión deshecha"
            
            elif accion.tipo == 'flood_fill':
                tiles_modificados = accion.datos
                capa = mapa.capa_activa
                
                tiles_actuales = []
                for x, y, _ in tiles_modificados:
                    tile_actual = mapa.capas[capa][y][x]
                    tiles_actuales.append((x, y, tile_actual))
                
                self.pila_redo.append(
                    Accion('flood_fill', tiles_actuales)
                )
                
                # Restaurar tiles anteriores
                for x, y, tile_anterior in tiles_modificados:
                    mapa.capas[capa][y][x] = tile_anterior
                
                return True, "✅ Relleno deshecho"
        
        except Exception as e:
            return False, f"❌ Error al deshacer: {str(e)}"
    
    def rehacer(self, mapa):
        if not self.puede_rehacer():
            return False, "No hay acciones para rehacer"
        
        accion = self.pila_redo.pop()
        
        try:
            if accion.tipo == 'colocar_tile':
                x, y, capa, tile_nuevo = accion.datos
                
                # Guardar estado actual para undo
                tile_actual = mapa.capas[capa][y][x]
                self.pila_undo.append(
                    Accion('colocar_tile', (x, y, capa, tile_actual))
                )
                
                # Aplicar estado nuevo
                mapa.capas[capa][y][x] = tile_nuevo
                return True, "✅ Acción rehecha"
            
            elif accion.tipo == 'toggle_colision':
                x, y, estado_nuevo = accion.datos
                
                # Guardar estado actual para undo
                estado_actual = mapa.capas['colision'][y][x]
                self.pila_undo.append(
                    Accion('toggle_colision', (x, y, estado_actual))
                )
                
                # Aplicar estado nuevo
                mapa.capas['colision'][y][x] = estado_nuevo
                return True, "✅ Colisión rehecha"
            
            elif accion.tipo == 'flood_fill':
                tiles_nuevos = accion.datos
                capa = mapa.capa_activa
                
                # Guardar estado actual para undo
                tiles_actuales = []
                for x, y, _ in tiles_nuevos:
                    tile_actual = mapa.capas[capa][y][x]
                    tiles_actuales.append((x, y, tile_actual))
                
                self.pila_undo.append(
                    Accion('flood_fill', tiles_actuales)
                )
                
                # Aplicar tiles nuevos
                for x, y, tile_nuevo in tiles_nuevos:
                    mapa.capas[capa][y][x] = tile_nuevo
                
                return True, "✅ Relleno rehecho"
        
        except Exception as e:
            return False, f"❌ Error al rehacer: {str(e)}"
    
    def limpiar(self):
        self.pila_undo.clear()
        self.pila_redo.clear()
    
    def obtener_estado(self):
        return {
            'puede_deshacer': self.puede_deshacer(),
            'puede_rehacer': self.puede_rehacer(),
            'acciones_undo': len(self.pila_undo),
            'acciones_redo': len(self.pila_redo)
        }


# TEST
if __name__ == '__main__':
    print("✅ Módulo de undo/redo cargado correctamente")
    gestor = GestorUndoRedo()
    print(f"Estado inicial: {gestor.obtener_estado()}")