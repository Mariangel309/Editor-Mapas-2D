import os
from pathlib import Path


def crear_estructura():
    carpetas = [
        'assets/tiles',
        'assets/objects',
        'maps',
        'exports',
        'docs',
        'tests'
    ]
    
    print("Creando estructura de carpetas...")
    for carpeta in carpetas:
        os.makedirs(carpeta, exist_ok=True)
        print(f"  ✅ {carpeta}")


def verificar_assets():
    tiles_requeridos = [
        'grass.png', 'dirt.png', 'water.png', 'stone.png',
        'sand.png', 'snow.png', 'lava.png', 'path.png'
    ]
    
    objetos_requeridos = [
        'tree.png', 'rock.png', 'house.png', 'chest.png', 'npc.png'
    ]
    
    print("\n Verificando tiles...")
    tiles_faltantes = []
    for tile in tiles_requeridos:
        ruta = f'assets/tiles/{tile}'
        if os.path.exists(ruta):
            print(f"  ✅ {tile}")
        else:
            print(f"  ❌ {tile} - FALTANTE")
            tiles_faltantes.append(tile)
    
    print("\n Verificando objetos...")
    objetos_faltantes = []
    for obj in objetos_requeridos:
        ruta = f'assets/objects/{obj}'
        if os.path.exists(ruta):
            print(f"  ✅ {obj}")
        else:
            print(f"  ❌ {obj} - FALTANTE")
            objetos_faltantes.append(obj)
    
    return tiles_faltantes, objetos_faltantes


def crear_placeholders():
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("\n Pillow no está instalado.")
        print("Instalar con pip install Pillow")
        return False
    
    print("\n Creando placeholders...")
    
    # Tiles
    tiles_colores = {
        'grass.png': '#7CFC00',
        'dirt.png': '#8B4513',
        'water.png': '#1E90FF',
        'stone.png': '#696969',
        'sand.png': '#F4A460',
        'snow.png': '#FFFAFA',
        'lava.png': '#FF4500',
        'path.png': '#D2B48C',
    }
    
    for nombre, color in tiles_colores.items():
        ruta = f'assets/tiles/{nombre}'
        if not os.path.exists(ruta):
            img = Image.new('RGB', (32, 32), color)
            draw = ImageDraw.Draw(img)
            
            draw.rectangle([0, 0, 31, 31], outline='black', width=1)
            
            for i in range(0, 32, 4):
                for j in range(0, 32, 4):
                    if (i + j) % 8 == 0:
                        r = int(color[1:3], 16) - 20
                        g = int(color[3:5], 16) - 20
                        b = int(color[5:7], 16) - 20
                        r = max(0, r)
                        g = max(0, g)
                        b = max(0, b)
                        dark_color = f'#{r:02x}{g:02x}{b:02x}'
                        draw.rectangle([i, j, i+2, j+2], fill=dark_color)
            
            img.save(ruta)
            print(f"  ✅ Creado: {nombre}")
    
    objetos_colores = {
        'tree.png': '#006400',
        'rock.png': '#808080',
        'house.png': '#8B4513',
        'chest.png': '#FFD700',
        'npc.png': '#FF6347',
    }
    
    for nombre, color in objetos_colores.items():
        ruta = f'assets/objects/{nombre}'
        if not os.path.exists(ruta):
            img = Image.new('RGB', (32, 32), color)
            draw = ImageDraw.Draw(img)
            
            draw.rectangle([0, 0, 31, 31], outline='black', width=2)
            
            draw.ellipse([8, 8, 24, 24], fill='white', outline='black')
            
            img.save(ruta)
            print(f" Creado: {nombre}")
    
    return True


def main():
    print("=" * 60)
    print("CONFIGURACIÓN DE ASSETS - Editor de Mapas 2D")
    print("=" * 60)
    
    crear_estructura()
    
    tiles_faltantes, objetos_faltantes = verificar_assets()
    
    if tiles_faltantes or objetos_faltantes:
        print("\n Faltan algunos assets.")
        print(f"  Tiles faltantes: {len(tiles_faltantes)}")
        print(f"  Objetos faltantes: {len(objetos_faltantes)}")
        
        print("\n¿Qué deseas hacer?")
        print("  A) Crear placeholders de colores (rápido, funcional)")
        print("  B) Ver instrucciones para descargar assets (mejor calidad)")
        print("  C) Añadir manualmente después")
        
        opcion = input("\nElige una opción (A/B/C): ").strip().upper()
        
        if opcion == 'A':
            if crear_placeholders():
                print("\n Placeholders creados exitosamente.")
                print("El editor funcionará con colores sólidos.")
                print("Puedes reemplazarlos con imágenes reales después.")
            else:
                print("\n No se pudieron crear placeholders.")
                print("Instala Pillow")
        
        elif opcion == 'B':
            print("\nDespués de descargar, ejecuta este script de nuevo")
            print("para verificar los assets.")
            
        else:
            print("\n📝 Recuerda agregar manualmente las imágenes:")
            print("   - Formato: PNG 32x32 píxeles")
            print("   - Ubicación: assets/tiles/ y assets/objects/")
            print("\nEjecuta este script de nuevo después de agregar los assets.")
            
    else:
        print("\nTodos los assets están listos!")
        print("Puedes ejecutar el editor sin problemas.")
    
    print("\n" + "=" * 60)
    print("CONFIGURACIÓN COMPLETA")
    print("=" * 60)
    print("\nPróximos pasos:")
    print("  1. Ejecutar tests: python tests/test_modelo.py")
    print("  2. Ver documentación: docs/MODELO_API.md")
    print("  3. Iniciar desarrollo del editor")


if __name__ == '__main__':
    main()