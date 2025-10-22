import json
import os
from datetime import datetime
from PIL import Image, ImageDraw

from modelo.mapa import Mapa, Tile
from modelo.objetos import Objeto


VERSION_FORMATO = "1.0"


class GestorArchivos:
    
    def __init__(self):
        self.ruta_maps = "maps/"
        self.ruta_exports = "exports/"
        self._crear_directorios()
    
    def _crear_directorios(self):
        os.makedirs(self.ruta_maps, exist_ok=True)
        os.makedirs(self.ruta_exports, exist_ok=True)
    
    def guardar_mapa(self, mapa, nombre_archivo):
        try:
            datos = {
                'version': VERSION_FORMATO,
                'metadata': {
                    'nombre': nombre_archivo,
                    'fecha_creacion': datetime.now().isoformat(),
                    'ancho': mapa.ancho,
                    'alto': mapa.alto,
                    'tamano_tile': mapa.tamano_tile
                },
                'capas': {},
                'spawn_points': mapa.spawn_points
            }
            
            for nombre_capa, matriz in mapa.capas.items():
                if nombre_capa == 'colision':
                    datos['capas'][nombre_capa] = matriz
                else:
                    # Serializar tiles
                    capa_serializada = []
                    for fila in matriz:
                        fila_data = []
                        for tile in fila:
                            if tile is None:
                                fila_data.append(None)
                            else:
                                fila_data.append(tile.to_dict())
                        capa_serializada.append(fila_data)
                    datos['capas'][nombre_capa] = capa_serializada
            
            # Guardar archivo
            ruta_completa = os.path.join(self.ruta_maps, f"{nombre_archivo}.json")
            with open(ruta_completa, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
            
            return True, f"✅ Mapa guardado en {ruta_completa}"
            
        except Exception as e:
            return False, f"❌ Error al guardar: {str(e)}"
    
    def cargar_mapa(self, nombre_archivo):
        try:
            # Quitar extensión si la tiene
            if nombre_archivo.endswith('.json'):
                nombre_archivo = nombre_archivo[:-5]
            
            ruta_completa = os.path.join(self.ruta_maps, f"{nombre_archivo}.json")
            
            if not os.path.exists(ruta_completa):
                return False, None, f"❌ Archivo no encontrado: {ruta_completa}"
            
            with open(ruta_completa, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            # Validar
            if not self._validar_estructura(datos):
                return False, None, "❌ Estructura de JSON inválida"
            
            # Reconstruir mapa
            metadata = datos['metadata']
            mapa = Mapa(metadata['ancho'], metadata['alto'], metadata['tamano_tile'])
            
            # Reconstruir capas
            for nombre_capa, contenido in datos['capas'].items():
                if nombre_capa == 'colision':
                    mapa.capas[nombre_capa] = contenido
                else:
                    for y, fila in enumerate(contenido):
                        for x, tile_data in enumerate(fila):
                            if tile_data:
                                tile = Tile.from_dict(tile_data)
                                mapa.capas[nombre_capa][y][x] = tile
            
            mapa.spawn_points = datos.get('spawn_points', [])
            
            return True, mapa, "✅ Mapa cargado correctamente"
            
        except json.JSONDecodeError:
            return False, None, "❌ Archivo JSON corrupto"
        except Exception as e:
            return False, None, f"❌ Error: {str(e)}"
    
    def _validar_estructura(self, datos):
        if 'version' not in datos:
            return False
        if 'metadata' not in datos:
            return False
        if 'capas' not in datos:
            return False
        
        metadata = datos['metadata']
        if 'ancho' not in metadata or 'alto' not in metadata:
            return False
        
        return True
    
    def exportar_para_motor(self, mapa, nombre_archivo):
        try:
            export_data = {
                'width': mapa.ancho,
                'height': mapa.alto,
                'tileSize': mapa.tamano_tile,
                'layers': {
                    'background': self._comprimir_capa(mapa.capas['fondo']),
                    'objects': self._comprimir_capa(mapa.capas['objetos']),
                    'collision': self._comprimir_colisiones(mapa.capas['colision'])
                },
                'spawns': mapa.spawn_points
            }
            
            ruta = os.path.join(self.ruta_exports, f"{nombre_archivo}_game.json")
            with open(ruta, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, separators=(',', ':'))
            
            return True, f"✅ Exportado a {ruta}"
            
        except Exception as e:
            return False, f"❌ Error: {str(e)}"
    
    def _comprimir_capa(self, matriz):
        return [[tile.tipo if tile else None for tile in fila] for fila in matriz]
    
    def _comprimir_colisiones(self, matriz):
        colisiones = []
        for y, fila in enumerate(matriz):
            for x, tiene_colision in enumerate(fila):
                if tiene_colision:
                    colisiones.append([x, y])
        return colisiones
    
    def exportar_png(self, mapa, nombre_archivo):
        #BONO, Exportar el mapa como imagen PNG
        try:
            ancho_img = mapa.ancho * mapa.tamano_tile
            alto_img = mapa.alto * mapa.tamano_tile
            
            img = Image.new('RGB', (ancho_img, alto_img), color='white')
            draw = ImageDraw.Draw(img)
            
            for nombre_capa in ['fondo', 'objetos']:
                for y in range(mapa.alto):
                    for x in range(mapa.ancho):
                        tile = mapa.obtener_tile(x, y, nombre_capa)
                        if tile:
                            x1 = x * mapa.tamano_tile
                            y1 = y * mapa.tamano_tile
                            x2 = x1 + mapa.tamano_tile
                            y2 = y1 + mapa.tamano_tile
                            
                            color = tile.color.lstrip('#')
                            rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
                            
                            draw.rectangle([x1, y1, x2, y2], fill=rgb)
            
            for y in range(mapa.alto):
                for x in range(mapa.ancho):
                    if mapa.capas['colision'][y][x]:
                        x1 = x * mapa.tamano_tile
                        y1 = y * mapa.tamano_tile
                        x2 = x1 + mapa.tamano_tile
                        y2 = y1 + mapa.tamano_tile

                        draw.line([x1, y1, x2, y2], fill=(255, 0, 0), width=2)
                        draw.line([x2, y1, x1, y2], fill=(255, 0, 0), width=2)
            
            for x in range(0, ancho_img, mapa.tamano_tile):
                draw.line([(x, 0), (x, alto_img)], fill=(200, 200, 200), width=1)
            for y in range(0, alto_img, mapa.tamano_tile):
                draw.line([(0, y), (ancho_img, y)], fill=(200, 200, 200), width=1)
            
            ruta = os.path.join(self.ruta_exports, f"{nombre_archivo}.png")
            img.save(ruta, 'PNG')
            
            return True, f"✅ PNG exportado a {ruta}"
            
        except Exception as e:
            return False, f"❌ Error: {str(e)}"


def guardar_mapa_json(datos_mapa, ruta_archivo):
    try:
        os.makedirs(os.path.dirname(ruta_archivo) if os.path.dirname(ruta_archivo) else ".", exist_ok=True)
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            json.dump(datos_mapa, f, indent=2, ensure_ascii=False)
        print(f"✅ Mapa guardado en {ruta_archivo}")
        return True
    except Exception as e:
        print(f"❌ Error al guardar: {e}")
        return False


def cargar_mapa_json(ruta_archivo):
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        print(f"✅ Mapa cargado desde {ruta_archivo}")
        return datos
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {ruta_archivo}")
        return None
    except json.JSONDecodeError:
        print(f"❌ Archivo JSON corrupto: {ruta_archivo}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def exportar_para_motor(datos_mapa, ruta_exportacion):
    try:
        os.makedirs(os.path.dirname(ruta_exportacion) if os.path.dirname(ruta_exportacion) else ".", exist_ok=True)
        
        # Formato simplificado para el motor
        export_data = {
            'width': datos_mapa.get('ancho', 0),
            'height': datos_mapa.get('alto', 0),
            'tiles': datos_mapa.get('tiles', []),
            'collisions': datos_mapa.get('colisiones', [])
        }
        
        with open(ruta_exportacion, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, separators=(',', ':'))
        
        print(f"✅ Exportado para motor en {ruta_exportacion}")
        return True
    except Exception as e:
        print(f"❌ Error al exportar: {e}")
        return False


# TEST
if __name__ == '__main__':
    print("✅ Módulo de exportación cargado correctamente")
    gestor = GestorArchivos()
    print(f"Rutas: maps={gestor.ruta_maps}, exports={gestor.ruta_exports}")