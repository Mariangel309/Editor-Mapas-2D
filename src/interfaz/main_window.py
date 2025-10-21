from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QToolBar, QAction, QFileDialog,
                             QColorDialog, QMessageBox, QLabel, QButtonGroup,
                             QDockWidget, QListWidget, QListWidgetItem, QDialog,
                             QSpinBox, QFormLayout, QDialogButtonBox)  # ← AGREGAR ESTAS
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from modelo.mapa import Mapa, Tile, TILES_CONFIG, crear_tile_desde_config  # ← AGREGAR crear_tile_desde_config
from modelo.objetos import Objeto
from exportacion.gestor_archivos import guardar_mapa_json, cargar_mapa_json, exportar_para_motor
from .map_canvas import MapView


class NewMapDialog(QDialog):
    """Diálogo para crear un nuevo mapa."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Mapa")
        
        layout = QFormLayout()
        
        self.width_spin = QSpinBox()
        self.width_spin.setRange(10, 200)
        self.width_spin.setValue(30)
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(10, 200)
        self.height_spin.setValue(20)
        
        self.tile_spin = QSpinBox()
        self.tile_spin.setRange(8, 64)
        self.tile_spin.setValue(32)
        
        layout.addRow("Ancho (tiles):", self.width_spin)
        layout.addRow("Alto (tiles):", self.height_spin)
        layout.addRow("Tamaño tile (px):", self.tile_spin)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addRow(buttons)
        self.setLayout(layout)
    
    def get_values(self):
        return self.width_spin.value(), self.height_spin.value(), self.tile_spin.value()


class MainWindow(QMainWindow):
    """Ventana principal con integración completa del modelo."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editor de Mapas 2D")
        self.resize(1200, 800)

        # Canvas central
        self.map_view = MapView()
        self.setCentralWidget(self.map_view)

        # Paneles laterales
        self._create_left_palette()
        self._create_right_panel()

        # Barra de estado
        self.status = self.statusBar()
        self.status.showMessage("Listo - Crea un nuevo mapa para empezar")

        # Menú
        self._create_menu()

    # ----------------- Menú superior -----------------
    def _create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&Archivo")
        view_menu = menubar.addMenu("&Vista")
        tools_menu = menubar.addMenu("&Herramientas")
        menu_edicion = menubar.addMenu("&Edición")

        undo_action = QAction("Deshacer", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo)
        menu_edicion.addAction(undo_action)

        redo_action = QAction("Rehacer", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.redo)
        menu_edicion.addAction(redo_action)

        # Archivo
        new_action = QAction("Nuevo mapa", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.action_new_map)
        
        open_action = QAction("Abrir...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.action_open)
        
        save_action = QAction("Guardar...", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.action_save)
        
        exit_action = QAction("Salir", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)

        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # Vista
        zoom_in = QAction("Zoom in", self)
        zoom_in.setShortcut("Ctrl++")
        zoom_in.triggered.connect(self.map_view.zoom_in)
        
        zoom_out = QAction("Zoom out", self)
        zoom_out.setShortcut("Ctrl+-")
        zoom_out.triggered.connect(self.map_view.zoom_out)
        
        reset_zoom = QAction("Reset zoom", self)
        reset_zoom.setShortcut("Ctrl+0")
        reset_zoom.triggered.connect(self.map_view.reset_zoom)

        view_menu.addAction(zoom_in)
        view_menu.addAction(zoom_out)
        view_menu.addAction(reset_zoom)

        # Herramientas
        pencil_action = QAction("Lápiz", self)
        pencil_action.setShortcut("1")
        pencil_action.triggered.connect(lambda: self.cambiar_herramienta('lapiz'))
        
        eraser_action = QAction("Borrador", self)
        eraser_action.setShortcut("2")
        eraser_action.triggered.connect(lambda: self.cambiar_herramienta('borrador'))

        tools_menu.addAction(pencil_action)
        tools_menu.addAction(eraser_action)

    
    def undo(self):
        if self.map_view.mapa and hasattr(self.map_view, 'gestor_undo_redo'):
            exito, msg = self.map_view.gestor_undo_redo.deshacer(self.map_view.mapa)
            if exito:
                self.map_view.dibujar_mapa()
                self.status.showMessage(f"{msg}")
            else:
                self.status.showMessage(f"{msg}")
        else:
            self.status.showMessage("No hay acciones para deshacer")

    
    def redo(self):
        if self.map_view.mapa and hasattr(self.map_view, 'gestor_undo_redo'):
            exito, msg = self.map_view.gestor_undo_redo.rehacer(self.map_view.mapa)
            if exito:
                self.map_view.dibujar_mapa()
                self.status.showMessage(f"{msg}")
            else:
                self.status.showMessage(f"{msg}")
        else:
            self.status.showMessage("No hay acciones para rehacer")

    # ----------------- Panel izquierdo: PALETA REAL -----------------
    def _create_left_palette(self):
        """Crea paleta con tiles reales del modelo."""
        dock = QDockWidget("Paleta de Tiles", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        
        widget = QWidget()
        layout = QVBoxLayout()

        # Título
        layout.addWidget(QLabel("<b>Tiles Disponibles:</b>"))

        # Lista de tiles REALES desde TILES_CONFIG
        self.palette_list = QListWidget()
        self.palette_list.itemClicked.connect(self._on_tile_selected)
        
        # Agregar tiles del modelo
        for tipo, config in TILES_CONFIG.items():
            item = QListWidgetItem(f"  {config['nombre']}")
            item.setData(Qt.UserRole, tipo)  # Guardar tipo
            
            # Color de fondo
            color = QColor(config['color'])
            item.setBackground(color)
            
            self.palette_list.addItem(item)
        
        layout.addWidget(self.palette_list)

        # Preview
        self.preview_label = QLabel("Selecciona un tile")
        self.preview_label.setFixedHeight(100)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid gray; background: white;")
        layout.addWidget(self.preview_label)

        # Sección de herramientas
        layout.addWidget(QLabel("<b>Herramientas:</b>"))
        
        btn_pencil = QPushButton("✏️ Lápiz (1)")
        btn_pencil.clicked.connect(lambda: self.cambiar_herramienta('lapiz'))
        layout.addWidget(btn_pencil)
        
        btn_eraser = QPushButton("🧹 Borrador (2)")
        btn_eraser.clicked.connect(lambda: self.cambiar_herramienta('borrador'))
        layout.addWidget(btn_eraser)

        layout.addStretch()
        widget.setLayout(layout)
        dock.setWidget(widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)
    
    def _on_tile_selected(self, item):
        """Cuando se selecciona un tile de la paleta."""
        tipo = item.data(Qt.UserRole)
        
        # CREAR TILE REAL DEL MODELO
        tile = crear_tile_desde_config(tipo)
        
        # Establecer en el canvas
        self.map_view.establecer_tile_seleccionado(tile)
        
        # Actualizar preview
        config = TILES_CONFIG[tipo]
        self.preview_label.setText(
            f"<b>{config['nombre']}</b><br>"
            f"Color: {config['color']}<br>"
            f"Colisión: {'Sí' if config['colision'] else 'No'}"
        )
        self.preview_label.setStyleSheet(
            f"border: 2px solid black; background: {config['color']};"
        )
        
        self.status.showMessage(f"Tile seleccionado: {config['nombre']}")

    # ----------------- Panel derecho: CAPAS REALES -----------------
    def _create_right_panel(self):
        """Panel de capas conectado al modelo."""
        dock = QDockWidget("Capas", self)
        dock.setAllowedAreas(Qt.RightDockWidgetArea)
        
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("<b>Capas del Mapa:</b>"))
        
        self.layers_list = QListWidget()
        self.layers_list.addItems(["👁️ Fondo", "👁️ Objetos", "👁️ Colisión"])
        self.layers_list.setCurrentRow(0)  # Fondo por defecto
        self.layers_list.itemClicked.connect(self._on_layer_changed)
        
        layout.addWidget(self.layers_list)
        
        # Botón limpiar capa
        btn_clear = QPushButton("🗑️ Limpiar Capa")
        btn_clear.clicked.connect(self._clear_layer)
        layout.addWidget(btn_clear)
        
        layout.addStretch()
        widget.setLayout(layout)
        dock.setWidget(widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
    
    def _on_layer_changed(self, item):
        """Cuando se cambia de capa."""
        texto = item.text().replace('👁️ ', '').lower()
        
        if self.map_view.mapa:
            self.map_view.mapa.cambiar_capa_activa(texto)
            self.status.showMessage(f"Capa activa: {texto}")
    
    def _clear_layer(self):
        """Limpia la capa activa."""
        if not self.map_view.mapa:
            return
        
        reply = QMessageBox.question(
            self, 'Limpiar Capa',
            f'¿Limpiar toda la capa "{self.map_view.mapa.capa_activa}"?',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.map_view.mapa.limpiar_capa(self.map_view.mapa.capa_activa)
            self.map_view.dibujar_mapa()
            self.status.showMessage(f"Capa '{self.map_view.mapa.capa_activa}' limpiada")

    # ----------------- Herramientas -----------------
    def cambiar_herramienta(self, herramienta):
        """Cambia la herramienta activa."""
        self.map_view.establecer_herramienta(herramienta)
        nombres = {
            'lapiz': 'Lápiz',
            'borrador': 'Borrador'
        }
        self.status.showMessage(f"Herramienta: {nombres.get(herramienta, herramienta)}")

    # ----------------- Acciones del menú -----------------
    def action_new_map(self):
        """Crea un nuevo mapa usando el modelo."""
        dialog = NewMapDialog(self)
        if dialog.exec_() == dialog.Accepted:
            w, h, tile = dialog.get_values()
            
            # CREAR MAPA DEL MODELO
            self.map_view.create_new_map(w, h, tile)
            
            self.status.showMessage(f"✅ Mapa nuevo {w}x{h}, tile={tile}px")

    def action_open(self):
        """Abrir mapa (requiere módulo de Persona 4)."""
        fname, _ = QFileDialog.getOpenFileName(
            self, "Abrir mapa", "maps/", "JSON Files (*.json);;All Files (*)"
        )
        if fname:
            QMessageBox.information(
                self, "Abrir", 
                f"Cargar desde: {fname}\n\n"
                f"(Requiere integración con módulo exportacion/)"
            )

    def action_save(self):
        """Guardar mapa (requiere módulo de Persona 4)."""
        if not self.map_view.mapa:
            QMessageBox.warning(self, "Guardar", "No hay mapa para guardar")
            return
        
        fname, _ = QFileDialog.getSaveFileName(
            self, "Guardar mapa", "maps/", "JSON Files (*.json);;All Files (*)"
        )
        if fname:
            QMessageBox.information(
                self, "Guardar", 
                f"Guardar en: {fname}\n\n"
                f"(Requiere integración con módulo exportacion/)"
            )