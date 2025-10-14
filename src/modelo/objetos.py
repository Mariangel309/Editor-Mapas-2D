#OBJETOS DECORATIVOS E INTERACTIVOS DEL MAPA
class Objeto:
    def __init__(self, nombre, x, y, tipo='decorativo'):
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

        #interactivos:
        self.interactivo = False
        self.dialogo = None
        self.items = []

        self.visible = True
        self.rotacion = 0

    def _obtener_color_por_tipo(self):
        colores_tipo = {
            'decorativo': '#8B4513',    # Marrón
            'arbol': '#006400',          # Verde oscuro
            'roca': '#808080',           # Gris
            'edificio': '#8B4513',       # Marrón
            'casa': '#D2691E'
            
        }