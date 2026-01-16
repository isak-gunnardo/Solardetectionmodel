"""
Konvertera problematiska TIFF-filer till JPG
"""

from PIL import Image
from pathlib import Path
import os

# Tillåt stora bilder
Image.MAX_IMAGE_PIXELS = None

INPUT_DIR = "rich_solar_areas"
OUTPUT_DIR = "rich_solar_areas_jpg"

os.makedirs(OUTPUT_DIR, exist_ok=True)

tiff_files = list(Path(INPUT_DIR).glob("*.tif"))

print(f"Konverterar {len(tiff_files)} TIFF-filer till JPG...")
print("=" * 60)

converted = 0
failed = 0

for idx, tiff_path in enumerate(tiff_files, 1):
    print(f"[{idx}/{len(tiff_files)}] {tiff_path.name}")
    
    try:
        # Öppna med PIL
        img = Image.open(tiff_path)
        
        # Konvertera till RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Spara som JPG
        jpg_name = tiff_path.stem + '.jpg'
        jpg_path = Path(OUTPUT_DIR) / jpg_name
        img.save(jpg_path, 'JPEG', quality=90)
        
        print(f"  ✅ Sparat: {jpg_name}")
        converted += 1
        
    except Exception as e:
        print(f"  ❌ Fel: {e}")
        failed += 1

print("\n" + "=" * 60)
print(f"Konvertering klar!")
print(f"Lyckade: {converted}")
print(f"Misslyckade: {failed}")
print(f"JPG-filer: {OUTPUT_DIR}/")
