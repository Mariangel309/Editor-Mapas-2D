import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modelo import (
    Mapa, Tile, Objeto,
    crear_tile_desde_config,
    crear_objeto_desde_config,
    TILES_CONFIG,
    OBJETOS_PREDEFINIDOS
)


class TestResultado:
    
    def __init__(self):
        self.pasados = 0
        self.fallados = 0
        self.errores = []
    
    def registrar_exito(self, nombre_test):
        self.pasados += 1
        print(f"  ✅ {nombre_test}")
    
    def registrar_fallo(self, nombre_test, error):
        self.fallados += 1
        self.errores.append((nombre_test, error))
        print(f"  ❌ {nombre_test}: {error}")
    
    def mostrar_resumen(self):
        total = self.pasados + self.fallados
        print("\n" + "=" * 60)
        print(f"RESUMEN DE TESTS")
        print("=" * 60)
        print(f"Total: {total}")
        print(f"✅ Pasados: {self.pasados}")
        print(f"❌ Fallados: {self.fallados}")
        
        if self.fallados > 0:
            print("\n🐛 Errores encontrados:")
            for nombre, error in self.errores:
                print(f"  - {nombre}: {error}")
        else:
            print("\n¡TODOS LOS TESTS PASARON!")
        
        print("=" * 60)
        return self.fallados == 0


resultado = TestResultado()


def test_crear_tile():
    try:
        tile = Tile('pasto', color='#7CFC00')
        assert tile.tipo == 'pasto'
        assert tile.color == '#7CFC00'
        assert tile.tiene_colision == False
        resultado.registrar_exito("Crear tile básico")
    except Exception as e:
        resultado.registrar_fallo("Crear tile básico", str(e))


def test_tile_color_default():
    try:
        tile = Tile('agua')
        assert tile.color == '#1E90FF'
        resultado.registrar_exito("Color por defecto")
    except Exception as e:
        resultado.registrar_fallo("Color por defecto", str(e))


def test_tile_propiedades():
    try:
        tile = Tile('pasto')
        tile.establecer_propiedad('velocidad', 1.5)
        tile.establecer_propiedad('daño', 10)
        
        assert tile.obtener_propiedad('velocidad') == 1.5
        assert tile.obtener_propiedad('daño') == 10
        assert tile.obtener_propiedad('inexistente', 'default') == 'default'
        resultado.registrar_exito("Propiedades de tile")
    except Exception as e:
        resultado.registrar_fallo("Propiedades de tile", str(e))


def test_tile_serializacion():
    try:
        tile = Tile('piedra', color='#696969', tiene_colision=True)
        tile.establecer_propiedad('dureza', 100)
        
        tile_dict = tile.to_dict()
        
        tile_nuevo = Tile.from_dict(tile_dict)
        
        assert tile_nuevo.tipo == tile.tipo
        assert tile_nuevo.color == tile.color
        assert tile_nuevo.tiene_colision == tile.tiene_colision
        assert tile_nuevo.obtener_propiedad('dureza') == 100
        resultado.registrar_exito("Serialización de tile")
    except Exception as e:
        resultado.registrar_fallo("Serialización de tile", str(e))


def test_crear_mapa():
    try:
        mapa = Mapa(20, 15, 32)
        assert mapa.ancho == 20
        assert mapa.alto == 15
        assert mapa.tamano_tile == 32
        assert len(mapa.capas) == 4
        resultado.registrar_exito("Crear mapa")
    except Exception as e:
        resultado.registrar_fallo("Crear mapa", str(e))


def test_mapa_dimensiones_invalidas():
    try:
        try:
            mapa = Mapa(-5, 10)
            resultado.registrar_fallo("Dimensiones inválidas", "No lanzó ValueError")
        except ValueError:
            resultado.registrar_exito("Dimensiones inválidas")
    except Exception as e:
        resultado.registrar_fallo("Dimensiones inválidas", str(e))


