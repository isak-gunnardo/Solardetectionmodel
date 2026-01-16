#!/usr/bin/env python
"""
Ladda ner och importera solcellsdetekteringsmodellen
Automatisk nedladdning från GitHub Releases
"""

import os
import urllib.request
from pathlib import Path

# GitHub Release info
GITHUB_REPO = "isak-gunnardo/Solardetectionmodel"
RELEASE_TAG = "v1.0"
MODEL_FILENAME = "best.pt"
MODEL_URL = f"https://github.com/{GITHUB_REPO}/releases/download/{RELEASE_TAG}/{MODEL_FILENAME}"

# Lokal sökväg för modellen
LOCAL_MODEL_PATH = "models/yolov8s_solar_best.pt"

def download_model():
    """
    Laddar ner modellen från GitHub Releases
    """
    print("☀️  SOLCELLSDETEKTERING - MODELLIMPORT")
    print("=" * 50)
    
    # Skapa models-mapp om den inte finns
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    model_path = Path(LOCAL_MODEL_PATH)
    
    # Kolla om modellen redan finns
    if model_path.exists():
        print(f"✅ Modellen finns redan: {LOCAL_MODEL_PATH}")
        print(f"📦 Storlek: {model_path.stat().st_size / (1024*1024):.1f} MB")
        return str(model_path)
    
    print(f"📥 Laddar ner modell från GitHub Releases...")
    print(f"🔗 URL: {MODEL_URL}")
    print(f"💾 Sparas till: {LOCAL_MODEL_PATH}")
    print()
    
    try:
        # Ladda ner med progress
        def show_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(downloaded / total_size * 100, 100)
            mb_downloaded = downloaded / (1024*1024)
            mb_total = total_size / (1024*1024)
            print(f"\r⏳ {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end='')
        
        urllib.request.urlretrieve(MODEL_URL, model_path, show_progress)
        print()  # Ny rad efter progress
        print(f"✅ Nedladdning klar!")
        print(f"📦 Storlek: {model_path.stat().st_size / (1024*1024):.1f} MB")
        
        return str(model_path)
        
    except Exception as e:
        print(f"\n❌ Fel vid nedladdning: {e}")
        print(f"\n💡 Ladda ner manuellt från:")
        print(f"   {MODEL_URL}")
        print(f"   Spara som: {LOCAL_MODEL_PATH}")
        return None

def load_model():
    """
    Importerar modellen för användning
    
    Returns:
        YOLO model eller None om misslyckades
    """
    try:
        from ultralytics import YOLO
    except ImportError:
        print("❌ Ultralytics är inte installerat!")
        print("💡 Installera med: pip install ultralytics")
        return None
    
    # Ladda ner om inte finns
    model_path = download_model()
    if model_path is None:
        return None
    
    # Ladda modell
    print("\n🔄 Laddar modell...")
    model = YOLO(model_path)
    
    print("✅ Modell laddad och redo att användas!")
    print("\n📊 MODELLPRESTANDA:")
    print("   • Recall: 45.3% (hittar 45% av alla solceller)")
    print("   • Precision: 72.7% (73% av detektioner är korrekta)")
    print("   • mAP50: 49.2%")
    print("\n💡 ANVÄNDNING:")
    print("   results = model('min_bild.jpg')")
    print("   results[0].show()  # Visa resultat")
    
    return model

# ============================================
# HUVUDPROGRAM
# ============================================

if __name__ == "__main__":
    model = load_model()
    
    if model:
        print("\n" + "=" * 50)
        print("✅ KLAR ATT ANVÄNDAS!")
        print("=" * 50)
        
        print("\n📝 Exempel:")
        print("""
from import_model import load_model

# Ladda modell
model = load_model()

# Analysera bild
results = model('ortofoto.jpg')

# Visa resultat
results[0].show()

# Spara resultat
results[0].save('resultat.jpg')
""")
