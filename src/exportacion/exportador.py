import json
import os
from PIL import Image

VERSION_FORMATO = "1.0"

def guardar_mapa_json(mapa, ruta_archivo):
    try:
        if isinstance(mapa, dict):
            datos_mapa = mapa.copy()
            datos_mapa["version"]= VERSION_FORMATO

        else:
            datos_mapa = {
                "version": VERSION_FORMATO,
                "ancho": getattr(mapa, "ancho", 0),
                "alto": getattr(mapa, "alto", 0),
                "tiles": [],
                "obejetos": []  
            }

            for fila in getattr(mapa, "tiles",[]):
                fila_tiles = []
                for tile in fila:
                    fila_tiles.append({
                        "tipo":getattr(tile,"tipo", None), 
                        "colision":getattr(tile,"colision", None), 
                    })
                datos_mapa["tiles"].append(fila_tiles)

            for obj in getattr(mapa, "objetos",[]):
                datos_mapa["objetos"].append({
                    "tipo": getattr(obj, "posicion", [0,0])[0],
                    "posicion": {
                        "x": getattr(obj, "posicion", [0,0])[0],
                        "y": getattr(obj, "posicion", [0,0])[1],
                    },
                    "propiedades": getattr(obj, "propiedades", {})
                })

        os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
        with open(ruta_archivo, "w", encoding="utf-8") as archivo:
            json.dump(datos_mapa, archivo, indent=4, ensure_ascii=False)
            print(f"Mapa guardado en {ruta_archivo}")
    except Exception as e:
        print(f"Error al guardar el mapa: {e}")


# DESERIALIZACIÓN CON VALIDACION #

def cargar_mapa_json(ruta_archivo):
    
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
            data = json.load(archivo)

        if not validar_datos_mapa(data):
            raise ValueError("El formato del mapa es invalido o incompleta.")
        
        print(f"Mapa correctamente cargado desde {ruta_archivo}")
        return data
    except FileNotFoundError:
        print(f"Archivo no encontrado: {ruta_archivo}")
    except json.JSONDecodeError:
        print(f"Error: El archivo no tiene un formato JSON valido.")
    except Exception as e:
        print(f"Error al cargar el mapa: {e}")

    return None

# VALIDACION DE DATOS #

def validar_datos_mapa(data):
    claves_obligatorias = ["ancho", "alto", "version"]

    for clave in claves_obligatorias:
        if clave not in data:
            print(f"Falta la clave obligatoria: {clave}")
            return False
        
    if "tiles" in data and not isinstance(data["tiles"], list):
        print("La clave 'tiles' debe ser una lista.")
        return False
    if "objetos" in data and not isinstance(data["objetos"], list):
        print("La clave 'objetos' debe ser una lista.")
        return False
    return True

# exportacion para motor de juego #
def exportar_para_motor(mapa, ruta_exportacion):
    try:
        if isinstance(mapa, dict):
            data_motor = {
                "ancho": mapa.get("ancho", 0),
                "alto": mapa.get("alto", 0),
                "tiles": mapa.get("tiles", []),
                "colisiones": mapa.get("colisiones", []),
            }
        else:
            data_motor = {
                "ancho": getattr(mapa, "ancho", 0),
                "alto": getattr(mapa, "alto", 0),
                "tiles": getattr(mapa,"tiles",[]),
                "colisiones": getattr(mapa,"colisiones",[])
            }
        os.makedirs(os.path.dirname(ruta_exportacion), exist_ok=True)
        with open(ruta_exportacion, "w", encoding="utf-8") as archivo:
            json.dump(data_motor, archivo, indent=4, ensure_ascii=False)
            print(f"Mapa exportado correctamente en {ruta_exportacion}")
    except Exception as e:
        print(f"Error al exportar el mapa: {e}")

# BONO #    
def exportar_png_mapa(mapa, ruta_exportacion, ruta_tiles):
    try:
        ancho = mapa.get("ancho",0)
        alto = mapa.get("alto",0)
        tiles = mapa.get("capas",[])[0] if "capas" in mapa else mapa.get("tiles",[])
        tile_size = 32
        imagen_final = Image.new("RGBA", (ancho * tile_size, alto * tile_size))

        for y, fila in enumerate(tiles):
            for x, id_tile in enumerate(fila):
                try:
                    ruta_tile = os.path.join(ruta_tiles,f"{id_tile}.png")
                    tile_img = Image.open(ruta_tile).convert("RGBA")
                    imagen_final.paste(tile_img, (x * tile_size, y * tile_size), tile_img)
                except FileNotFoundError:
                    continue
        os.makedirs(os.path.dirname(ruta_exportacion), exist_ok=True)
        imagen_final.save(ruta_exportacion)
        print(f"Mapa exportado como PNG en {ruta_exportacion}")     
    except Exception as e:
        print(f"Error al exportar el mapa como PNG: {e}")



        