def test_colocar_obtener_tile():
    try:
        mapa = Mapa(10, 10)
        tile = Tile('pasto')
        
        mapa.colocar_tile(5, 5, tile)
        tile_obtenido = mapa.obtener_tile(5, 5, 'fondo')
        
        assert tile_obtenido == tile
        resultado.registrar_exito("Colocar y obtener tile")
    except Exception as e:
        resultado.registrar_fallo("Colocar y obtener tile", str(e))


def test_validar_coordenadas():
    try:
        mapa = Mapa(10, 10)
        
        assert mapa._validar_coordenadas(5, 5) == True
        assert mapa._validar_coordenadas(0, 0) == True
        assert mapa._validar_coordenadas(9, 9) == True
        assert mapa._validar_coordenadas(10, 10) == False
        assert mapa._validar_coordenadas(-1, 5) == False
        assert mapa._validar_coordenadas(5, -1) == False
        resultado.registrar_exito("Validar coordenadas")
    except Exception as e:
        resultado.registrar_fallo("Validar coordenadas", str(e))


def test_colocar_fuera_mapa():
    try:
        mapa = Mapa(10, 10)
        tile = Tile('pasto')
        
        try:
            mapa.colocar_tile(50, 50, tile)
            resultado.registrar_fallo("Colocar fuera del mapa", "No lanzó ValueError")
        except ValueError:
            resultado.registrar_exito("Colocar fuera del mapa")
    except Exception as e:
        resultado.registrar_fallo("Colocar fuera del mapa", str(e))


def test_spawn_points():
    try:
        mapa = Mapa(10, 10)
        
        exito = mapa.agregar_spawn_point(5, 5, 'jugador', 'Inicio')
        assert exito == True
        assert len(mapa.spawn_points) == 1
        
        mapa.agregar_spawn_point(8, 8, 'enemigo', 'Spawn 1')
        assert len(mapa.spawn_points) == 2
        
        spawn = mapa.spawn_points[0]
        assert spawn['x'] == 5
        assert spawn['y'] == 5
        assert spawn['tipo'] == 'jugador'
        assert spawn['nombre'] == 'Inicio'
        
        eliminado = mapa.eliminar_spawn_point(5, 5)
        assert eliminado == True
        assert len(mapa.spawn_points) == 1
        
        resultado.registrar_exito("Spawn points")
    except Exception as e:
        resultado.registrar_fallo("Spawn points", str(e))


def test_limpiar_capa():
    try:
        mapa = Mapa(5, 5)
        
        for x in range(5):
            for y in range(5):
                mapa.colocar_tile(x, y, Tile('pasto'), 'fondo')
        
        assert mapa.obtener_tile(2, 2, 'fondo') is not None
        
        mapa.limpiar_capa('fondo')
        
        assert mapa.obtener_tile(2, 2, 'fondo') is None
        resultado.registrar_exito("Limpiar capa")
    except Exception as e:
        resultado.registrar_fallo("Limpiar capa", str(e))


def test_cambiar_capa_activa():
    try:
        mapa = Mapa(10, 10)
        
        assert mapa.capa_activa == 'fondo'
        
        exito = mapa.cambiar_capa_activa('objetos')
        assert exito == True
        assert mapa.capa_activa == 'objetos'
        
        exito = mapa.cambiar_capa_activa('capa_inexistente')
        assert exito == False
        resultado.registrar_exito("Cambiar capa activa")
    except Exception as e:
        resultado.registrar_fallo("Cambiar capa activa", str(e))


def test_estadisticas_mapa():
    try:
        mapa = Mapa(10, 10, 32)
        mapa.agregar_spawn_point(5, 5)
        mapa.agregar_spawn_point(8, 8)
        
        stats = mapa.obtener_estadisticas()
        
        assert stats['dimensiones'] == '10x10'
        assert stats['tiles_totales'] == 100
        assert stats['tamano_tile'] == 32
        assert stats['spawn_points'] == 2
        resultado.registrar_exito("Estadísticas del mapa")
    except Exception as e:
        resultado.registrar_fallo("Estadísticas del mapa", str(e))


def test_crear_objeto():
    try:
        obj = Objeto('Arbol', 10, 15, 'arbol')
        assert obj.nombre == 'Arbol'
        assert obj.x == 10
        assert obj.y == 15
        assert obj.tipo == 'arbol'
        assert obj.tiene_colision == True
        resultado.registrar_exito("Crear objeto")
    except Exception as e:
        resultado.registrar_fallo("Crear objeto", str(e))


