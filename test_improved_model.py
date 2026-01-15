"""
Test av den förbättrade modellen på riktiga ortofoto
Kör inferens och visualiserar resultat
"""

import cv2
import numpy as np
from ultralytics import YOLO
import os
from pathlib import Path
import random

# Konfig
MODEL_PATH = "improved_training/mega_improved_fast/weights/best.pt"
INPUT_DIR = "mega_yolo_dataset/images/train"
OUTPUT_DIR = "test_results"
CONFIDENCE_THRESHOLD = 0.25  # Visa alla detektioner över 25% confidence

# Skapa output-mapp
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Ladda modell
print(f"Laddar modell: {MODEL_PATH}")
model = YOLO(MODEL_PATH)

# Hitta tillgängliga bilder
image_files = []
if os.path.exists(INPUT_DIR):
    for ext in ['*.tif', '*.jpg', '*.png', '*.jpeg']:
        image_files.extend(Path(INPUT_DIR).glob(ext))
    
    # Välj 10 slumpmässiga bilder
    if len(image_files) > 10:
        image_files = random.sample(image_files, 10)
    image_files = sorted(image_files)

if not image_files:
    print(f"\nIngen bilder hittades i {INPUT_DIR}/")
    print("Lägg ortofoto där eller ändra INPUT_DIR i scriptet")
    exit()

print(f"\nHittade {len(image_files)} bilder att testa")
print("=" * 60)

# Testa varje bild
total_detections = 0
for idx, img_path in enumerate(image_files, 1):
    print(f"\n[{idx}/{len(image_files)}] Processar: {img_path.name}")
    
    # Läs bild (använd reducerad upplösning för stora TIFF)
    if img_path.suffix.lower() == '.tif':
        print("  TIFF-fil detekterad, använder halv upplösning...")
        try:
            img = cv2.imread(str(img_path), cv2.IMREAD_REDUCED_COLOR_2)
            scale_factor = 2
        except Exception as e:
            print(f"  ⚠️ Fel vid läsning (troligen flerkanals-TIFF), försöker vanlig läsning...")
            try:
                img = cv2.imread(str(img_path))
                scale_factor = 1
            except:
                print(f"  ⚠️ Kunde inte läsa bild alls: {img_path.name}")
                continue
    else:
        img = cv2.imread(str(img_path))
        scale_factor = 1
    
    if img is None:
        print(f"  ⚠️ Kunde inte läsa bild: {img_path.name}")
        continue
    
    h, w = img.shape[:2]
    print(f"  Bildstorlek: {w}x{h} pixels")
    
    # Kör inferens
    print("  Kör detektion...")
    results = model(img, conf=CONFIDENCE_THRESHOLD, verbose=False)
    
    # Räkna detektioner
    detections = results[0].boxes
    num_detections = len(detections)
    total_detections += num_detections
    
    print(f"  ✅ Hittade {num_detections} solpaneler")
    
    # Rita detektioner på bilden
    annotated = img.copy()
    
    if num_detections > 0:
        # Få confidence scores och sortera
        confidences = detections.conf.cpu().numpy()
        boxes = detections.xyxy.cpu().numpy()
        
        # Rita varje detektion
        for i, (box, conf) in enumerate(zip(boxes, confidences)):
            x1, y1, x2, y2 = map(int, box)
            
            # Färg baserat på confidence (grön=hög, gul=medel, röd=låg)
            if conf > 0.7:
                color = (0, 255, 0)  # Grön
            elif conf > 0.5:
                color = (0, 255, 255)  # Gul
            else:
                color = (0, 165, 255)  # Orange
            
            # Rita rektangel
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            
            # Rita confidence score
            label = f"{conf:.2f}"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(annotated, (x1, y1-20), (x1+label_size[0], y1), color, -1)
            cv2.putText(annotated, label, (x1, y1-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        # Visa confidence-fördelning
        high_conf = np.sum(confidences > 0.7)
        med_conf = np.sum((confidences > 0.5) & (confidences <= 0.7))
        low_conf = np.sum(confidences <= 0.5)
        print(f"    Hög conf (>70%): {high_conf}")
        print(f"    Medel conf (50-70%): {med_conf}")
        print(f"    Låg conf (<50%): {low_conf}")
    
    # Spara resultat
    output_path = Path(OUTPUT_DIR) / f"result_{img_path.stem}.jpg"
    
    # Resize om bilden är för stor för att spara (max 4000 pixels)
    if max(w, h) > 4000:
        scale = 4000 / max(w, h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        annotated = cv2.resize(annotated, (new_w, new_h))
        print(f"  Skalade ner till {new_w}x{new_h} för att spara")
    
    cv2.imwrite(str(output_path), annotated, [cv2.IMWRITE_JPEG_QUALITY, 85])
    print(f"  💾 Sparat: {output_path}")

# Sammanfattning
print("\n" + "=" * 60)
print("TESTSAMMANFATTNING")
print("=" * 60)
print(f"Testade bilder: {len(image_files)}")
print(f"Totalt antal detekterade solpaneler: {total_detections}")
print(f"Genomsnitt per bild: {total_detections/len(image_files):.1f}")
print(f"\nResultat sparade i: {OUTPUT_DIR}/")
print("\nÖppna bilderna i test_results/ för att se detektionerna!")
