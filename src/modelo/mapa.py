import copy
import os
from typing import Optional, Dict, List, Tuple, Any

class Tile:
    #Esta clase represnyta un tile individual del mapa, el tile o puede ser imagen es decir sprite o un color solido
    def __init__(
            self,
            tipo: str,
            color: Optional[str] = None,
            sprite: Optional[str] = None,
            tiene_colision: bool = False,
            animado: bool = False
    ):
        self.tipo = tipo
        self.sprite = sprite
        self.color = color if color is not None else self._obtener_color_default()
        self.tiene_colision = tiene_colision
        self.animado = animado

        #animaciones peroo todavia nooo
        self.frames = []
        self.frame_actual = 0
        self.tiempo_por_frame = 200
        self.ultimo_cambio = 0

        self.propiedades = {}
    
    def _obtener_color_default(self) -> str:
        colores = {
            'vacio': '#FFFFFF',
            'pasto': '#7CFC00',
            'pasto_oscuro': '#228B22',
            'tierra': '#8B4513',
            'agua': '#1E90FF',
            'agua_profunda': '#000080',
            'piedra': '#696969',
            'roca': '#808080',
            'arena': '#F4A460',
            'nieve': '#FFFAFA',
            'hielo': '#B0E0E6',
            'lava': '#FF4500',
            'camino': '#D2B48C',
            'madera': '#DEB887',
            'metal': '#C0C0C0',
            'pared': '#A9A9A9',
        }
        return colores.get(self.tipo, '#FFFFFF')
    
    def tiene_sprite(self) -> bool:
        #aqui se verifica si el tile tiene algun sprite valido y devuelve verdadero si es lo tiene y el archivo existe
        return self.sprite is not None and os.path.exists(self.sprite)
    
    def obtener_sprite_path(self) -> Optional[str]:
        #busca la ruta del sprite si es q existe
        if self.tiene_sprite():
            return self.sprite
        return None
    
    def establecer_sprite(self, ruta: str) -> bool:
        #establece el sprite del tile
        if os.path.exists(ruta):
            self.sprite = ruta
            return True
        return False
    
    def establecer_propiedad(self, clave: str, valor: Any) -> None:
        #estabalce una propiedad personalizada
        self.propiedades[clave] = valor

    def obtener_propiedad(self, clave: str, default: Any = None) -> Any:
        #obtiene una propiedad personalizada
        return self.propiedades.get(clave, default)
    
    def to_dict(self) -> Dict[str, Any]:
        #serializa el tile a un dicc y devuelve el dicc con los datos del tile
        return {
            'tipo': self.tipo,
            'color': self.color,
            'sprite': self.sprite,
            'colision': self.tiene_colision,
            'animado': self.animado,
            'frames': self.frames,
            'propiedades': self.propiedades
        }
    @classmethod
    def from_dict(cls, datos: Dict[str, Any]) -> 'Tile':
        #la opcion  fue crear un tile desde un diccionario
        tile = cls(
            tipo=datos['tipo'],
            color=datos.get('color'),
            sprite=datos.get('sprite'),
            tiene_colision=datos.get('colision', False),
            animado=datos.get('animado', False)
        )
        tile.frames = datos.get('frames', [])
        tile.propiedades = datos.get('propiedades', {})
        return tile
    
    def clonar(self) -> 'Tile':
        #crea una copia del tile
        tile_nuevo = Tile(
            tipo=self.tipo,
            color=self.color,
            sprite=self.sprite,
            tiene_colision=self.tiene_colision,
            animado=self.animado
        )
        tile_nuevo = Tile(
            tipo=self.tipo,
            color=self.color,
            sprite=self.sprite,
            tiene_colision=self.tiene_colision,
            animado=self.animado
        )
        tile_nuevo.frames = self.frames.copy()
        tile_nuevo.propiedades = copy.deepcopy(self.propiedades)
        return tile_nuevo
    
    def __repr__(self) -> str:
        sprite_str = "🖼️" if self.tiene_sprite() else "🎨"
        colision_str = "🚫" if self.tiene_colision else "✅"
        return f"Tile({self.tipo} {sprite_str} {colision_str})"

    def __eq__(self, otro: object) -> bool:
        if not isinstance(otro, Tile):
            return False
        return (
            self.tipo == otro.tipo and
            self.color == otro.color and
            self.tiene_colision == otro.tiene_colision
        )
    

