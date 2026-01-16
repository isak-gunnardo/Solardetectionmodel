#!/usr/bin/env python
"""
Använd den tränade solcellsdetekteringsmodellen
Enkel användning av YOLOv8s-modellen för att hitta solceller
"""

from ultralytics import YOLO
import sys
from pathlib import Path

# Sökväg till modell
MODEL_PATH = "improved_training/mega_improved_fast/weights/best.pt"

def load_model():
    """Laddar den tränade modellen"""
    print(f"🔄 Laddar modell: {MODEL_PATH}")
    
    if not Path(MODEL_PATH).exists():
        print(f"❌ Modellen hittades inte på: {MODEL_PATH}")
        print("💡 Ladda ner från GitHub Releases eller ange rätt sökväg")
        return None
    
    model = YOLO(MODEL_PATH)
    print("✅ Modell laddad!")
    print(f"📊 Prestanda: 45.3% recall, 72.7% precision")
    return model

def detect_single_image(model, image_path, save=True):
    """
    Detektera solceller på en enskild bild
    
    Args:
        model: YOLO-modell
        image_path: Sökväg till bild
        save: Om True, spara resultat
    """
    print(f"\n🔍 Analyserar: {image_path}")
    
    # Kör detektion
    results = model(image_path)
    
    # Få antal detektioner
    num_detections = len(results[0].boxes)
    print(f"☀️  Hittade {num_detections} solceller!")
    
    # Visa detaljer
    if num_detections > 0:
        print("\n📍 Detektioner:")
        for i, box in enumerate(results[0].boxes, 1):
            conf = box.conf[0].item()
            x, y, w, h = box.xywh[0].tolist()
            print(f"   {i}. Position: ({x:.0f}, {y:.0f}), "
                  f"Storlek: {w:.0f}x{h:.0f}, "
                  f"Säkerhet: {conf:.1%}")
    
    # Spara resultat
    if save:
        output_path = f"result_{Path(image_path).stem}.jpg"
        results[0].save(output_path)
        print(f"💾 Resultat sparat: {output_path}")
    
    # Visa bild
    results[0].show()
    
    return results

def detect_folder(model, folder_path, confidence=0.25):
    """
    Detektera solceller på alla bilder i en mapp
    
    Args:
        model: YOLO-modell
        folder_path: Sökväg till mapp med bilder
        confidence: Minsta säkerhet för detektion (0-1)
    """
    print(f"\n📁 Analyserar alla bilder i: {folder_path}")
    
    # Hitta alla bilder
    folder = Path(folder_path)
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.tif']
    images = []
    for ext in image_extensions:
        images.extend(folder.glob(ext))
    
    if not images:
        print("❌ Inga bilder hittades!")
        return
    
    print(f"📊 Hittade {len(images)} bilder")
    
    # Analysera alla bilder
    total_detections = 0
    for img_path in images:
        results = model(str(img_path), conf=confidence, verbose=False)
        num_det = len(results[0].boxes)
        total_detections += num_det
        print(f"   {img_path.name}: {num_det} solceller")
        
        # Spara resultat
        results[0].save(f"result_{img_path.stem}.jpg")
    
    print(f"\n✅ Totalt: {total_detections} solceller i {len(images)} bilder")
    print(f"📈 Genomsnitt: {total_detections/len(images):.1f} solceller/bild")

def get_statistics(model, image_path):
    """
    Få detaljerad statistik om detektioner
    
    Args:
        model: YOLO-modell
        image_path: Sökväg till bild
    """
    results = model(image_path, verbose=False)
    boxes = results[0].boxes
    
    if len(boxes) == 0:
        print("❌ Inga solceller hittades")
        return
    
    # Beräkna statistik
    confidences = [box.conf[0].item() for box in boxes]
    areas = [box.xywh[0][2].item() * box.xywh[0][3].item() for box in boxes]
    
    print(f"\n📊 STATISTIK FÖR {image_path}:")
    print(f"   Antal solceller: {len(boxes)}")
    print(f"   Genomsnittlig säkerhet: {sum(confidences)/len(confidences):.1%}")
    print(f"   Min säkerhet: {min(confidences):.1%}")
    print(f"   Max säkerhet: {max(confidences):.1%}")
    print(f"   Genomsnittlig storlek: {sum(areas)/len(areas):.0f} pixels²")

# ============================================
# HUVUDPROGRAM
# ============================================

if __name__ == "__main__":
    print("☀️  SOLCELLSDETEKTION MED YOLOv8s")
    print("=" * 50)
    
    # Ladda modell
    model = load_model()
    if model is None:
        sys.exit(1)
    
    # Exempel på användning
    print("\n💡 EXEMPEL PÅ ANVÄNDNING:")
    print("1. Analysera en bild:")
    print("   results = detect_single_image(model, 'min_bild.jpg')")
    print("\n2. Analysera en mapp:")
    print("   detect_folder(model, 'mina_bilder/')")
    print("\n3. Få statistik:")
    print("   get_statistics(model, 'bild.jpg')")
    
    # Om användaren angav en bild som argument
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        if Path(image_path).is_file():
            detect_single_image(model, image_path)
        elif Path(image_path).is_dir():
            detect_folder(model, image_path)
        else:
            print(f"❌ Hittar inte: {image_path}")
    else:
        print("\n💡 Använd scriptet:")
        print("   python use_model.py bild.jpg")
        print("   python use_model.py mapp/")
