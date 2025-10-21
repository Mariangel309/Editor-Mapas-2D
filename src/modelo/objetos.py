#OBJETOS DECORATIVOS E INTERACTIVOS DEL MAPA

import copy
import os
from typing import Optional, Dict, List, Any, Tuple  # ← AGREGAR Tuple aquí


class Objeto:

    def __init__(
        self, 
        nombre: str, 
        x: int, 
        y: int, 
        tipo: str = 'decorativo'
    ):
        
        self.nombre = nombre
        self.x = x
        self.y = y
        self.tipo = tipo
        
        self.sprite = None
        self.color = self._obtener_color_por_tipo()
        
        self.tiene_colision = True
        self.ancho = 1
        self.alto = 1
        
        self.propiedades = {}
        
        self.visible = True
        self.rotacion = 0
    
    def _obtener_color_por_tipo(self) -> str:
        colores = {
            'arbol': '#006400',
            'roca': '#808080',
            'casa': '#8B4513',
            'cofre': '#FFD700',
            'npc': '#FF6347',
            'enemigo': '#8B0000',
            'item': '#00CED1',
            'decorativo': '#8B4513',
        }
        return colores.get(self.tipo, '#FFFFFF')
    
    def tiene_sprite(self) -> bool:
        return self.sprite is not None and os.path.exists(self.sprite)
    
    def establecer_sprite(self, ruta: str) -> bool:
        if os.path.exists(ruta):
            self.sprite = ruta
            return True
        return False
    
    def mover(self, nueva_x: int, nueva_y: int) -> None:
        self.x = nueva_x
        self.y = nueva_y
    
    def mover_relativo(self, delta_x: int, delta_y: int) -> None:
        self.x += delta_x
        self.y += delta_y
    
    def establecer_propiedad(self, clave: str, valor: Any) -> None:
        self.propiedades[clave] = valor
    
    def obtener_propiedad(self, clave: str, default: Any = None) -> Any:
        return self.propiedades.get(clave, default)
    
    def cambiar_tamaño(self, ancho: int, alto: int) -> bool:
        if ancho > 0 and alto > 0:
            self.ancho = ancho
            self.alto = alto
            return True
        return False
    
    def obtener_area_ocupada(self) -> List[Tuple[int, int]]:
        area = []
        for dy in range(self.alto):
            for dx in range(self.ancho):
                area.append((self.x + dx, self.y + dy))
        return area
    
    def colisiona_con(self, x: int, y: int) -> bool:
        if not self.tiene_colision:
            return False
        
        return (
            self.x <= x < self.x + self.ancho and 
            self.y <= y < self.y + self.alto
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'nombre': self.nombre,
            'x': self.x,
            'y': self.y,
            'tipo': self.tipo,
            'sprite': self.sprite,
            'color': self.color,
            'colision': self.tiene_colision,
            'ancho': self.ancho,
            'alto': self.alto,
            'visible': self.visible,
            'rotacion': self.rotacion,
            'propiedades': self.propiedades
        }
    
    @classmethod
    def from_dict(cls, datos: Dict[str, Any]) -> 'Objeto':
        obj = cls(
            nombre=datos['nombre'],
            x=datos['x'],
            y=datos['y'],
            tipo=datos.get('tipo', 'decorativo')
        )
        
        obj.sprite = datos.get('sprite')
        obj.color = datos.get('color', obj.color)
        obj.tiene_colision = datos.get('colision', True)
        obj.ancho = datos.get('ancho', 1)
        obj.alto = datos.get('alto', 1)
        obj.visible = datos.get('visible', True)
        obj.rotacion = datos.get('rotacion', 0)
        obj.propiedades = datos.get('propiedades', {})
        
        return obj
    
    def clonar(self) -> 'Objeto':
        nuevo = Objeto(self.nombre, self.x, self.y, self.tipo)
        nuevo.sprite = self.sprite
        nuevo.color = self.color
        nuevo.tiene_colision = self.tiene_colision
        nuevo.ancho = self.ancho
        nuevo.alto = self.alto
        nuevo.visible = self.visible
        nuevo.rotacion = self.rotacion
        nuevo.propiedades = copy.deepcopy(self.propiedades)
        return nuevo
    
    def __repr__(self) -> str:
        sprite_str = "🖼️" if self.tiene_sprite() else "🎨"
        colision_str = "🚫" if self.tiene_colision else "✅"
        return f"Objeto({self.nombre} {sprite_str} {colision_str} en ({self.x},{self.y}))"
    
    def __str__(self) -> str:
        return f"{self.nombre} en ({self.x}, {self.y})"


