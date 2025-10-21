from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, 
    QSpinBox, QDialogButtonBox, QLabel
)
class NewMapDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo mapa")
        self.setModal(True)
        self.resize(300, 200)

        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 200)
        self.width_spin.setValue(20)

        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 200)
        self.height_spin.setValue(15)

        self.tile_spin = QSpinBox()
        self.tile_spin.setRange(16, 128)
        self.tile_spin.setValue(32)

        form = QFormLayout()
        form.addRow("Ancho (tiles):", self.width_spin)
        form.addRow("Alto (tiles):", self.height_spin)
        form.addRow("Tamaño tile (px):", self.tile_spin)
        
        info = QLabel(
            "<small><i>Recomendado: 20x15 con tiles de 32px</i></small>"
        )
        form.addRow("", info)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_values(self):
        return (
            self.width_spin.value(), 
            self.height_spin.value(), 
            self.tile_spin.value()
        )