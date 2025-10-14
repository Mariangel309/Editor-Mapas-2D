from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QSpinBox, QDialogButtonBox

class NewMapDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo mapa")
        self.setModal(True)

        # Campos de entrada
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 500)
        self.width_spin.setValue(20)

        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 500)
        self.height_spin.setValue(15)

        self.tile_spin = QSpinBox()
        self.tile_spin.setRange(8, 256)
        self.tile_spin.setValue(32)

        # Diseño del formulario
        form = QFormLayout()
        form.addRow("Ancho (tiles):", self.width_spin)
        form.addRow("Alto (tiles):", self.height_spin)
        form.addRow("Tamaño tile (px):", self.tile_spin)

        # Botones Aceptar / Cancelar
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_values(self):
        """Devuelve los valores elegidos por el usuario."""
        return self.width_spin.value(), self.height_spin.value(), self.tile_spin.value()