class Mapa:
    #Representa el mapa completo del editor, aqui voy a a hacer uso de una matriz bidimensional ya q como el mapa esta coompuesto por multiples capas, cada una se implementa como una matriz
    def __init__(self, ancho: int, alto: int, tamaño_tile: int = 32):
        #inicializar un nuevo mapa
        if ancho <= 0 or alto <= 0:
            raise ValueError(f"Dimensiones inválidas: {ancho}x{alto}")
        if tamaño_tile <= 0:
            raise ValueError(f"Tamaño de tile inválido: {tamaño_tile}")
        
        self.ancho = ancho
        self.alto = alto
        self.tamaño_tile = tamaño_tile

        #creacion de capas del mapa
        self.capas = {
            'fondo': [[None for _ in range(ancho)] for _ in range(alto)],
            'decoracion': [[None for _ in range(ancho)] for _ in range(alto)],
            'objetos': [[None for _ in range(ancho)] for _ in range(alto)],
            'colision': [[False for _ in range(ancho)] for _ in range(alto)]
        }

        self.capa_activa = 'fondo'
        self.spawn_points = []
        
        #metadata del mapa
        self.metadata = {
            'nombre': 'Sin nombre',
            'autor': '',
            'version': '1.0',
            'descripcion': '',
            'ruta_assets': 'assets/'
        }

    def colocar_tile(
            self,
            x: int,
            y: int,
            tile: Optional[Tile],
            capa: Optional[str] = None
    ) -> None:
        #coloca el tile en la posicion q se quiera
        if not self._validar_coordenadas(x, y):
            raise ValueError(f"Coordenadas fuera del mapa: ({x}, {y})")
        
        capa = capa or self.capa_activa
        
        if capa not in self.capas:
            raise ValueError(f"Capa inválida: {capa}")
        
        if capa == 'colision':
            self.capas[capa][y][x] = bool(tile) if tile is not None else False
        else:
            self.capas[capa][y][x] = tile
    
    def obtener_tile(self, x: int, y: int, capa: str) -> Optional[Tile]:
        #obtiene el tile en la pos especificada
        if not self._validar_coordenadas(x, y):
            return None
        
        if capa not in self.capas:
            return None
        
        return self.capas[capa][y][x]
    
    def _validar_coordenadas(self, x: int, y: int) -> bool:
        #verificacion si las coordenadas estan dentro del mapa
        return 0 <= x <= self.ancho and 0 <= y <= self.alto
    
    def agregar_spawn_point(
        self, 
        x: int, 
        y: int, 
        tipo: str = 'jugador',
        nombre: Optional[str] = None
    ) -> bool:
        if not self._validar_coordenadas(x, y):
            return False
        
        spawn = {
            'x': x,
            'y': y,
            'tipo': tipo,
            'nombre': nombre or f"{tipo}_{len(self.spawn_points)}"
        }

        self.spawn_points.append(spawn)
        return True

    def eliminar_spawn_point(self, x: int, y: int) -> bool:
        #elimina spawn point de acuerdo a las coordenadas dadas
        inicial = len(self.spawn_points) 
        self.spawn_points = [
            sp for sp in self.spawn_points
            if not (sp['x'] == x and sp['y'] == y)
        ]
        return len(self.spawn_points) < inicial
    
    def limpiar_capa(self, nombre_capa: str) -> bool:
        #limpia toda una capa completa
        if nombre_capa not in self.capas:
            return False
        
        if nombre_capa == 'colision':
            self.capas[nombre_capa] = [
                [False for _ in range(self.ancho)]
                for _ in range(self.alto)
            ]
        else:
            self.capas[nombre_capa] = [
                [None for _ in range(self.ancho)]
                for _ in range(self.alto)
            ]
        return True
    
    def cambiar_capa_activa(self, nombre_capa: str) -> bool:
        #aca se cambia la capa activa del mapa
        if nombre_capa not in self.capas:
            return False
        self.capa_activa = nombre_capa
        return True
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        #adicional .
        stats = {
            'dimensiones': f"{self.ancho}x{self.alto}",
            'tiles_totales': self.ancho * self.alto,
            'tamaño_tile': self.tamaño_tile,
            'spawn_points': len(self.spawn_points),
            'capas': len(self.capas)
        }

        #conteo de tiles por capa
        for nombre_capa, matriz in self.capas.items():
            if nombre_capa == 'colision':
                count = sum(1 for fila in matriz for col in fila if col)
                stats['tiles_colision'] = count
            else:
                count = sum(1 for fila in matriz for tile in fila if tile is not None)
                stats[f'tiles_{nombre_capa}'] = count
        return stats
    
    def clonar(self) -> 'Mapa':
        #copia mapa
        nuevo_mapa = Mapa(self.ancho, self.alto, self.tamaño_tile)
        nuevo_mapa.capas = copy.deepcopy(self.capas)
        nuevo_mapa.spawn_points = copy.deepcopy(self.spawn_points)
        nuevo_mapa.metadata = self.metadata.copy()
        nuevo_mapa.capa_activa = self.capa_activa
        return nuevo_mapa
    
    def __repr__(self) -> str:
        return f"Mapa '{self.metadata['nombre']}': {self.ancho}x{self.alto}"
    
    def __str__(self) -> str:
        return f"Mapa '{self.metadata['nombre']}': {self.ancho}x{self.alto}"
    
