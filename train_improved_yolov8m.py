#!/usr/bin/env python
"""
Alternativ träning med STÖRRE modell (YOLOv8m)
För bättre prestanda på litet dataset - större kapacitet att lära
"""

from ultralytics import YOLO

def train_with_bigger_model():
    print("🚀 TRÄNING MED STÖRRE MODELL (YOLOv8m)")
    print("=" * 70)
    print("\n💡 YOLOv8m har 25M parametrar (vs 11M för YOLOv8s)")
    print("   → Bättre kapacitet att lära från begränsad data")
    print("   → Men långsammare träning på CPU")
    
    # Använd större basmodell
    model = YOLO('yolov8m.pt')
    
    print(f"\n📊 Dataset: mega_yolo_dataset")
    print(f"   - 52 bilder totalt")
    print(f"   - 1093 annoterade solceller")
    print(f"   - Lantmäteriet + Intelligence Company")
    
    results = model.train(
        data='mega_yolo_dataset/data.yaml',
        
        # Träning
        epochs=100,
        patience=25,
        batch=4,                # MINSKAT från 6 (större modell)
        imgsz=640,
        
        # Hardware
        device='cpu',
        workers=0,
        
        # Optimizer - mjukare för större modell
        optimizer='AdamW',
        lr0=0.0003,            # Lägre än small-modellen
        lrf=0.003,
        weight_decay=0.001,    # Mer regularisering
        
        # Loss
        box=10.0,
        cls=1.0,
        dfl=2.0,
        
        # Kraftig augmentation
        mosaic=1.0,
        mixup=0.25,
        copy_paste=0.3,
        hsv_h=0.03,
        hsv_s=0.9,
        hsv_v=0.5,
        degrees=15.0,
        translate=0.2,
        scale=0.9,
        shear=5.0,
        perspective=0.0005,
        flipud=0.1,
        fliplr=0.5,
        erasing=0.6,
        auto_augment='randaugment',
        
        # Sparinställningar
        project='improved_training',
        name='mega_yolov8m_v1',
        save=True,
        save_period=5,
        
        # Validation
        val=True,
        plots=True,
        seed=42,
        amp=True,
        verbose=True,
    )
    
    print("\n✅ TRÄNING KLAR!")
    print(f"🏆 Modell: improved_training/mega_yolov8m_v1/weights/best.pt")
    
    return results

if __name__ == "__main__":
    print("\n🎯 TRÄNING MED YOLOV8M (MEDIUM)")
    print("⚠️  VARNING: Mycket långsammare på CPU!")
    print("   Uppskattad tid: 12-24 timmar")
    
    choice = input("\n▶️  Fortsätt? (j/n): ")
    
    if choice.lower() == 'j':
        train_with_bigger_model()
    else:
        print("Avbruten.")
