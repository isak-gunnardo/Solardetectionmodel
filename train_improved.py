#!/usr/bin/env python
"""
Förbättrad träning från best.pt med optimerade parametrar
Bygger vidare på mega_1093_cpu_optimized med:
- Aggressivare data augmentation
- Större modell (YOLOv8m)
- Optimerade loss weights
- Längre träning med lägre learning rate
"""

from ultralytics import YOLO
import torch

def train_improved_model():
    print("🚀 FÖRBÄTTRAD TRÄNING - Bygger vidare på bästa modellen")
    print("=" * 70)
    
    # Ladda bästa modellen som startpunkt
    model_path = "mega_training_optimized/mega_1093_cpu_optimized/weights/best.pt"
    print(f"\n📁 Laddar basmodell: {model_path}")
    
    # Alternativ 1: Fortsätt från best.pt (rekommenderat för fintuning)
    model = YOLO(model_path)
    
    # Alternativ 2: Om du vill börja från större modell, avkommentera:
    # model = YOLO('yolov8m.pt')  # Mediumstorlek med mer kapacitet
    
    print(f"✅ Modell laddad: {model.model}")
    print(f"📊 Dataset: mega_yolo_dataset (52 bilder, 1093 solceller)")
    print(f"   - Lantmäteriet: 8 bilder, 290 solceller")
    print(f"   - IC/Demo: 44 bilder, 803 solceller")
    
    # Träningsparametrar - OPTIMERADE
    print("\n⚙️ TRÄNINGSKONFIGURATION:")
    print("  • Kraftigare augmentation (mixup, copy-paste)")
    print("  • Högre loss weights för box & class")
    print("  • Lägre learning rate för finare justering")
    print("  • 100 epochs med tålamod 25")
    
    results = model.train(
        # Dataset
        data='mega_yolo_dataset/data.yaml',
        
        # Träningslängd
        epochs=100,              # Ökat från 50
        patience=25,             # Ökat från 12 - mer tid att förbättra
        
        # Batch & Image
        batch=6,                 # Samma (CPU-begränsning)
        imgsz=640,
        
        # Hardware
        device='cpu',
        workers=0,
        
        # Optimizer
        optimizer='AdamW',
        lr0=0.0005,             # HALVERAD från 0.001 - mjukare uppdateringar
        lrf=0.005,              # Lägre slutlig LR
        momentum=0.937,
        weight_decay=0.0005,    # Ökat från 0.0001 - mer regularisering
        
        # Loss weights - ÖKADE för bättre precision
        box=10.0,               # Ökat från 7.5
        cls=1.0,                # Ökat från 0.5
        dfl=2.0,                # Ökat från 1.5
        
        # AGGRESSIV DATA AUGMENTATION
        mosaic=1.0,             # Kombinera 4 bilder
        mixup=0.2,              # ⭐ NY: Blanda bilder (20% chans)
        copy_paste=0.3,         # ⭐ NY: Kopiera objekt mellan bilder
        
        # Färgaugmentation - KRAFTIGARE
        hsv_h=0.03,             # Ökat från 0.015
        hsv_s=0.9,              # Ökat från 0.7
        hsv_v=0.5,              # Ökat från 0.4
        
        # Geometrisk augmentation - KRAFTIGARE
        degrees=15.0,           # ⭐ NY: Rotation ±15 grader
        translate=0.2,          # Ökat från 0.1
        scale=0.9,              # Ökat från 0.5 - mer skalvariation
        shear=5.0,              # ⭐ NY: Skjuvning
        perspective=0.0005,     # ⭐ NY: Perspektivförändring
        flipud=0.1,             # ⭐ NY: Vertikal flip (10%)
        fliplr=0.5,             # Horisontell flip
        
        # Random erasing - KRAFTIGARE
        erasing=0.6,            # Ökat från 0.4
        
        # Annat
        auto_augment='randaugment',
        close_mosaic=10,
        
        # Sparinställningar
        project='improved_training',
        name='mega_improved_v1',
        save=True,
        save_period=5,
        
        # Validation
        val=True,
        plots=True,
        
        # Reproducerbarhet
        seed=42,
        deterministic=True,
        
        # Övriga optimeringar
        amp=True,               # Mixed precision
        verbose=True,
    )
    
    print("\n" + "=" * 70)
    print("✅ TRÄNING KLAR!")
    print(f"📁 Resultat sparade i: improved_training/mega_improved_v1/")
    print(f"🏆 Bästa modell: improved_training/mega_improved_v1/weights/best.pt")
    
    # Visa resultat
    print("\n📊 SLUTRESULTAT:")
    print(f"   Precision: {results.results_dict.get('metrics/precision(B)', 'N/A')}")
    print(f"   Recall: {results.results_dict.get('metrics/recall(B)', 'N/A')}")
    print(f"   mAP50: {results.results_dict.get('metrics/mAP50(B)', 'N/A')}")
    print(f"   mAP50-95: {results.results_dict.get('metrics/mAP50-95(B)', 'N/A')}")
    
    return results

if __name__ == "__main__":
    print("\n🎯 FÖRBÄTTRAD MODELLTRÄNING")
    print("Bygger vidare på: mega_1093_cpu_optimized")
    print("Strategi: Kraftig augmentation + optimerade hyperparametrar")
    print("\n⚠️  OBSERVERA: Detta kommer ta flera timmar på CPU!")
    print("\n▶️  STARTAR TRÄNING...")
    
    train_improved_model()