def test_objeto_propiedades():
    try:
        obj = Objeto('Cofre', 5, 5, 'cofre')
        obj.establecer_propiedad('contenido', 'espada')
        obj.establecer_propiedad('abierto', False)
        
        assert obj.obtener_propiedad('contenido') == 'espada'
        assert obj.obtener_propiedad('abierto') == False
        resultado.registrar_exito("Propiedades de objeto")
    except Exception as e:
        resultado.registrar_fallo("Propiedades de objeto", str(e))


def test_objeto_movimiento():
    try:
        obj = Objeto('NPC', 5, 5, 'npc')
        
        obj.mover(10, 10)
        assert obj.x == 10 and obj.y == 10
        
        obj.mover_relativo(5, -3)
        assert obj.x == 15 and obj.y == 7
        resultado.registrar_exito("Movimiento de objeto")
    except Exception as e:
        resultado.registrar_fallo("Movimiento de objeto", str(e))


def test_objeto_area_ocupada():
    try:
        obj = Objeto('Casa', 5, 5, 'casa')
        obj.cambiar_tamaño(3, 3)
        
        area = obj.obtener_area_ocupada()
        assert len(area) == 9
        assert (5, 5) in area
        assert (7, 7) in area
        assert (8, 8) not in area
        resultado.registrar_exito("Área ocupada")
    except Exception as e:
        resultado.registrar_fallo("Área ocupada", str(e))


def test_objeto_colision():
    try:
        obj = Objeto('Roca', 10, 10, 'roca')
        obj.cambiar_tamaño(2, 2)
        
        assert obj.colisiona_con(10, 10) == True
        assert obj.colisiona_con(11, 11) == True
        assert obj.colisiona_con(12, 12) == False
        
        obj.tiene_colision = False
        assert obj.colisiona_con(10, 10) == False
        resultado.registrar_exito("Colisión de objeto")
    except Exception as e:
        resultado.registrar_fallo("Colisión de objeto", str(e))


def test_objeto_serializacion():
    try:
        obj = Objeto('Casa Grande', 5, 5, 'casa')
        obj.cambiar_tamaño(4, 4)
        obj.establecer_propiedad('habitantes', 3)
        
        obj_dict = obj.to_dict()
        
        obj_nuevo = Objeto.from_dict(obj_dict)
        
        assert obj_nuevo.nombre == obj.nombre
        assert obj_nuevo.x == obj.x
        assert obj_nuevo.y == obj.y
        assert obj_nuevo.ancho == 4
        assert obj_nuevo.alto == 4
        assert obj_nuevo.obtener_propiedad('habitantes') == 3
        resultado.registrar_exito("Serialización de objeto")
    except Exception as e:
        resultado.registrar_fallo("Serialización de objeto", str(e))


def test_crear_tile_desde_config():
    try:
        tile = crear_tile_desde_config('agua')
        assert tile.tipo == 'agua'
        assert tile.color == '#1E90FF'
        assert tile.tiene_colision == True
        resultado.registrar_exito("Tile desde config")
    except Exception as e:
        resultado.registrar_fallo("Tile desde config", str(e))


def test_crear_objeto_desde_config():
    try:
        obj = crear_objeto_desde_config('arbol', 10, 10)
        assert obj.nombre == 'Árbol'
        assert obj.tipo == 'arbol'
        assert obj.x == 10
        assert obj.y == 10
        resultado.registrar_exito("Objeto desde config")
    except Exception as e:
        resultado.registrar_fallo("Objeto desde config", str(e))


def test_tiles_config_completo():
    try:
        tiles_esperados = ['pasto', 'tierra', 'agua', 'piedra', 'arena', 'nieve', 'lava', 'camino']
        
        for tipo in tiles_esperados:
            assert tipo in TILES_CONFIG
            config = TILES_CONFIG[tipo]
            assert 'nombre' in config
            assert 'color' in config
            assert 'sprite' in config
        
        resultado.registrar_exito("TILES_CONFIG completo")
    except Exception as e:
        resultado.registrar_fallo("TILES_CONFIG completo", str(e))


