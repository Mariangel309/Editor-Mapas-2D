# src/modelo/cargador_tiles.py
import os
from modelo.mapa import Tile

def cargar_tiles_desde_assets(carpeta="assets/tiles"):
    """
    Carga todos los tiles individuales desde la carpeta indicada.
    Cada imagen (ej: grass.png) se convierte en un Tile con su sprite asignado.
    """
    tiles = {}
    if not os.path.exists(carpeta):
        print(f"[ADVERTENCIA] Carpeta {carpeta} no existe.")
        return tiles

    for archivo in os.listdir(carpeta):
        if archivo.lower().endswith((".png", ".jpg", ".jpeg")):
            tipo = os.path.splitext(archivo)[0]
            ruta = os.path.join(carpeta, archivo)
            tile = Tile(tipo=tipo, sprite=ruta, tiene_colision=False)
            tiles[tipo] = tile

    print(f"[INFO] Tiles cargados desde {carpeta}: {len(tiles)}")
    return tiles
