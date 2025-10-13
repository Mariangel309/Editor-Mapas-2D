from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QPainter

class MapView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        # Mejor renderizado
        self.setRenderHints(self.renderHints() | 
                    QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        # Permitir arrastrar el lienzo con el mouse
        self.setDragMode(QGraphicsView.ScrollHandDrag)

        # Parámetros de zoom
        self._zoom = 0
        self._zoom_step = 1.15
        self._max_zoom = 10
        self._min_zoom = -10

        # Parámetros del mapa
        self.map_width = 0
        self.map_height = 0
        self.tile_size = 32

    def create_new_map(self, width_tiles, height_tiles, tile_size):
        """Crea un nuevo mapa con una cuadrícula de tiles."""
        self.map_width = width_tiles
        self.map_height = height_tiles
        self.tile_size = tile_size

        w = width_tiles * tile_size
        h = height_tiles * tile_size
        self._scene.clear()
        self._scene.setSceneRect(0, 0, w, h)

        pen = QPen(Qt.gray)
        pen.setWidth(0)

        # Líneas verticales
        for x in range(0, w + 1, tile_size):
            self._scene.addLine(x, 0, x, h, pen)

        # Líneas horizontales
        for y in range(0, h + 1, tile_size):
            self._scene.addLine(0, y, w, y, pen)

    # Eventos de zoom
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
