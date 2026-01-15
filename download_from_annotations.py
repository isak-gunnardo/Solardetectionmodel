import os
import glob
from lantmateriet_ortofoto import download_orthophoto

annotation_files = glob.glob("annotations_*.txt")

for ann_file in annotation_files:
    with open(ann_file, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        if first_line.startswith("Bild:"):
            image_path = first_line.split(": ")[1].strip()
            image_name = os.path.basename(image_path)
            
            parts = image_name.replace("o", "").replace(".tif", "").split("_")
            east = int(parts[0]) * 1000
            north = int(parts[1]) * 1000
            
            print(f"Laddar ner {image_name}...")
            download_orthophoto(east, north, "downloaded_orthophotos")