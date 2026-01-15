#!/usr/bin/env python
"""
Konverterar TIFF-bilder och annotationer till YOLO-format
Delar upp stora TIFF-bilder i mindre sektioner för träning
"""

import os
import json
import cv2
import numpy as np
from pathlib import Path
import re
from PIL import Image

# Öka PIL:s säkerhetsgräns för stora TIFF-bilder
Image.MAX_IMAGE_PIXELS = None  # Inaktivera säkerhetsgränsen

def parse_annotation_file(annotation_file):
    """Parsar våra annotation-filer till lista av bounding boxes"""
    annotations = []
    
    with open(annotation_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Hitta bild-namnet
    image_match = re.search(r'Bild: (.+)', content)
    if not image_match:
        return None, []
    
    image_path = image_match.group(1)
    
    # Parsa annotationer
    pattern = r'Solcell: x=(\d+), y=(\d+), w=(\d+), h=(\d+)'
    matches = re.findall(pattern, content)
    
    for match in matches:
        x, y, w, h = map(int, match)
        annotations.append({
            'x': x,
            'y': y, 
            'w': w,
            'h': h,
            'class': 0  # solcell class
        })
    
    return image_path, annotations

def split_large_image(image_path, output_dir, tile_size=1024, overlap=100):
    """Delar upp stor bild i mindre tiles"""
    print(f" Läser stor bild: {image_path}")
    
    # Läs bild med PIL för att hantera stora TIFF-filer
    with Image.open(image_path) as img:
        img_width, img_height = img.size
        print(f" Bildstorlek: {img_width}x{img_height} pixlar")
        
        tiles = []
        tile_id = 0
        
        # Dela upp i tiles
        for y in range(0, img_height - overlap, tile_size - overlap):
            for x in range(0, img_width - overlap, tile_size - overlap):
                # Beräkna tile-gränser
                x_end = min(x + tile_size, img_width)
                y_end = min(y + tile_size, img_height)
                
                # Hoppa över för små tiles
                if (x_end - x) < 400 or (y_end - y) < 400:
                    continue
                
                # Extrahera tile
                tile = img.crop((x, y, x_end, y_end))
                
                # Spara tile
                base_name = Path(image_path).stem
                tile_filename = f"{base_name}_tile_{tile_id:03d}.jpg"
                tile_path = output_dir / "images" / "train" / tile_filename
                
                # Konvertera till RGB om nödvändigt
                if tile.mode != 'RGB':
                    tile = tile.convert('RGB')
                
                tile.save(tile_path, 'JPEG', quality=95)
                
                tiles.append({
                    'filename': tile_filename,
                    'x_offset': x,
                    'y_offset': y,
                    'width': x_end - x,
                    'height': y_end - y
                })
                
                tile_id += 1
                
                if tile_id % 10 == 0:
                    print(f"   Skapade {tile_id} tiles...")
        
        print(f" Totalt {len(tiles)} tiles skapade")
        return tiles

def convert_annotations_to_yolo(annotations, tiles, original_width, original_height):
    """Konverterar annotationer till YOLO-format för varje tile"""
    yolo_annotations = {}
    
    for tile in tiles:
        tile_annotations = []
        
        # Kontrollera vilka annotationer som överlappar denna tile
        for ann in annotations:
            # Bounding box koordinater
            bbox_x = ann['x']
            bbox_y = ann['y'] 
            bbox_w = ann['w']
            bbox_h = ann['h']
            
            # Kontrollera överlapp med tile
            tile_x = tile['x_offset']
            tile_y = tile['y_offset']
            tile_w = tile['width']
            tile_h = tile['height']
            
            # Beräkna intersection
            x1 = max(bbox_x, tile_x)
            y1 = max(bbox_y, tile_y)
            x2 = min(bbox_x + bbox_w, tile_x + tile_w)
            y2 = min(bbox_y + bbox_h, tile_y + tile_h)
            
            # Om det finns överlapp
            if x1 < x2 and y1 < y2:
                # Beräkna relativa koordinater inom tile
                rel_x = x1 - tile_x
                rel_y = y1 - tile_y
                rel_w = x2 - x1
                rel_h = y2 - y1
                
                # Konvertera till YOLO-format (normaliserade koordinater)
                center_x = (rel_x + rel_w / 2) / tile_w
                center_y = (rel_y + rel_h / 2) / tile_h
                norm_w = rel_w / tile_w
                norm_h = rel_h / tile_h
                
                # Bara include om bounding box är tillräckligt stor
                if norm_w > 0.01 and norm_h > 0.01:  # Minst 1% av tile
                    tile_annotations.append(f"0 {center_x:.6f} {center_y:.6f} {norm_w:.6f} {norm_h:.6f}")
        
        if tile_annotations:
            yolo_annotations[tile['filename']] = tile_annotations
    
    return yolo_annotations

def main():
    # Sökvägar
    base_dir = Path("C:/Users/claes/OneDrive/Solceller_Lantmateriet")
    output_dir = base_dir / "yolo_dataset"
    
    # Skapa output-struktur
    (output_dir / "images" / "train").mkdir(parents=True, exist_ok=True)
    (output_dir / "images" / "val").mkdir(parents=True, exist_ok=True)
    (output_dir / "labels" / "train").mkdir(parents=True, exist_ok=True)
    (output_dir / "labels" / "val").mkdir(parents=True, exist_ok=True)
    
    print(f" KONVERTERAR TIFF-BILDER OCH ANNOTATIONER TILL YOLO-FORMAT")
    print(f" Output: {output_dir}")
    print()
    
    # Hitta alla annotation-filer
    annotation_files = list(base_dir.glob("annotations_*.txt"))
    print(f" Hittade {len(annotation_files)} annotation-filer")
    
    total_tiles = 0
    total_annotations = 0
    
    for ann_file in annotation_files:
        print(f"\n BEARBETAR: {ann_file.name}")
        
        # Parsa annotationer
        image_path, annotations = parse_annotation_file(ann_file)
        if not image_path or not annotations:
            print(f"   Kunde inte läsa annotationer från {ann_file}")
            continue
            
        # Hitta motsvarande TIFF-bild
        full_image_path = base_dir / image_path
        if not full_image_path.exists():
            print(f"   Bildfil saknas: {full_image_path}")
            continue
            
        print(f"   Hittade {len(annotations)} annotationer")
        
        # Försök läsa bildstorlek först
        try:
            with Image.open(full_image_path) as img:
                original_width, original_height = img.size
                
            print(f"   Bildstorlek: {original_width}x{original_height}")
            
            # Dela upp bild i tiles
            tiles = split_large_image(full_image_path, output_dir)
            
            # Konvertera annotationer
            yolo_annotations = convert_annotations_to_yolo(
                annotations, tiles, original_width, original_height
            )
            
            # Spara YOLO-annotationer
            for tile_filename, tile_anns in yolo_annotations.items():
                label_filename = tile_filename.replace('.jpg', '.txt')
                label_path = output_dir / "labels" / "train" / label_filename
                
                with open(label_path, 'w') as f:
                    f.write('\n'.join(tile_anns))
                
                total_annotations += len(tile_anns)
            
            total_tiles += len(tiles)
            print(f"   Skapade {len(tiles)} tiles med {len(yolo_annotations)} annoterade tiles")
            
        except Exception as e:
            print(f"   Fel vid bearbetning: {e}")
            continue
    
    print(f"\n SLUTRESULTAT:")
    print(f"   {total_tiles} bilder skapade")
    print(f"   {total_annotations} annotationer konverterade")
    
    # Skapa dataset.yaml
    dataset_yaml = f"""# YOLO Dataset - Svenska solceller
# Konverterade TIFF-bilder från Lantmäteriet

path: {output_dir}
train: images/train
val: images/val

# Classes
nc: 1
names:
  0: solcell

# Dataset info
info: |
  Svenska solceller från Lantmäteriets ortofoto
  {total_tiles} bilder, {total_annotations} annotationer
  Konverterade från {len(annotation_files)} TIFF-bilder
"""
    
    with open(output_dir / "dataset.yaml", 'w', encoding='utf-8') as f:
        f.write(dataset_yaml)
    
    print(f"   dataset.yaml skapad")
    print(f" KONVERTERING SLUTFÖRD! 🎯")

if __name__ == "__main__":
    main()