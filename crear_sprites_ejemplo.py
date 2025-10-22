"""
Script para generar sprites de ejemplo para el editor.
Ejecutar desde la raíz del proyecto: python crear_sprites_ejemplo.py
"""

from PIL import Image, ImageDraw
import os

def crear_sprite(nombre, color_principal, patron='solido'):
    """Crea un sprite de 32x32 píxeles."""
    size = 32
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if patron == 'solido':
        # Tile sólido con borde
        draw.rectangle([0, 0, size-1, size-1], fill=color_principal, outline=(0, 0, 0))
    
    elif patron == 'pasto':
        # Base verde
        draw.rectangle([0, 0, size-1, size-1], fill=color_principal)
        # Líneas de pasto
        for i in range(0, size, 4):
            draw.line([i, size, i+2, size-8], fill=(0, 100, 0), width=1)
    
    elif patron == 'agua':
        # Base azul
        draw.rectangle([0, 0, size-1, size-1], fill=color_principal)
        # Ondas
        for y in range(8, size, 8):
            draw.arc([2, y-2, size-2, y+2], 0, 180, fill=(255, 255, 255, 128))
    
    elif patron == 'piedra':
        # Base gris
        draw.rectangle([0, 0, size-1, size-1], fill=color_principal)
        # Grietas
        draw.line([5, 5, 10, 15], fill=(50, 50, 50), width=2)
        draw.line([20, 10, 25, 20], fill=(50, 50, 50), width=2)
        # Sombras
        draw.ellipse([8, 8, 15, 15], fill=(80, 80, 80))
        draw.ellipse([18, 18, 26, 26], fill=(80, 80, 80))
    
    elif patron == 'tierra':
        # Base marrón
        draw.rectangle([0, 0, size-1, size-1], fill=color_principal)
        # Puntos de tierra
        import random
        random.seed(42)  # Para que sea reproducible
        for _ in range(20):
            x = random.randint(0, size-1)
            y = random.randint(0, size-1)
            draw.point((x, y), fill=(101, 67, 33))
    
    elif patron == 'arena':
        # Base beige
        draw.rectangle([0, 0, size-1, size-1], fill=color_principal)
        # Textura de arena
        import random
        random.seed(42)
        for _ in range(30):
            x = random.randint(0, size-1)
            y = random.randint(0, size-1)
            draw.point((x, y), fill=(255, 228, 196))
    
    elif patron == 'nieve':
        # Base blanca
        draw.rectangle([0, 0, size-1, size-1], fill=color_principal)
        # Copos de nieve
        puntos_nieve = [(5, 5), (15, 12), (25, 8), (10, 20), (20, 25), (8, 28)]
        for x, y in puntos_nieve:
            draw.ellipse([x-1, y-1, x+1, y+1], fill=(200, 220, 255))
    
    elif patron == 'lava':
        # Base roja
        draw.rectangle([0, 0, size-1, size-1], fill=color_principal)
        # Burbujas brillantes
        draw.ellipse([8, 8, 14, 14], fill=(255, 200, 0))
        draw.ellipse([20, 18, 26, 24], fill=(255, 200, 0))
        draw.ellipse([5, 22, 9, 26], fill=(255, 150, 0))
    
    elif patron == 'camino':
        # Base marrón claro
        draw.rectangle([0, 0, size-1, size-1], fill=color_principal)
        # Piedras del camino
        piedras = [(8, 10), (20, 8), (15, 20), (25, 22), (5, 24)]
        for x, y in piedras:
            draw.ellipse([x-2, y-2, x+2, y+2], fill=(160, 130, 100))
    
    return img


def main():
    # Crear carpeta si no existe
    os.makedirs('assets/tiles', exist_ok=True)
    
    print("🎨 Generando sprites de ejemplo...")
    
    # Configuración de sprites a crear
    sprites_config = [
        ('grass', (124, 252, 0), 'pasto'),
        ('grass_dark', (34, 139, 34), 'pasto'),
        ('dirt', (139, 69, 19), 'tierra'),
        ('water', (30, 144, 255), 'agua'),
        ('water_deep', (0, 0, 139), 'agua'),
        ('stone', (105, 105, 105), 'piedra'),
        ('rock', (128, 128, 128), 'piedra'),
        ('sand', (244, 164, 96), 'arena'),
        ('snow', (255, 250, 250), 'nieve'),
        ('ice', (176, 224, 230), 'solido'),
        ('lava', (255, 69, 0), 'lava'),
        ('path', (210, 180, 140), 'camino'),
        ('wood', (222, 184, 135), 'solido'),
        ('metal', (192, 192, 192), 'solido'),
        ('wall', (169, 169, 169), 'piedra'),
    ]
    
    for nombre, color, patron in sprites_config:
        ruta = f'assets/tiles/{nombre}.png'
        
        # Solo crear si no existe
        if not os.path.exists(ruta):
            sprite = crear_sprite(nombre, color, patron)
            sprite.save(ruta)
            print(f"  ✅ Creado: {nombre}.png")
        else:
            print(f"  ⏭️  Ya existe: {nombre}.png")
    
    print("\n🎉 ¡Sprites creados exitosamente!")
    print(f"📁 Ubicación: assets/tiles/")
    print(f"📊 Total: {len(sprites_config)} sprites")
    
    # Crear también algunos objetos de ejemplo
    os.makedirs('assets/objects', exist_ok=True)
    
    print("\n🌳 Generando sprites de objetos...")
    
    # Árbol simple
    if not os.path.exists('assets/objects/tree.png'):
        tree = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
        draw = ImageDraw.Draw(tree)
        # Tronco
        draw.rectangle([12, 20, 20, 32], fill=(101, 67, 33))
        # Copa
        draw.ellipse([6, 8, 26, 24], fill=(34, 139, 34))
        tree.save('assets/objects/tree.png')
        print("  ✅ Creado: tree.png")
    
    # Roca
    if not os.path.exists('assets/objects/rock.png'):
        rock = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
        draw = ImageDraw.Draw(rock)
        # Roca irregular
        draw.polygon([(16, 8), (26, 16), (24, 28), (8, 28), (6, 16)], 
                    fill=(128, 128, 128), outline=(80, 80, 80))
        rock.save('assets/objects/rock.png')
        print("  ✅ Creado: rock.png")
    
    # Casa simple
    if not os.path.exists('assets/objects/house.png'):
        house = Image.new('RGBA', (96, 96), (0, 0, 0, 0))
        draw = ImageDraw.Draw(house)
        # Paredes
        draw.rectangle([20, 40, 76, 90], fill=(139, 69, 19))
        # Techo
        draw.polygon([(10, 40), (48, 10), (86, 40)], fill=(178, 34, 34))
        # Puerta
        draw.rectangle([38, 60, 58, 90], fill=(101, 67, 33))
        # Ventana
        draw.rectangle([25, 50, 35, 60], fill=(135, 206, 235))
        house.save('assets/objects/house.png')
        print("  ✅ Creado: house.png")
    
    print("\n✨ ¡Todo listo! Ejecuta el editor para ver los sprites.")


if __name__ == '__main__':
    main()