OBJETOS_PREDEFINIDOS = {
    # Vegetación
    'arbol': {
        'nombre': 'Árbol',
        'tipo': 'arbol',
        'sprite': 'assets/objects/tree.png',
        'color': '#006400',
        'colision': True,
        'descripcion': 'Árbol frondoso'
    },
    'arbol_pino': {
        'nombre': 'Pino',
        'tipo': 'arbol',
        'sprite': 'assets/objects/pine.png',
        'color': '#2F4F4F',
        'colision': True,
        'descripcion': 'Árbol de pino'
    },
    'arbusto': {
        'nombre': 'Arbusto',
        'tipo': 'decorativo',
        'sprite': 'assets/objects/bush.png',
        'color': '#228B22',
        'colision': False,
        'descripcion': 'Arbusto pequeño'
    },
    
    # Rocas
    'roca': {
        'nombre': 'Roca',
        'tipo': 'roca',
        'sprite': 'assets/objects/rock.png',
        'color': '#808080',
        'colision': True,
        'descripcion': 'Roca común'
    },
    'roca_grande': {
        'nombre': 'Roca Grande',
        'tipo': 'roca',
        'sprite': 'assets/objects/rock_big.png',
        'color': '#696969',
        'colision': True,
        'ancho': 2,
        'alto': 2,
        'descripcion': 'Roca grande'
    },
    
    # Edificios
    'casa': {
        'nombre': 'Casa',
        'tipo': 'edificio',
        'sprite': 'assets/objects/house.png',
        'color': '#8B4513',
        'colision': True,
        'ancho': 3,
        'alto': 3,
        'descripcion': 'Casa pequeña'
    },
    'casa_grande': {
        'nombre': 'Casa Grande',
        'tipo': 'edificio',
        'sprite': 'assets/objects/house_big.png',
        'color': '#D2691E',
        'colision': True,
        'ancho': 4,
        'alto': 4,
        'descripcion': 'Casa grande'
    },
    'tienda': {
        'nombre': 'Tienda',
        'tipo': 'edificio',
        'sprite': 'assets/objects/shop.png',
        'color': '#DAA520',
        'colision': True,
        'ancho': 3,
        'alto': 2,
        'descripcion': 'Tienda comercial'
    },
    
    # Interactivos
    'cofre': {
        'nombre': 'Cofre',
        'tipo': 'interactivo',
        'sprite': 'assets/objects/chest.png',
        'color': '#FFD700',
        'colision': True,
        'descripcion': 'Cofre de tesoro'
    },
    'puerta': {
        'nombre': 'Puerta',
        'tipo': 'interactivo',
        'sprite': 'assets/objects/door.png',
        'color': '#8B4513',
        'colision': False,
        'descripcion': 'Puerta'
    },
    
    # NPCs
    'npc': {
        'nombre': 'NPC',
        'tipo': 'npc',
        'sprite': 'assets/objects/npc.png',
        'color': '#FF6347',
        'colision': True,
        'descripcion': 'Personaje no jugable'
    },
    'vendedor': {
        'nombre': 'Vendedor',
        'tipo': 'npc',
        'sprite': 'assets/objects/merchant.png',
        'color': '#FFA500',
        'colision': True,
        'descripcion': 'Vendedor'
    },
    
    # Enemigos
    'enemigo': {
        'nombre': 'Enemigo',
        'tipo': 'enemigo',
        'sprite': 'assets/objects/enemy.png',
        'color': '#8B0000',
        'colision': True,
        'descripcion': 'Enemigo genérico'
    },
}


def crear_objeto_desde_config(tipo: str, x: int, y: int) -> Objeto:
    if tipo not in OBJETOS_PREDEFINIDOS:
        return Objeto(tipo, x, y)
    
    config = OBJETOS_PREDEFINIDOS[tipo]
    obj = Objeto(config['nombre'], x, y, config['tipo'])
    
    sprite_path = config.get('sprite')
    if sprite_path and os.path.exists(sprite_path):
        obj.sprite = sprite_path
    
    obj.color = config['color']
    obj.tiene_colision = config.get('colision', True)
    obj.ancho = config.get('ancho', 1)
    obj.alto = config.get('alto', 1)
    
    return obj


def obtener_objetos_por_tipo(tipo: str) -> Dict[str, Dict]:
    return {
        clave: obj for clave, obj in OBJETOS_PREDEFINIDOS.items()
        if obj['tipo'] == tipo
    }


def obtener_tipos_disponibles() -> List[str]:
    tipos = set()
    for obj in OBJETOS_PREDEFINIDOS.values():
        tipos.add(obj['tipo'])
    return sorted(list(tipos))