#CONFIGURACION DE TILES

TILES_CONFIG = {
    'pasto': {
        'nombre': 'Pasto',
        'sprite': 'assets/tiles/grass.png',
        'color': '#7CFC00',
        'colision': False,
        'descripcion': 'Pasto verde básico'
    },
    'tierra': {
        'nombre': 'Tierra',
        'sprite': 'assets/tiles/dirt.png',
        'color': '#8B4513',
        'colision': False,
        'descripcion': 'Tierra marrón'
    },
    'agua': {
        'nombre': 'Agua',
        'sprite': 'assets/tiles/water.png',
        'color': '#1E90FF',
        'colision': True,
        'descripcion': 'Agua azul (bloq uea paso)'
    },
    'piedra': {
        'nombre': 'Piedra',
        'sprite': 'assets/tiles/stone.png',
        'color': '#696969',
        'colision': True,
        'descripcion': 'Piedra gris sólida'
    },
    'arena': {
        'nombre': 'Arena',
        'sprite': 'assets/tiles/sand.png',
        'color': '#F4A460',
        'colision': False,
        'descripcion': 'Arena de playa'
    },
    'nieve': {
        'nombre': 'Nieve',
        'sprite': 'assets/tiles/snow.png',
        'color': '#FFFAFA',
        'colision': False,
        'descripcion': 'Nieve blanca'
    },
    'lava': {
        'nombre': 'Lava',
        'sprite': 'assets/tiles/lava.png',
        'color': '#FF4500',
        'colision': True,
        'descripcion': 'Lava ardiente (daña)'
    },
    'camino': {
        'nombre': 'Camino',
        'sprite': 'assets/tiles/path.png',
        'color': '#D2B48C',
        'colision': False,
        'descripcion': 'Camino de tierra'
    },
}

def crear_tile_desde_config(tipo: str) -> Tile:
    #crear un tile desde la config predefinida
    if tipo not in TILES_CONFIG:
        return Tile(tipo)
    
    config = TILES_CONFIG[tipo]

    #se verififca si el sprite existe
    sprite_path = config['sprite']
    if not os.path.exists(sprite_path):
        sprite_path = None
    
    return Tile(
        tipo=tipo
        color=config['color'],
        sprite=sprite_path,
        tiene_colision=config.get('colision', False)
    )