def test_objetos_predefinidos_completo():
    try:
        objetos_esperados = ['arbol', 'roca', 'casa', 'cofre', 'npc']
        
        for tipo in objetos_esperados:
            assert tipo in OBJETOS_PREDEFINIDOS
            config = OBJETOS_PREDEFINIDOS[tipo]
            assert 'nombre' in config
            assert 'tipo' in config
            assert 'color' in config
        
        resultado.registrar_exito("OBJETOS_PREDEFINIDOS completo")
    except Exception as e:
        resultado.registrar_fallo("OBJETOS_PREDEFINIDOS completo", str(e))


def test_mapa_grande():
    try:
        mapa = Mapa(100, 100, 32)
        
        # Colocar tiles en las esquinas
        mapa.colocar_tile(0, 0, Tile('pasto'))
        mapa.colocar_tile(99, 99, Tile('agua'))
        
        # Verificar
        assert mapa.obtener_tile(0, 0, 'fondo') is not None
        assert mapa.obtener_tile(99, 99, 'fondo') is not None
        
        stats = mapa.obtener_estadisticas()
        assert stats['tiles_totales'] == 10000
        resultado.registrar_exito("Mapa grande (100x100)")
    except Exception as e:
        resultado.registrar_fallo("Mapa grande (100x100)", str(e))


def test_clonar_mapa():

    try:
        mapa = Mapa(5, 5, 32)
        mapa.colocar_tile(2, 2, Tile('pasto'))
        mapa.agregar_spawn_point(3, 3)
        
        mapa_clon = mapa.clonar()
        
        mapa_clon.colocar_tile(2, 2, Tile('agua'))
        
        tile_original = mapa.obtener_tile(2, 2, 'fondo')
        tile_clon = mapa_clon.obtener_tile(2, 2, 'fondo')
        
        assert tile_original.tipo == 'pasto'
        assert tile_clon.tipo == 'agua'
        resultado.registrar_exito("Clonar mapa")
    except Exception as e:
        resultado.registrar_fallo("Clonar mapa", str(e))


def test_clonar_objeto():
    try:
        obj = Objeto('Original', 5, 5, 'test')
        obj.establecer_propiedad('dato', 'valor')
        
        obj_clon = obj.clonar()
        obj_clon.mover(10, 10)
        
        assert obj.x == 5
        assert obj_clon.x == 10
        assert obj_clon.obtener_propiedad('dato') == 'valor'
        resultado.registrar_exito("Clonar objeto")
    except Exception as e:
        resultado.registrar_fallo("Clonar objeto", str(e))



def ejecutar_todos_los_tests():
    """Ejecuta todos los tests del módulo."""
    print("=" * 60)
    print("TESTS DEL MÓDULO MODELO")
    print("=" * 60)
    
    print("\n Tests de Tile:")
    test_crear_tile()
    test_tile_color_default()
    test_tile_propiedades()
    test_tile_serializacion()
    test_crear_tile_desde_config()
    
    print("\n Tests de Mapa:")
    test_crear_mapa()
    test_mapa_dimensiones_invalidas()
    test_colocar_obtener_tile()
    test_validar_coordenadas()
    test_colocar_fuera_mapa()
    test_spawn_points()
    test_limpiar_capa()
    test_cambiar_capa_activa()
    test_estadisticas_mapa()
    test_mapa_grande()
    test_clonar_mapa()
    
    print("\n Tests de Objeto:")
    test_crear_objeto()
    test_objeto_propiedades()
    test_objeto_movimiento()
    test_objeto_area_ocupada()
    test_objeto_colision()
    test_objeto_serializacion()
    test_crear_objeto_desde_config()
    test_clonar_objeto()
    
    print("\n Tests de Configuración:")
    test_tiles_config_completo()
    test_objetos_predefinidos_completo()
    
    exito = resultado.mostrar_resumen()
    return exito


if __name__ == '__main__':
    exito = ejecutar_todos_los_tests()
    sys.exit(0 if exito else 1)