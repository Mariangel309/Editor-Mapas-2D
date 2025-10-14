import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.exportacion.exportador import guardar_mapa_json, cargar_mapa_json

mapa_prueba = {
    "ancho": 5,
    "alto": 5,
    "tiles": [
        [0, 1, 2, 1, 0],
        [1, 0, 0, 2, 2],
        [2, 1, 1, 0, 0],
        [0, 0, 2, 1, 1],
        [1, 2, 0, 0, 2]
    ],
    "colisiones": [
        [0, 0, 1, 0, 0],
        [0, 1, 1, 0, 0],
        [1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1],
        [0, 0, 0, 0, 0]
    ]
}

guardar_mapa_json(mapa_prueba, "maps/ejemplo1.json")

mapa_cargado = cargar_mapa_json("maps/ejemplo1.json")

print("\n📋 Resultado del mapa cargado:")
print(mapa_cargado)
