"""
Canvas del mapa con undo/redo integrado.
"""

from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QWidget
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QPen, QPainter, QBrush, QColor, QPixmap

from modelo.mapa import Mapa, Tile
from modelo.objetos import Objeto
from sistema.undo_redo import GestorUndoRedo, Accion


class MapView(QGraphicsView):
    """Vista del canvas con undo/redo integrado."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

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
        
        # UNDO/REDO
        self.gestor_undo_redo = GestorUndoRedo()

    def create_new_map(self, width_tiles, height_tiles, tile_size):
        """Crea un nuevo mapa."""
        self.mapa = Mapa(width_tiles, height_tiles, tile_size)
        
        w = width_tiles * tile_size
        h = height_tiles * tile_size
        self._scene.clear()
        self._scene.setSceneRect(0, 0, w, h)
        
        # Limpiar historial de undo/redo
        self.gestor_undo_redo.limpiar()
        
        self.dibujar_mapa()
    
    def dibujar_mapa(self):
        """Dibuja el mapa completo."""
        if not self.mapa:
            return
        
        self._scene.clear()
        
        # Dibujar capas
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
        
        self._dibujar_cuadricula()
    
    def _dibujar_cuadricula(self):
        """Dibuja la cuadrícula."""
        if not self.mapa:
            return
        
        w = self.mapa.ancho * self.mapa.tamano_tile
        h = self.mapa.alto * self.mapa.tamano_tile
        size = self.mapa.tamano_tile
        
        pen = QPen(QColor(200, 200, 200, 100))
        pen.setWidth(1)
        
        for x in range(0, w + 1, size):
            self._scene.addLine(x, 0, x, h, pen)
        
        for y in range(0, h + 1, size):
            self._scene.addLine(0, y, w, y, pen)
    
    def establecer_tile_seleccionado(self, tile):
        self.tile_seleccionado = tile
    
    def establecer_herramienta(self, herramienta):
        self.herramienta_activa = herramienta
    
    # ==================== MOUSE CON UNDO/REDO ====================
    
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
        if self.dibujando and self.mapa:
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
                    self.mapa.colocar_tile(grid_x, grid_y, tile_nuevo)
                    
                    # REGISTRAR PARA UNDO
                    accion = Accion('colocar_tile', (grid_x, grid_y, capa, tile_anterior))
                    self.gestor_undo_redo.registrar_accion(accion)
                    
                    self.dibujar_mapa()
            
            elif self.herramienta_activa == 'borrador':
                # GUARDAR ESTADO ANTERIOR
                tile_anterior = self.mapa.obtener_tile(grid_x, grid_y, capa)
                
                # Borrar
                self.mapa.colocar_tile(grid_x, grid_y, None)
                
                # REGISTRAR PARA UNDO
                accion = Accion('colocar_tile', (grid_x, grid_y, capa, tile_anterior))
                self.gestor_undo_redo.registrar_accion(accion)
                
                self.dibujar_mapa()
        
        except ValueError:
            pass
    
    # ==================== ZOOM ====================
    
    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

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