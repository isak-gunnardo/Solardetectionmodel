#!/usr/bin/env python
"""
SNABBARE träning med balanserad augmentation
Bygger vidare på best.pt men med CPU-vänliga inställningar
"""

from ultralytics import YOLO

def train_improved_fast():
    print("🚀 SNABB FÖRBÄTTRAD TRÄNING")
    print("=" * 70)
    
    model_path = "mega_training_optimized/mega_1093_cpu_optimized/weights/best.pt"
    print(f"\n📁 Laddar: {model_path}")
    
    model = YOLO(model_path)
    
    print(f"📊 Dataset: mega_yolo_dataset (52 bilder, 1093 solceller)")
    print(f"\n⚙️ OPTIMERAD FÖR CPU - Balanserad augmentation")
    
    results = model.train(
        # Dataset
        data='mega_yolo_dataset/data.yaml',
        
        # Träning
        epochs=100,
        patience=25,
        batch=6,
        imgsz=640,
        
        # Hardware
        device='cpu',
        workers=0,
        
        # Optimizer
        optimizer='AdamW',
        lr0=0.0005,
        lrf=0.005,
        momentum=0.937,
        weight_decay=0.0005,
        
        # Loss weights
        box=10.0,
        cls=1.0,
        dfl=2.0,
        
        # BALANSERAD AUGMENTATION (mindre CPU-intensiv)
        mosaic=1.0,              # Behåll mosaic
        mixup=0.0,               # ❌ AVSTÄNGD (för långsam)
        copy_paste=0.0,          # ❌ AVSTÄNGD (för långsam)
        
        # Färgaugmentation
        hsv_h=0.02,              # Måttlig
        hsv_s=0.7,               # Måttlig
        hsv_v=0.4,               # Måttlig
        
        # Geometrisk augmentation
        degrees=10.0,            # Mindre rotation
        translate=0.1,           # Standard
        scale=0.5,               # Standard
        shear=0.0,               # Avstängd
        perspective=0.0,         # Avstängd
        flipud=0.0,              # Avstängd
        fliplr=0.5,              # Standard
        
        # Random erasing
        erasing=0.4,             # Standard
        auto_augment='randaugment',
        close_mosaic=10,
        
        # Sparinställningar
        project='improved_training',
        name='mega_improved_fast',
        save=True,
        save_period=5,
        
        # Validation
        val=True,
        plots=True,
        
        # Övriga
        seed=42,
        deterministic=True,
        amp=True,
        verbose=True,
    )
    
    print("\n" + "=" * 70)
    print("✅ TRÄNING KLAR!")
    print(f"📁 Resultat: improved_training/mega_improved_fast/")
    print(f"🏆 Bästa modell: improved_training/mega_improved_fast/weights/best.pt")
    
    return results

if __name__ == "__main__":
    print("\n🎯 SNABB FÖRBÄTTRAD TRÄNING")
    print("Mindre aggressiv augmentation = snabbare träning på CPU")
    print("Uppskattat: 3-5 minuter/epoch\n")
    
    train_improved_fast()
