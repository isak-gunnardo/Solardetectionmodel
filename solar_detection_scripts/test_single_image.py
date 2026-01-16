"""
Testa modellen på en enskild ny bild
Användning: python test_single_image.py <bildväg>
"""

import cv2
import sys
from ultralytics import YOLO
from pathlib import Path

# Modell
MODEL_PATH = "improved_training/mega_improved_fast/weights/best.pt"

# Kolla om användaren angav en bild
if len(sys.argv) < 2:
    print("Användning: python test_single_image.py <bildväg>")
    print("\nExempel:")
    print("  python test_single_image.py C:\\min_bild.jpg")
    print("  python test_single_image.py downloaded_orthophotos\\någon_bild.tif")
    sys.exit(1)

image_path = sys.argv[1]

# Kolla att bilden finns
if not Path(image_path).exists():
    print(f"❌ Bilden finns inte: {image_path}")
    sys.exit(1)

print(f"Testar bild: {image_path}")
print(f"Laddar modell: {MODEL_PATH}")
print("=" * 60)

# Ladda modell
model = YOLO(MODEL_PATH)

# Läs bild
img_path = Path(image_path)
if img_path.suffix.lower() == '.tif':
    print("TIFF-fil detekterad, försöker läsa...")
    try:
        img = cv2.imread(str(img_path), cv2.IMREAD_REDUCED_COLOR_2)
    except:
        img = cv2.imread(str(img_path))
else:
    img = cv2.imread(str(img_path))

if img is None:
    print(f"❌ Kunde inte läsa bilden: {image_path}")
    sys.exit(1)

h, w = img.shape[:2]
print(f"Bildstorlek: {w}x{h} pixels")

# Kör detektion
print("\nKör detektion...")
results = model(img, conf=0.25, verbose=False)

# Räkna detektioner
detections = results[0].boxes
num_detections = len(detections)

print(f"\n{'='*60}")
print(f"✅ RESULTAT: Hittade {num_detections} solpaneler")
print(f"{'='*60}")

if num_detections > 0:
    # Få confidence scores
    confidences = detections.conf.cpu().numpy()
    boxes = detections.xyxy.cpu().numpy()
    
    # Rita detektioner
    annotated = img.copy()
    
    print("\nDetektioner:")
    for i, (box, conf) in enumerate(zip(boxes, confidences)):
        x1, y1, x2, y2 = map(int, box)
        
        # Färg baserat på confidence
        if conf > 0.7:
            color = (0, 255, 0)  # Grön
            conf_level = "HÖG"
        elif conf > 0.5:
            color = (0, 255, 255)  # Gul
            conf_level = "MEDEL"
        else:
            color = (0, 165, 255)  # Orange
            conf_level = "LÅG"
        
        print(f"  #{i+1}: Confidence {conf:.2%} ({conf_level}) - Position ({x1},{y1})-({x2},{y2})")
        
        # Rita rektangel och text
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        label = f"{conf:.2f}"
        label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(annotated, (x1, y1-20), (x1+label_size[0], y1), color, -1)
        cv2.putText(annotated, label, (x1, y1-5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    
    # Confidence-statistik
    high_conf = sum(1 for c in confidences if c > 0.7)
    med_conf = sum(1 for c in confidences if 0.5 < c <= 0.7)
    low_conf = sum(1 for c in confidences if c <= 0.5)
    
    print(f"\nConfidence-fördelning:")
    print(f"  🟢 Hög (>70%): {high_conf}")
    print(f"  🟡 Medel (50-70%): {med_conf}")
    print(f"  🟠 Låg (<50%): {low_conf}")
    
    # Spara resultat
    output_path = f"result_{img_path.stem}.jpg"
    
    # Resize om nödvändigt
    if max(w, h) > 4000:
        scale = 4000 / max(w, h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        annotated = cv2.resize(annotated, (new_w, new_h))
    
    cv2.imwrite(output_path, annotated, [cv2.IMWRITE_JPEG_QUALITY, 85])
    print(f"\n💾 Resultat sparat: {output_path}")
    print(f"Öppna bilden för att se detektionerna!")
else:
    print("\nInga solpaneler hittades i bilden.")
    print("Detta kan betyda:")
    print("  - Det finns verkligen inga solpaneler i bilden")
    print("  - Solpanelerna är för små/otydliga för modellen")
    print("  - Bilden skiljer sig mycket från träningsdata")
