from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QToolBar, QAction, QFileDialog,
                             QColorDialog, QMessageBox, QLabel, QButtonGroup,
                             QDockWidget, QListWidget, QListWidgetItem, QDialog,
                             QSpinBox, QFormLayout, QDialogButtonBox, QInputDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import os

from modelo.mapa import Mapa, Tile, TILES_CONFIG, crear_tile_desde_config
from modelo.objetos import Objeto
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

        # Gestor de archivos
        self.gestor_archivos = GestorArchivos()
        self.archivo_actual = None

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

    def _create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&Archivo")
        view_menu = menubar.addMenu("&Vista")
        tools_menu = menubar.addMenu("&Herramientas")
        menu_edicion = menubar.addMenu("&Edición")
        export_menu = menubar.addMenu("E&xportar")


        undo_action = QAction("⟲ Deshacer", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo)
        menu_edicion.addAction(undo_action)

        redo_action = QAction("⟳ Rehacer", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.redo)
        menu_edicion.addAction(redo_action)

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

        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addSeparator()
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

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

        view_menu.addAction(zoom_in)
        view_menu.addAction(zoom_out)
        view_menu.addAction(reset_zoom)
        view_menu.addSeparator()
        view_menu.addAction(toggle_grid)

        pencil_action = QAction("✏️ Lápiz", self)
        pencil_action.setShortcut("1")
        pencil_action.triggered.connect(lambda: self.cambiar_herramienta('lapiz'))
        
        eraser_action = QAction("🧹 Borrador", self)
        eraser_action.setShortcut("2")
        eraser_action.triggered.connect(lambda: self.cambiar_herramienta('borrador'))
        
        fill_action = QAction("🎨 Relleno", self)
        fill_action.setShortcut("3")
        fill_action.triggered.connect(lambda: self.cambiar_herramienta('relleno'))
        
        collision_action = QAction("🚫 Colisión", self)
        collision_action.setShortcut("4")
        collision_action.triggered.connect(lambda: self.cambiar_herramienta('colision'))

        tools_menu.addAction(pencil_action)
        tools_menu.addAction(eraser_action)
        tools_menu.addAction(fill_action)
        tools_menu.addAction(collision_action)

        export_game_action = QAction("🎮 Exportar para motor de juego", self)
        export_game_action.setShortcut("Ctrl+E")
        export_game_action.triggered.connect(self.action_export_game)
        
        export_png_action = QAction("🖼️ Exportar como PNG", self)
        export_png_action.setShortcut("Ctrl+P")
        export_png_action.triggered.connect(self.action_export_png)

        export_menu.addAction(export_game_action)
        export_menu.addAction(export_png_action)

    def toggle_grid(self):
        """Alterna la visibilidad de la cuadrícula."""
        self.map_view.mostrar_cuadricula = not self.map_view.mostrar_cuadricula
        self.map_view.dibujar_mapa()
        estado = "visible" if self.map_view.mostrar_cuadricula else "oculta"
        self.status.showMessage(f"Cuadrícula {estado}")
    
    def undo(self):
        """Deshacer última acción."""
        if self.map_view.mapa and hasattr(self.map_view, 'gestor_undo_redo'):
            exito, msg = self.map_view.gestor_undo_redo.deshacer(self.map_view.mapa)
            if exito:
                self.map_view.dibujar_mapa()
            self.status.showMessage(msg)
        else:
            self.status.showMessage("No hay acciones para deshacer")

    def redo(self):
        """Rehacer última acción deshecha."""
        if self.map_view.mapa and hasattr(self.map_view, 'gestor_undo_redo'):
            exito, msg = self.map_view.gestor_undo_redo.rehacer(self.map_view.mapa)
            if exito:
                self.map_view.dibujar_mapa()
            self.status.showMessage(msg)
        else:
            self.status.showMessage("No hay acciones para rehacer")

    def _create_left_palette(self):
        dock = QDockWidget("Paleta de Tiles", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        
        widget = QWidget()
        layout = QVBoxLayout()


        layout.addWidget(QLabel("<b>Tiles Disponibles:</b>"))


        self.palette_list = QListWidget()
        self.palette_list.itemClicked.connect(self._on_tile_selected)
        

        for tipo, config in TILES_CONFIG.items():
            item = QListWidgetItem(f"  {config['nombre']}")
            item.setData(Qt.UserRole, tipo)
            

            color = QColor(config['color'])
            item.setBackground(color)
            

            if config['colision']:
                item.setText(f"🚫 {config['nombre']}")
            
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
        
        self.tool_buttons = []
        
        btn_pencil = QPushButton("✏️ Lápiz (1)")
        btn_pencil.clicked.connect(lambda: self.cambiar_herramienta('lapiz'))
        btn_pencil.setCheckable(True)
        btn_pencil.setChecked(True)
        layout.addWidget(btn_pencil)
        self.tool_buttons.append(('lapiz', btn_pencil))
        
        btn_eraser = QPushButton("🧹 Borrador (2)")
        btn_eraser.clicked.connect(lambda: self.cambiar_herramienta('borrador'))
        btn_eraser.setCheckable(True)
        layout.addWidget(btn_eraser)
        self.tool_buttons.append(('borrador', btn_eraser))
        
        btn_fill = QPushButton("🎨 Relleno (3)")
        btn_fill.clicked.connect(lambda: self.cambiar_herramienta('relleno'))
        btn_fill.setCheckable(True)
        layout.addWidget(btn_fill)
        self.tool_buttons.append(('relleno', btn_fill))
        
        btn_collision = QPushButton("🚫 Colisión (4)")
        btn_collision.clicked.connect(lambda: self.cambiar_herramienta('colision'))
        btn_collision.setCheckable(True)
        layout.addWidget(btn_collision)
        self.tool_buttons.append(('colision', btn_collision))

        layout.addStretch()
        widget.setLayout(layout)
        dock.setWidget(widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)
    
    def _on_tile_selected(self, item):
        #Cuando se selecciona un tile de la paleta
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


    def _create_right_panel(self):
        """Panel de capas conectado al modelo."""
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
        
        mapa_capas = {
            'fondo': 'fondo',
            'objetos': 'objetos',
            'colisión': 'colision'
        }
        
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

    def cambiar_herramienta(self, herramienta):
        """Cambia la herramienta activa."""
        self.map_view.establecer_herramienta(herramienta)
        
        # Actualizar botones
        for nombre, btn in self.tool_buttons:
            btn.setChecked(nombre == herramienta)
        
        nombres = {
            'lapiz': 'Lápiz',
            'borrador': 'Borrador',
            'relleno': 'Relleno',
            'colision': 'Colisión'
        }
        self.status.showMessage(f"Herramienta: {nombres.get(herramienta, herramienta)}")

    def action_new_map(self):
        #Crea un nuevo mapa usando el modelo.
        dialog = NewMapDialog(self)
        if dialog.exec_() == dialog.Accepted:
            w, h, tile = dialog.get_values()
            
            self.map_view.create_new_map(w, h, tile)
            self.archivo_actual = None
            
            self.status.showMessage(f"✅ Mapa nuevo {w}x{h}, tile={tile}px")

    def action_open(self):
        """Abrir mapa."""
        fname, _ = QFileDialog.getOpenFileName(
            self, "Abrir mapa", "maps/", "JSON Files (*.json);;All Files (*)"
        )
        
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
        
        try:
            exito, mensaje = self.gestor_archivos.guardar_mapa(
                self.map_view.mapa, 
                self.archivo_actual
            )
            
            if exito:
                self.status.showMessage(f"✅ Guardado: {self.archivo_actual}")
                QMessageBox.information(self, "Éxito", mensaje)
            else:
                QMessageBox.critical(self, "Error", mensaje)
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
    
    def action_save_as(self):
        if not self.map_view.mapa:
            QMessageBox.warning(self, "Guardar", "No hay mapa para guardar")
            return
        
        nombre, ok = QInputDialog.getText(
            self, "Guardar como", 
            "Nombre del mapa:"
        )
        
        if ok and nombre:
            try:
                exito, mensaje = self.gestor_archivos.guardar_mapa(
                    self.map_view.mapa, 
                    nombre
                )
                
                if exito:
                    self.archivo_actual = nombre
                    self.status.showMessage(f"✅ Guardado: {nombre}")
                    QMessageBox.information(self, "Éxito", mensaje)
                else:
                    QMessageBox.critical(self, "Error", mensaje)
            
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {str(e)}")
    
    def action_export_game(self):
        if not self.map_view.mapa:
            QMessageBox.warning(self, "Exportar", "No hay mapa para exportar")
            return
        
        nombre, ok = QInputDialog.getText(
            self, "Exportar para motor", 
            "Nombre del archivo de exportación:"
        )
        
        if ok and nombre:
            try:
                exito, mensaje = self.gestor_archivos.exportar_para_motor(
                    self.map_view.mapa, 
                    nombre
                )
                
                if exito:
                    self.status.showMessage(f"✅ Exportado: {nombre}")
                    QMessageBox.information(self, "Éxito", mensaje)
                else:
                    QMessageBox.critical(self, "Error", mensaje)
            
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {str(e)}")
    
    def action_export_png(self):
        #Exportar mapa como PNG (BONO).
        if not self.map_view.mapa:
            QMessageBox.warning(self, "Exportar PNG", "No hay mapa para exportar")
            return
        
        nombre, ok = QInputDialog.getText(
            self, "Exportar como PNG", 
            "Nombre de la imagen:"
        )
        
        if ok and nombre:
            try:
                exito, mensaje = self.gestor_archivos.exportar_png(
                    self.map_view.mapa, 
                    nombre
                )
                
                if exito:
                    self.status.showMessage(f"✅ PNG exportado: {nombre}")
                    QMessageBox.information(self, "Éxito BONO", mensaje)
                else:
                    QMessageBox.critical(self, "Error", mensaje)
            
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {str(e)}")