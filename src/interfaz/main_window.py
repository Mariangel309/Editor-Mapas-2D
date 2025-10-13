from PyQt5.QtWidgets import (
    QMainWindow, QAction, QFileDialog, QMessageBox,
    QWidget, QVBoxLayout, QLabel, QDockWidget, QListWidget
)
from PyQt5.QtCore import Qt
from .map_canvas import MapView
from .dialogs import NewMapDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editor de Mapas 2D - Interfaz")
        self.resize(1200, 800)

        # Canvas central
        self.map_view = MapView()
        self.setCentralWidget(self.map_view)

        # Paneles laterales
        self._create_left_palette()
        self._create_right_panel()

        # Barra de estado
        self.status = self.statusBar()
        self.status.showMessage("Listo")

        # Menú
        self._create_menu()

    # ----------------- Menú superior -----------------
    def _create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&Archivo")
        view_menu = menubar.addMenu("&Vista")
        config_menu = menubar.addMenu("&Configuración")

        # Archivo
        new_action = QAction("Nuevo mapa", self)
        new_action.triggered.connect(self.action_new_map)
        open_action = QAction("Abrir...", self)
        open_action.triggered.connect(self.action_open)
        save_action = QAction("Guardar...", self)
        save_action.triggered.connect(self.action_save)
        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(self.close)

        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # Vista
        zoom_in = QAction("Zoom in", self)
        zoom_in.triggered.connect(self.map_view.zoom_in)
        zoom_out = QAction("Zoom out", self)
        zoom_out.triggered.connect(self.map_view.zoom_out)
        reset_zoom = QAction("Reset zoom", self)
        reset_zoom.triggered.connect(self.map_view.reset_zoom)

        view_menu.addAction(zoom_in)
        view_menu.addAction(zoom_out)
        view_menu.addAction(reset_zoom)

        # Configuración
        prefs_action = QAction("Preferencias", self)
        prefs_action.triggered.connect(self.action_prefs)
        config_menu.addAction(prefs_action)

    # ----------------- Panel izquierdo -----------------
    def _create_left_palette(self):
        dock = QDockWidget("Paleta / Herramientas", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        widget = QWidget()
        layout = QVBoxLayout()

        self.palette_list = QListWidget()
        self.palette_list.addItems(["Tile: Suelo", "Tile: Agua", "Tile: Montaña"])
        self.preview_label = QLabel("Previsualización")
        self.preview_label.setFixedHeight(80)
        self.preview_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.palette_list)
        layout.addWidget(self.preview_label)
        widget.setLayout(layout)
        dock.setWidget(widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

    # ----------------- Panel derecho -----------------
    def _create_right_panel(self):
        dock = QDockWidget("Capas / Propiedades", self)
        dock.setAllowedAreas(Qt.RightDockWidgetArea)
        widget = QWidget()
        layout = QVBoxLayout()
        self.layers_list = QListWidget()
        self.layers_list.addItems(["Fondo", "Objetos"])
        layout.addWidget(QLabel("Capas:"))
        layout.addWidget(self.layers_list)
        widget.setLayout(layout)
        dock.setWidget(widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    # ----------------- Acciones del menú -----------------
    def action_new_map(self):
        dialog = NewMapDialog(self)
        if dialog.exec_() == dialog.Accepted:
            w, h, tile = dialog.get_values()
            self.map_view.create_new_map(w, h, tile)
            self.status.showMessage(f"Mapa nuevo {w}x{h}, tile={tile}px")

    def action_open(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Abrir mapa", "", "JSON Files (*.json);;All Files (*)")
        if fname:
            QMessageBox.information(self, "Abrir", f"Abrir: {fname}\n(Implementar carga en el módulo modelo)")

    def action_save(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Guardar mapa", "", "JSON Files (*.json);;All Files (*)")
        if fname:
            QMessageBox.information(self, "Guardar", f"Guardar: {fname}\n(Implementar guardado en el módulo exportación)")

    def action_prefs(self):
        QMessageBox.information(self, "Preferencias", "Aquí irán las preferencias (implementación futura).")
