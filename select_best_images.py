"""
Kör modellen på alla nya bilder och väljer de 50 bästa
(de med flest solpanel-detektioner)
"""

import cv2
from ultralytics import YOLO
from pathlib import Path
import json

# Konfig
MODEL_PATH = "improved_training/mega_improved_fast/weights/best.pt"
DOWNLOADED_DIR = "rich_solar_areas_jpg"
TRAIN_DIR = "mega_yolo_dataset/images/train"
OUTPUT_FILE = "best_rich_images.json"
NUM_IMAGES = 15

print("Laddar modell...")
model = YOLO(MODEL_PATH)

# Hitta träningsbilder (för att exkludera)
train_images = set()
if Path(TRAIN_DIR).exists():
    for img in Path(TRAIN_DIR).glob("*"):
        train_images.add(img.stem)

print(f"Träningsbilder att exkludera: {len(train_images)}")

# Hitta alla nya bilder
new_images = []
for img_path in Path(DOWNLOADED_DIR).glob("*.jpg"):
    if img_path.stem not in train_images:
        new_images.append(img_path)

print(f"\nHittade {len(new_images)} nya bilder att analysera")
print("=" * 60)

# Analysera varje bild
results_list = []

for idx, img_path in enumerate(new_images, 1):
    print(f"[{idx}/{len(new_images)}] Analyserar: {img_path.name}")
    
    # Läs bild
    try:
        if img_path.suffix.lower() == '.tif':
            try:
                img = cv2.imread(str(img_path), cv2.IMREAD_REDUCED_COLOR_2)
            except:
                img = cv2.imread(str(img_path))
        else:
            img = cv2.imread(str(img_path))
        
        if img is None:
            print(f"  ⚠️ Kunde inte läsa bild")
            continue
        
        # Kör detektion
        pred = model(img, conf=0.25, verbose=False)
        detections = pred[0].boxes
        num_detections = len(detections)
        
        # Räkna confidence-nivåer
        if num_detections > 0:
            confidences = detections.conf.cpu().numpy()
            high_conf = sum(1 for c in confidences if c > 0.7)
            med_conf = sum(1 for c in confidences if 0.5 < c <= 0.7)
            low_conf = sum(1 for c in confidences if c <= 0.5)
        else:
            high_conf = med_conf = low_conf = 0
        
        results_list.append({
            'filename': img_path.name,
            'path': str(img_path),
            'total_detections': num_detections,
            'high_confidence': high_conf,
            'medium_confidence': med_conf,
            'low_confidence': low_conf
        })
        
        print(f"  ✅ {num_detections} solpaneler (H:{high_conf}, M:{med_conf}, L:{low_conf})")
        
    except Exception as e:
        print(f"  ❌ Fel: {e}")
        continue

print("\n" + "=" * 60)
print("ANALYS KLAR")
print("=" * 60)

# Sortera efter antal detektioner (högst först)
results_list.sort(key=lambda x: x['total_detections'], reverse=True)

# Välj top 50
top_50 = results_list[:NUM_IMAGES]

# Spara resultat
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(top_50, f, indent=2, ensure_ascii=False)

print(f"\nTopp {NUM_IMAGES} bilder med flest solpaneler:")
print("-" * 60)

total_panels = 0
for i, result in enumerate(top_50, 1):
    total_panels += result['total_detections']
    print(f"{i:2}. {result['filename']:40} - {result['total_detections']:3} solpaneler "
          f"(H:{result['high_confidence']}, M:{result['medium_confidence']}, L:{result['low_confidence']})")

print("-" * 60)
print(f"Totalt antal solpaneler i de {NUM_IMAGES} valda bilderna: {total_panels}")
print(f"Genomsnitt per bild: {total_panels/NUM_IMAGES:.1f}")
print(f"\n💾 Lista sparad i: {OUTPUT_FILE}")
print("\nNästa steg: Annotera dessa bilder och lägg till i träningsdatan!")
