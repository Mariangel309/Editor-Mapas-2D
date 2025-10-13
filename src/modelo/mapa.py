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
