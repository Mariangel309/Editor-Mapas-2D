from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QPushButton, QAction, QFileDialog, QMessageBox, QLabel, 
    QDockWidget, QListWidget, QListWidgetItem, QDialog, 
    QSpinBox, QFormLayout, QDialogButtonBox, QInputDialog
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QPixmap, QIcon
import os

from modelo.mapa import Mapa, Tile, TILES_CONFIG, crear_tile_desde_config
from modelo.cargador_tiles import cargar_tiles_desde_assets
from exportacion.gestor_archivos import GestorArchivos
from .map_canvas import MapView


class NewMapDialog(QDialog):
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
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editor de Mapas 2D")
        self.resize(1200, 800)

        self.gestor_archivos = GestorArchivos()
        self.archivo_actual = None

        self.map_view = MapView()
        self.setCentralWidget(self.map_view)

        # Crear paneles
        self._create_left_palette()
        self._create_right_panel()

        # Barra de estado
        self.status = self.statusBar()
        self.status.showMessage("Listo - Crea un nuevo mapa para empezar")

        self._create_menu()

    # =========================================================
    # MENÚ PRINCIPAL
    # =========================================================
    def _create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&Archivo")
        view_menu = menubar.addMenu("&Vista")
        tools_menu = menubar.addMenu("&Herramientas")
        edit_menu = menubar.addMenu("&Edición")
        export_menu = menubar.addMenu("E&xportar")

        undo_action = QAction("⟲ Deshacer", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("⟳ Rehacer", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)

        new_action = QAction("📄 Nuevo mapa", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.action_new_map)
        
        open_action = QAction("📂 Abrir...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.action_open)
        
        save_action = QAction("💾 Guardar", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.action_save)
        
        save_as_action = QAction("💾 Guardar como...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.action_save_as)
        
        exit_action = QAction("🚪 Salir", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)

        file_menu.addActions([new_action, open_action, save_action, save_as_action])
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # Vista
        zoom_in = QAction("🔍 Zoom in", self)
        zoom_in.setShortcut("Ctrl++")
        zoom_in.triggered.connect(self.map_view.zoom_in)
        
        zoom_out = QAction("🔍 Zoom out", self)
        zoom_out.setShortcut("Ctrl+-")
        zoom_out.triggered.connect(self.map_view.zoom_out)
        
        reset_zoom = QAction("🔍 Reset zoom", self)
        reset_zoom.setShortcut("Ctrl+0")
        reset_zoom.triggered.connect(self.map_view.reset_zoom)
        
        toggle_grid = QAction("⊞ Mostrar/Ocultar cuadrícula", self)
        toggle_grid.setShortcut("G")
        toggle_grid.triggered.connect(self.toggle_grid)

        view_menu.addActions([zoom_in, zoom_out, reset_zoom, toggle_grid])

        # Herramientas
        tools_menu.addAction("✏️ Lápiz (1)", lambda: self.cambiar_herramienta('lapiz'))
        tools_menu.addAction("🧹 Borrador (2)", lambda: self.cambiar_herramienta('borrador'))
        tools_menu.addAction("🎨 Relleno (3)", lambda: self.cambiar_herramienta('relleno'))
        tools_menu.addAction("🚫 Colisión (4)", lambda: self.cambiar_herramienta('colision'))

        # Exportar
        export_game_action = QAction("🎮 Exportar para motor de juego", self)
        export_game_action.setShortcut("Ctrl+E")
        export_game_action.triggered.connect(self.action_export_game)
        
        export_png_action = QAction("🖼️ Exportar como PNG", self)
        export_png_action.setShortcut("Ctrl+P")
        export_png_action.triggered.connect(self.action_export_png)

        export_menu.addActions([export_game_action, export_png_action])

    # =========================================================
    # PALETA COMBINADA (IMÁGENES + COLORES)
    # =========================================================
    def _create_left_palette(self):
        dock = QDockWidget("Paleta de Tiles", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        widget = QWidget()
        layout = QVBoxLayout()

        # --- Tiles con imágenes desde assets ---
        layout.addWidget(QLabel("<b>Tiles con Imágenes (assets/tiles):</b>"))
        self.palette_images = QListWidget()
        self.palette_images.setIconSize(QSize(32, 32))
        self.palette_images.itemClicked.connect(self._on_tile_selected)
        self.tiles_cargados = cargar_tiles_desde_assets()

        for tipo, tile in self.tiles_cargados.items():
            item = QListWidgetItem(f"🖼️ {tipo}")
            item.setData(Qt.UserRole, tile)
            if tile.tiene_sprite():
                icon = QIcon(QPixmap(tile.sprite).scaled(32, 32, Qt.KeepAspectRatio))
                item.setIcon(icon)
            self.palette_images.addItem(item)

        layout.addWidget(self.palette_images)

        # --- Tiles por color (de TILES_CONFIG) ---
        layout.addWidget(QLabel("<b>Tiles por Color:</b>"))
        self.palette_colors = QListWidget()
        self.palette_colors.itemClicked.connect(self._on_tile_selected)

        for tipo, config in TILES_CONFIG.items():
            item = QListWidgetItem(f"🎨 {config['nombre']}")
            item.setData(Qt.UserRole, crear_tile_desde_config(tipo))
            color = QColor(config['color'])
            item.setBackground(color)
            if config['colision']:
                item.setText(f"🚫 {config['nombre']}")
            self.palette_colors.addItem(item)

        layout.addWidget(self.palette_colors)

        # --- Preview ---
        self.preview_label = QLabel("Selecciona un tile")
        self.preview_label.setFixedHeight(100)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid gray; background: white;")
        layout.addWidget(self.preview_label)

        layout.addStretch()
        widget.setLayout(layout)
        dock.setWidget(widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

    def _on_tile_selected(self, item):
        tile = item.data(Qt.UserRole)
        self.map_view.establecer_tile_seleccionado(tile)

        if tile.tiene_sprite():
            pixmap = QPixmap(tile.sprite).scaled(64, 64, Qt.KeepAspectRatio)
            self.preview_label.setPixmap(pixmap)
            self.preview_label.setStyleSheet("border: 1px solid gray; background: white;")
        else:
            self.preview_label.setPixmap(QPixmap())
            self.preview_label.setText(tile.tipo)
            self.preview_label.setStyleSheet(f"border: 1px solid gray; background: {tile.color};")

        self.status.showMessage(f"Tile seleccionado: {tile.tipo}")

    # =========================================================
    # PANEL DE CAPAS Y OTRAS FUNCIONES (idéntico a versión previa)
    # =========================================================
    def _create_right_panel(self):
        dock = QDockWidget("Capas", self)
        dock.setAllowedAreas(Qt.RightDockWidgetArea)
        
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("<b>Capas del Mapa:</b>"))
        
        self.layers_list = QListWidget()
        self.layers_list.addItems(["👁️ Fondo", "👁️ Objetos", "👁️ Colisión"])
        self.layers_list.setCurrentRow(0)
        self.layers_list.itemClicked.connect(self._on_layer_changed)
        
        layout.addWidget(self.layers_list)
        
        btn_clear = QPushButton("🗑️ Limpiar Capa")
        btn_clear.clicked.connect(self._clear_layer)
        layout.addWidget(btn_clear)
        
        layout.addStretch()
        widget.setLayout(layout)
        dock.setWidget(widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
    
    # ---- Resto de funciones (undo, redo, guardar, exportar, etc.) ----
    # son las mismas que en tu versión anterior y no se modifican

    
    def _on_layer_changed(self, item):
        texto = item.text().replace('👁️ ', '').lower()
        mapa_capas = {'fondo': 'fondo', 'objetos': 'objetos', 'colisión': 'colision'}
        capa_real = mapa_capas.get(texto)
        
        if self.map_view.mapa and capa_real:
            self.map_view.mapa.cambiar_capa_activa(capa_real)
            self.status.showMessage(f"Capa activa: {capa_real}")

    def _clear_layer(self):
        if not self.map_view.mapa:
            return
        capa_actual = self.map_view.mapa.capa_activa
        reply = QMessageBox.question(
            self, 'Limpiar Capa',
            f'¿Limpiar toda la capa "{capa_actual}"?',
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.map_view.mapa.limpiar_capa(capa_actual)
            self.map_view.dibujar_mapa()
            self.status.showMessage(f"✅ Capa '{capa_actual}' limpiada")

    # =========================================================
    # FUNCIONES BÁSICAS
    # =========================================================
    def cambiar_herramienta(self, herramienta):
        self.map_view.establecer_herramienta(herramienta)
        self.status.showMessage(f"Herramienta activa: {herramienta}")

    def toggle_grid(self):
        self.map_view.mostrar_cuadricula = not self.map_view.mostrar_cuadricula
        self.map_view.dibujar_mapa()
        estado = "visible" if self.map_view.mostrar_cuadricula else "oculta"
        self.status.showMessage(f"Cuadrícula {estado}")

    def undo(self):
        if self.map_view.mapa and hasattr(self.map_view, 'gestor_undo_redo'):
            exito, msg = self.map_view.gestor_undo_redo.deshacer(self.map_view.mapa)
            if exito:
                self.map_view.dibujar_mapa()
            self.status.showMessage(msg)

    def redo(self):
        if self.map_view.mapa and hasattr(self.map_view, 'gestor_undo_redo'):
            exito, msg = self.map_view.gestor_undo_redo.rehacer(self.map_view.mapa)
            if exito:
                self.map_view.dibujar_mapa()
            self.status.showMessage(msg)

    # =========================================================
    # ACCIONES DE ARCHIVO
    # =========================================================
    def action_new_map(self):
        dialog = NewMapDialog(self)
        if dialog.exec_() == dialog.Accepted:
            w, h, tile = dialog.get_values()
            self.map_view.create_new_map(w, h, tile)
            self.archivo_actual = None
            self.status.showMessage(f"✅ Mapa nuevo {w}x{h}, tile={tile}px")

    def action_open(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Abrir mapa", "maps/", "JSON (*.json)")
        if not fname:
            return
        try:
            nombre_archivo = os.path.splitext(os.path.basename(fname))[0]
            exito, mapa, mensaje = self.gestor_archivos.cargar_mapa(nombre_archivo)
            if exito:
                self.map_view.mapa = mapa
                self.map_view.dibujar_mapa()
                self.archivo_actual = nombre_archivo
                self.status.showMessage(f"✅ Mapa cargado: {nombre_archivo}")
                QMessageBox.information(self, "Éxito", mensaje)
            else:
                QMessageBox.critical(self, "Error", mensaje)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar: {str(e)}")

    def action_save(self):
        if not self.map_view.mapa:
            QMessageBox.warning(self, "Guardar", "No hay mapa para guardar")
            return
        if self.archivo_actual is None:
            self.action_save_as()
            return
        exito, mensaje = self.gestor_archivos.guardar_mapa(self.map_view.mapa, self.archivo_actual)
        if exito:
            self.status.showMessage(f"✅ Guardado: {self.archivo_actual}")
            QMessageBox.information(self, "Éxito", mensaje)

    def action_save_as(self):
        if not self.map_view.mapa:
            QMessageBox.warning(self, "Guardar", "No hay mapa para guardar")
            return
        nombre, ok = QInputDialog.getText(self, "Guardar como", "Nombre del mapa:")
        if ok and nombre:
            exito, mensaje = self.gestor_archivos.guardar_mapa(self.map_view.mapa, nombre)
            if exito:
                self.archivo_actual = nombre
                self.status.showMessage(f"✅ Guardado: {nombre}")
                QMessageBox.information(self, "Éxito", mensaje)

    def action_export_game(self):
        if not self.map_view.mapa:
            QMessageBox.warning(self, "Exportar", "No hay mapa para exportar")
            return
        nombre, ok = QInputDialog.getText(self, "Exportar para motor", "Nombre del archivo:")
        if ok and nombre:
            exito, mensaje = self.gestor_archivos.exportar_para_motor(self.map_view.mapa, nombre)
            if exito:
                self.status.showMessage(f"✅ Exportado: {nombre}")
                QMessageBox.information(self, "Éxito", mensaje)

    def action_export_png(self):
        if not self.map_view.mapa:
            QMessageBox.warning(self, "Exportar PNG", "No hay mapa para exportar")
            return
        nombre, ok = QInputDialog.getText(self, "Exportar como PNG", "Nombre de la imagen:")
        if ok and nombre:
            exito, mensaje = self.gestor_archivos.exportar_png(self.map_view.mapa, nombre)
            if exito:
                self.status.showMessage(f"✅ PNG exportado: {nombre}")
                QMessageBox.information(self, "Éxito BONO", mensaje)
