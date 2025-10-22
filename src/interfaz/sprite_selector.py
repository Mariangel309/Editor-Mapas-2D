"""
Widget para seleccionar sprites de tiles.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFileDialog, QScrollArea, QGridLayout,
                             QFrame, QButtonGroup, QRadioButton)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon
import os


class SpriteButton(QPushButton):
    """Botón que muestra un sprite."""
    
    def __init__(self, sprite_path, nombre, parent=None):
        super().__init__(parent)
        self.sprite_path = sprite_path
        self.nombre = nombre
        
        self.setFixedSize(64, 64)
        self.setCheckable(True)
        self.setToolTip(nombre)
        
        if os.path.exists(sprite_path):
            icon = QIcon(sprite_path)
            self.setIcon(icon)
            self.setIconSize(self.size() - self.size()/4)
        else:
            self.setText("?")
        
        self.setStyleSheet("""
            QPushButton {
                border: 2px solid #ccc;
                border-radius: 4px;
                background: white;
            }
            QPushButton:hover {
                border: 2px solid #9650FF;
            }
            QPushButton:checked {
                border: 3px solid #9650FF;
                background: #E6D2FF;
            }
        """)


class SpritePaletteWidget(QWidget):
    """Widget de paleta de sprites."""
    
    sprite_selected = pyqtSignal(str, str)  # sprite_path, nombre
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sprite_buttons = []
        self.button_group = QButtonGroup()
        self.button_group.setExclusive(True)
        
        self.init_ui()
        self.cargar_sprites_disponibles()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Título
        titulo = QLabel("<b>Galería de Sprites:</b>")
        layout.addWidget(titulo)
        
        # Botón para modo color vs sprite
        btn_layout = QHBoxLayout()
        
        self.radio_color = QRadioButton("Usar Color")
        self.radio_sprite = QRadioButton("Usar Sprite")
        self.radio_color.setChecked(True)
        
        btn_layout.addWidget(self.radio_color)
        btn_layout.addWidget(self.radio_sprite)
        layout.addLayout(btn_layout)
        
        # Área scrolleable para sprites
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(300)
        
        # Widget contenedor de sprites
        self.sprite_container = QWidget()
        self.sprite_grid = QGridLayout(self.sprite_container)
        self.sprite_grid.setSpacing(5)
        
        scroll.setWidget(self.sprite_container)
        layout.addWidget(scroll)
        
        # Botón para cargar sprite personalizado
        btn_custom = QPushButton("📁 Cargar sprite personalizado...")
        btn_custom.clicked.connect(self.cargar_sprite_personalizado)
        layout.addWidget(btn_custom)
        
        # Preview del sprite seleccionado
        preview_frame = QFrame()
        preview_frame.setFrameStyle(QFrame.Box)
        preview_layout = QVBoxLayout(preview_frame)
        
        self.preview_label = QLabel("Sprite seleccionado:")
        self.preview_image = QLabel()
        self.preview_image.setFixedSize(80, 80)
        self.preview_image.setAlignment(Qt.AlignCenter)
        self.preview_image.setStyleSheet("border: 1px solid #ccc; background: white;")
        
        preview_layout.addWidget(self.preview_label)
        preview_layout.addWidget(self.preview_image)
        layout.addWidget(preview_frame)
        
        layout.addStretch()
    
    def cargar_sprites_disponibles(self):
        """Carga todos los sprites de la carpeta assets/tiles/"""
        ruta_base = "assets/tiles/"
        
        if not os.path.exists(ruta_base):
            os.makedirs(ruta_base, exist_ok=True)
            return
        
        # Limpiar grid
        for i in reversed(range(self.sprite_grid.count())): 
            self.sprite_grid.itemAt(i).widget().setParent(None)
        
        self.sprite_buttons.clear()
        
        # Cargar sprites
        sprites = []
        for archivo in os.listdir(ruta_base):
            if archivo.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                ruta_completa = os.path.join(ruta_base, archivo)
                nombre = os.path.splitext(archivo)[0]
                sprites.append((ruta_completa, nombre))
        
        # Agregar al grid
        row, col = 0, 0
        for sprite_path, nombre in sorted(sprites):
            btn = SpriteButton(sprite_path, nombre)
            btn.clicked.connect(lambda checked, p=sprite_path, n=nombre: 
                              self.on_sprite_selected(p, n))
            
            self.button_group.addButton(btn)
            self.sprite_grid.addWidget(btn, row, col)
            self.sprite_buttons.append(btn)
            
            col += 1
            if col >= 4:  # 4 columnas
                col = 0
                row += 1
        
        if not sprites:
            label = QLabel("No hay sprites disponibles.\nColoca archivos .png en assets/tiles/")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("color: gray; padding: 20px;")
            self.sprite_grid.addWidget(label, 0, 0, 1, 4)
    
    def cargar_sprite_personalizado(self):
        """Permite al usuario cargar un sprite desde su PC."""
        archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar sprite",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.gif);;Todos los archivos (*)"
        )
        
        if archivo:
            # Copiar a la carpeta assets
            import shutil
            nombre_archivo = os.path.basename(archivo)
            destino = os.path.join("assets/tiles/", nombre_archivo)
            
            os.makedirs("assets/tiles/", exist_ok=True)
            shutil.copy(archivo, destino)
            
            # Recargar galería
            self.cargar_sprites_disponibles()
            
            # Seleccionar el nuevo sprite
            self.on_sprite_selected(destino, os.path.splitext(nombre_archivo)[0])
    
    def on_sprite_selected(self, sprite_path, nombre):
        """Cuando se selecciona un sprite."""
        self.radio_sprite.setChecked(True)
        
        # Actualizar preview
        if os.path.exists(sprite_path):
            pixmap = QPixmap(sprite_path)
            pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_image.setPixmap(pixmap)
            self.preview_label.setText(f"<b>{nombre}</b>")
        
        # Emitir señal
        self.sprite_selected.emit(sprite_path, nombre)
    
    def usar_color(self):
        """Verifica si se debe usar color en lugar de sprite."""
        return self.radio_color.isChecked()
    
    def obtener_sprite_seleccionado(self):
        """Retorna el sprite actualmente seleccionado."""
        for btn in self.sprite_buttons:
            if btn.isChecked():
                return btn.sprite_path
        return None