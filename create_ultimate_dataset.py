#!/usr/bin/env python3
"""
ULTIMATE DATASET CREATOR
Kombinerar ALLA tillgängliga annotationer för maximal träningsprestanda
"""

import os
import shutil
import random
from pathlib import Path

def count_annotations_in_file(label_file):
    """Räknar antal annotationer i en label-fil"""
    try:
        with open(label_file, 'r') as f:
            return len([line for line in f if line.strip()])
    except:
        return 0

def create_ultimate_dataset():
    print("🚀 SKAPAR ULTIMATE DATASET MED ALLA ANNOTATIONER!")
    
    # Sökvägar
    demo_path = Path("c:/Users/claes/OneDrive/Dokument/GitHub/solcell-demo/datasets/solarpanels")
    mega_path = Path("mega_dataset")
    ultimate_path = Path("ultimate_dataset")
    
    # Skapa ultimate dataset mapp
    if ultimate_path.exists():
        shutil.rmtree(ultimate_path)
    ultimate_path.mkdir()
    (ultimate_path / "images" / "train").mkdir(parents=True)
    (ultimate_path / "images" / "val").mkdir(parents=True)
    (ultimate_path / "labels" / "train").mkdir(parents=True)
    (ultimate_path / "labels" / "val").mkdir(parents=True)
    
    all_samples = []
    total_annotations = 0
    
    # 1. DEMO DATA (hög kvalitet)
    if demo_path.exists():
        demo_images = list((demo_path / "images" / "train").glob("*"))
        for img_file in demo_images:
            label_file = demo_path / "labels" / "train" / f"{img_file.stem}.txt"
            if label_file.exists():
                annotations = count_annotations_in_file(label_file)
                if annotations > 0:
                    all_samples.append({
                        'image': img_file,
                        'label': label_file,
                        'source': 'demo',
                        'annotations': annotations
                    })
                    total_annotations += annotations
        print(f"✅ Demo data: {len([s for s in all_samples if s['source'] == 'demo'])} bilder")
    
    # 2. MEGA DATASET (TIFF + kombinerat)
    if mega_path.exists():
        mega_images = list((mega_path / "images" / "train").glob("*.jpg"))
        for img_file in mega_images:
            label_file = mega_path / "labels" / "train" / f"{img_file.stem}.txt"
            if label_file.exists():
                annotations = count_annotations_in_file(label_file)
                if annotations > 0:
                    all_samples.append({
                        'image': img_file,
                        'label': label_file,
                        'source': 'mega',
                        'annotations': annotations
                    })
                    total_annotations += annotations
        print(f"✅ Mega data: {len([s for s in all_samples if s['source'] == 'mega'])} bilder")
    
    print(f"🎯 TOTALT: {len(all_samples)} bilder med {total_annotations} annotationer!")
    
    # Blanda och dela 80/20
    random.seed(42)
    random.shuffle(all_samples)
    
    split_point = int(len(all_samples) * 0.8)
    train_samples = all_samples[:split_point]
    val_samples = all_samples[split_point:]
    
    # Kopiera träningsdata
    train_annotations = 0
    for i, sample in enumerate(train_samples):
        # Kopiera bild
        new_img = ultimate_path / "images" / "train" / f"ultimate_{i:04d}{sample['image'].suffix}"
        shutil.copy2(sample['image'], new_img)
        
        # Kopiera label
        new_label = ultimate_path / "labels" / "train" / f"ultimate_{i:04d}.txt"
        shutil.copy2(sample['label'], new_label)
        
        train_annotations += sample['annotations']
    
    # Kopiera valideringsdata
    val_annotations = 0
    for i, sample in enumerate(val_samples):
        # Kopiera bild
        new_img = ultimate_path / "images" / "val" / f"ultimate_val_{i:04d}{sample['image'].suffix}"
        shutil.copy2(sample['image'], new_img)
        
        # Kopiera label
        new_label = ultimate_path / "labels" / "val" / f"ultimate_val_{i:04d}.txt"
        shutil.copy2(sample['label'], new_label)
        
        val_annotations += sample['annotations']
    
    print(f"📊 TRAIN: {len(train_samples)} bilder, {train_annotations} annotationer")
    print(f"📊 VAL: {len(val_samples)} bilder, {val_annotations} annotationer")
    
    # Skapa dataset.yaml
    dataset_yaml = ultimate_path / "dataset.yaml"
    with open(dataset_yaml, 'w', encoding='utf-8') as f:
        f.write(f"""# ULTIMATE DATASET: Alla svenska solcellsannotationer
# Kombinerar demo-data + TIFF-data för maximal prestanda

path: {ultimate_path.absolute()}
train: images/train
val: images/val

# Classes
nc: 1
names: ['solarpanel']

# Dataset stats
total_images: {len(all_samples)}
total_annotations: {total_annotations}
train_images: {len(train_samples)}
train_annotations: {train_annotations}
val_images: {len(val_samples)}
val_annotations: {val_annotations}

# Sources
demo_data: {len([s for s in all_samples if s['source'] == 'demo'])} bilder
tiff_data: {len([s for s in all_samples if s['source'] == 'mega'])} bilder
""")
    
    print(f"✅ ULTIMATE DATASET SKAPAD!")
    print(f"📁 Sökväg: {ultimate_path.absolute()}")
    print(f"🎯 Redo för träning med {total_annotations} annotationer!")
    
    return ultimate_path, total_annotations

if __name__ == "__main__":
    create_ultimate_dataset()