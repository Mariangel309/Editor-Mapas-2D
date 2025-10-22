
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QWidget
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QPen, QPainter, QBrush, QColor, QPixmap

from modelo.mapa import Mapa, Tile
from modelo.objetos import Objeto
from sistema.undo_redo import GestorUndoRedo, Accion


class MapView(QGraphicsView):
    #Vista del canvas con undo/redo integrado
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.NoDrag)  

        # Zoom
        self._zoom = 0
        self._zoom_step = 1.15
        self._max_zoom = 10
        self._min_zoom = -10

        # Mapa y herramientas
        self.mapa = None
        self.tile_seleccionado = None
        self.herramienta_activa = 'lapiz'
        self.dibujando = False
        
        # Cuadrícula
        self.mostrar_cuadricula = True
        self.grosor_cuadricula = 1
        
        # UNDO/REDO
        self.gestor_undo_redo = GestorUndoRedo()

    def create_new_map(self, width_tiles, height_tiles, tile_size):
        self.mapa = Mapa(width_tiles, height_tiles, tile_size)
        
        w = width_tiles * tile_size
        h = height_tiles * tile_size
        self._scene.clear()
        self._scene.setSceneRect(0, 0, w, h)
        
        self.gestor_undo_redo.limpiar()
        
        self.dibujar_mapa()
    
    def dibujar_mapa(self):
        #Dibuja el mapa completo.
        if not self.mapa:
            return
        
        self._scene.clear()
        
        for nombre_capa in ['fondo', 'objetos']:
            for y in range(self.mapa.alto):
                for x in range(self.mapa.ancho):
                    tile = self.mapa.obtener_tile(x, y, nombre_capa)
                    
                    if tile is None:
                        continue
                    
                    px = x * self.mapa.tamano_tile
                    py = y * self.mapa.tamano_tile
                    size = self.mapa.tamano_tile
                    
                    if tile.tiene_sprite():
                        pixmap = QPixmap(tile.sprite)
                        pixmap = pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        item = QGraphicsPixmapItem(pixmap)
                        item.setPos(px, py)
                        self._scene.addItem(item)
                    else:
                        color = QColor(tile.color)
                        self._scene.addRect(
                            px, py, size, size,
                            QPen(QColor(200, 200, 200)),
                            QBrush(color)
                        )
        
        # Dibujar capa de colisión (con transparencia)
        for y in range(self.mapa.alto):
            for x in range(self.mapa.ancho):
                if self.mapa.capas['colision'][y][x]:
                    px = x * self.mapa.tamano_tile
                    py = y * self.mapa.tamano_tile
                    size = self.mapa.tamano_tile
                    
                    # Color rojo semi-transparente para colisiones
                    color = QColor(255, 0, 0, 100)
                    self._scene.addRect(
                        px, py, size, size,
                        QPen(QColor(255, 0, 0)),
                        QBrush(color)
                    )
        
        # Dibujar cuadrícula
        if self.mostrar_cuadricula:
            self._dibujar_cuadricula()
    
    def _dibujar_cuadricula(self):
        if not self.mapa:
            return
        
        w = self.mapa.ancho * self.mapa.tamano_tile
        h = self.mapa.alto * self.mapa.tamano_tile
        size = self.mapa.tamano_tile
        
        # Cuadrícula más sutil
        pen = QPen(QColor(180, 180, 180, 80))
        pen.setWidth(self.grosor_cuadricula)
        
        for x in range(0, w + 1, size):
            self._scene.addLine(x, 0, x, h, pen)
        
        for y in range(0, h + 1, size):
            self._scene.addLine(0, y, w, y, pen)
    
    def establecer_tile_seleccionado(self, tile):
        self.tile_seleccionado = tile
    
    def establecer_herramienta(self, herramienta):
        self.herramienta_activa = herramienta
    
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.mapa:
            scene_pos = self.mapToScene(event.pos())
            x = int(scene_pos.x())
            y = int(scene_pos.y())
            
            grid_x = x // self.mapa.tamano_tile
            grid_y = y // self.mapa.tamano_tile
            
            self.dibujando = True
            self._aplicar_herramienta(grid_x, grid_y)
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self.dibujando and self.mapa and self.herramienta_activa in ['lapiz', 'borrador', 'colision']:
            scene_pos = self.mapToScene(event.pos())
            x = int(scene_pos.x())
            y = int(scene_pos.y())
            
            grid_x = x // self.mapa.tamano_tile
            grid_y = y // self.mapa.tamano_tile
            
            self._aplicar_herramienta(grid_x, grid_y)
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dibujando = False
        super().mouseReleaseEvent(event)
    
    def _aplicar_herramienta(self, grid_x, grid_y):
        """Aplica herramienta CON registro de undo."""
        if not self.mapa._validar_coordenadas(grid_x, grid_y):
            return
        
        try:
            capa = self.mapa.capa_activa
            
            if self.herramienta_activa == 'lapiz':
                if self.tile_seleccionado:
                    # GUARDAR ESTADO ANTERIOR
                    tile_anterior = self.mapa.obtener_tile(grid_x, grid_y, capa)
                    
                    # Colocar tile
                    tile_nuevo = self.tile_seleccionado.clonar()
                    self.mapa.colocar_tile(grid_x, grid_y, tile_nuevo, capa)
                    
                    # REGISTRAR PARA UNDO
                    accion = Accion('colocar_tile', (grid_x, grid_y, capa, tile_anterior))
                    self.gestor_undo_redo.registrar_accion(accion)
                    
                    self.dibujar_mapa()
            
            elif self.herramienta_activa == 'borrador':
                tile_anterior = self.mapa.obtener_tile(grid_x, grid_y, capa)
                
                self.mapa.colocar_tile(grid_x, grid_y, None, capa)
                
                accion = Accion('colocar_tile', (grid_x, grid_y, capa, tile_anterior))
                self.gestor_undo_redo.registrar_accion(accion)
                
                self.dibujar_mapa()
            
            elif self.herramienta_activa == 'relleno':
                if self.mapa.capa_activa == 'colision':
                    return
                if self.tile_seleccionado:
                    self._flood_fill(grid_x, grid_y)

            
            elif self.herramienta_activa == 'colision':
                estado_anterior = self.mapa.capas['colision'][grid_y][grid_x]
                self.mapa.capas['colision'][grid_y][grid_x] = not estado_anterior
                
                accion = Accion('toggle_colision', (grid_x, grid_y, estado_anterior))
                self.gestor_undo_redo.registrar_accion(accion)
                
                self.dibujar_mapa()
        
        except (ValueError, IndexError):
            pass
    
    def _flood_fill(self, start_x, start_y):
        """Algoritmo de relleno (flood fill)."""
        if not self.tile_seleccionado or not self.mapa:
            return
        # Evitar flood fill si la capa es de colisión o no guarda Tiles
        if self.mapa.capa_activa == 'colision':
            return

        
        capa = self.mapa.capa_activa
        
        tile_original = self.mapa.obtener_tile(start_x, start_y, capa)
        tipo_original = tile_original.tipo if tile_original else None
        
        if tile_original and tile_original.tipo == self.tile_seleccionado.tipo:
            return
        
        pila = [(start_x, start_y)]
        visitados = set()
        tiles_modificados = []
        
        while pila:
            x, y = pila.pop()
            
            if (x, y) in visitados:
                continue
            
            if not self.mapa._validar_coordenadas(x, y):
                continue
            
            tile_actual = self.mapa.obtener_tile(x, y, capa)
            tipo_actual = tile_actual.tipo if tile_actual else None
            
            if tipo_actual != tipo_original:
                continue
            
            visitados.add((x, y))
            
            # Guardar estado anterior
            tiles_modificados.append((x, y, tile_actual))
            
            # Colocar nuevo tile
            tile_nuevo = self.tile_seleccionado.clonar()
            self.mapa.colocar_tile(x, y, tile_nuevo, capa)
            
            pila.extend([
                (x + 1, y),
                (x - 1, y),
                (x, y + 1),
                (x, y - 1)
            ])
        
        if tiles_modificados:
            accion = Accion('flood_fill', tiles_modificados)
            self.gestor_undo_redo.registrar_accion(accion)
        
        self.dibujar_mapa()
    
    
    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
        else:
            super().wheelEvent(event)

    def zoom_in(self):
        if self._zoom < self._max_zoom:
            self.scale(self._zoom_step, self._zoom_step)
            self._zoom += 1

    def zoom_out(self):
        if self._zoom > self._min_zoom:
            self.scale(1 / self._zoom_step, 1 / self._zoom_step)
            self._zoom -= 1

    def reset_zoom(self):
        while self._zoom > 0:
            self.zoom_out()
        while self._zoom < 0:
            self.zoom_in()