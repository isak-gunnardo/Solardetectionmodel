import os
import glob
import json
from pathlib import Path

class AnnotationCombiner:
    def __init__(self):
        self.combined_annotations = []
        self.class_mapping = {
            'solpanel': 0,
            'byggnad': 1
        }
        self.class_names = ['solpanel', 'byggnad']

    def read_annotation_file(self, file_path):
        """Läs en annotationsfil och extrahera markeringar"""
        annotations = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Hitta bildnamnet
        image_path = None
        for line in lines:
            if line.startswith('Bild:'):
                image_path = line.split(':', 1)[1].strip()
                break
        
        if not image_path:
            print(f"❌ Kunde inte hitta bildnamn i {file_path}")
            return []
        
        # Läs markeringar
        for line in lines:
            if line.strip() and line[0].isdigit():
                try:
                    # Parse "1. Solpanel: x=3575, y=3067, w=44, h=39"
                    parts = line.strip().split(':')
                    if len(parts) >= 2:
                        class_name = parts[1].split(':')[0].strip().lower()
                        coords_part = ':'.join(parts[2:]) if len(parts) > 2 else parts[1].split(':')[1]
                        
                        # Extrahera koordinater
                        coords = {}
                        for coord in coords_part.split(','):
                            if '=' in coord:
                                key, value = coord.split('=')
                                coords[key.strip()] = float(value.strip())
                        
                        if all(k in coords for k in ['x', 'y', 'w', 'h']):
                            annotation = {
                                'image': os.path.basename(image_path),
                                'image_path': image_path,
                                'class': class_name,
                                'x': coords['x'],
                                'y': coords['y'],
                                'width': coords['w'],
                                'height': coords['h']
                            }
                            annotations.append(annotation)
                
                except Exception as e:
                    print(f"❌ Fel vid parsing av rad: {line.strip()} - {e}")
        
        print(f"✅ Läste {len(annotations)} markeringar från {os.path.basename(file_path)}")
        return annotations

    def scan_folders(self, folders):
        """Skanna mappar efter annotationsfiler"""
        all_annotations = []
        
        for folder in folders:
            if not os.path.exists(folder):
                print(f"❌ Mappen {folder} finns inte")
                continue
                
            # Leta efter annotationsfiler
            pattern = os.path.join(folder, "annotations_*.txt")
            files = glob.glob(pattern)
            
            if not files:
                print(f"❌ Inga annotationsfiler hittades i {folder}")
                continue
            
            print(f"\n📁 Skannar {folder}:")
            for file_path in files:
                annotations = self.read_annotation_file(file_path)
                all_annotations.extend(annotations)
        
        return all_annotations

    def combine_annotations(self, folders):
        """Kombinera annotationer från flera mappar"""
        print("🔍 Skannar mappar efter annotationsfiler...")
        
        self.combined_annotations = self.scan_folders(folders)
        
        if not self.combined_annotations:
            print("❌ Inga annotationer hittades")
            return False
        
        # Sammanställning
        class_counts = {}
        image_counts = {}
        
        for ann in self.combined_annotations:
            # Räkna klasser
            class_name = ann['class']
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
            
            # Räkna bilder
            image_name = ann['image']
            image_counts[image_name] = image_counts.get(image_name, 0) + 1
        
        print(f"\n📊 SAMMANFATTNING:")
        print(f"   📝 Totalt annotationer: {len(self.combined_annotations)}")
        print(f"   🖼️ Antal bilder: {len(image_counts)}")
        print(f"   📂 Klasser:")
        for class_name, count in class_counts.items():
            print(f"      - {class_name}: {count} st")
        
        return True

    def export_to_yolo(self, output_folder, image_folder=None):
        """Exportera till YOLO format"""
        os.makedirs(output_folder, exist_ok=True)
        
        # Gruppera per bild
        images_annotations = {}
        for ann in self.combined_annotations:
            image_name = ann['image']
            if image_name not in images_annotations:
                images_annotations[image_name] = []
            images_annotations[image_name].append(ann)
        
        # Skapa YOLO-filer
        for image_name, annotations in images_annotations.items():
            # Anta bildstorlek (eller läs från verklig bild)
            img_width, img_height = 6000, 6000  # Default för dina bilder
            
            # YOLO format: class_id center_x center_y width height (normaliserat 0-1)
            yolo_lines = []
            for ann in annotations:
                class_id = self.class_mapping.get(ann['class'], 0)
                
                # Konvertera till YOLO format (center-baserat, normaliserat)
                center_x = (ann['x'] + ann['width'] / 2) / img_width
                center_y = (ann['y'] + ann['height'] / 2) / img_height
                norm_width = ann['width'] / img_width
                norm_height = ann['height'] / img_height
                
                yolo_line = f"{class_id} {center_x:.6f} {center_y:.6f} {norm_width:.6f} {norm_height:.6f}"
                yolo_lines.append(yolo_line)
            
            # Spara YOLO-fil
            txt_filename = os.path.splitext(image_name)[0] + '.txt'
            txt_path = os.path.join(output_folder, txt_filename)
            
            with open(txt_path, 'w') as f:
                f.write('\n'.join(yolo_lines))
            
            print(f"✅ Skapade {txt_path}")
        
        # Skapa classes.txt
        classes_path = os.path.join(output_folder, 'classes.txt')
        with open(classes_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.class_names))
        
        print(f"✅ Skapade {classes_path}")
        print(f"\n🎯 YOLO-dataset skapat i: {output_folder}")
        print("📝 För träning behöver du:")
        print("   1. Kopiera bildfilerna till samma mapp")
        print("   2. Dela upp i train/val/test mappar")
        print("   3. Skapa dataset.yaml för YOLO")

    def export_to_coco(self, output_file):
        """Exportera till COCO JSON format"""
        coco_data = {
            "images": [],
            "annotations": [],
            "categories": []
        }
        
        # Kategorier
        for i, class_name in enumerate(self.class_names):
            coco_data["categories"].append({
                "id": i,
                "name": class_name,
                "supercategory": "object"
            })
        
        # Gruppera per bild
        images_annotations = {}
        for ann in self.combined_annotations:
            image_name = ann['image']
            if image_name not in images_annotations:
                images_annotations[image_name] = []
            images_annotations[image_name].append(ann)
        
        annotation_id = 1
        image_id = 1
        
        for image_name, annotations in images_annotations.items():
            # Bildinfo
            img_width, img_height = 6000, 6000  # Default
            coco_data["images"].append({
                "id": image_id,
                "file_name": image_name,
                "width": img_width,
                "height": img_height
            })
            
            # Annotationer för denna bild
            for ann in annotations:
                class_id = self.class_mapping.get(ann['class'], 0)
                
                coco_annotation = {
                    "id": annotation_id,
                    "image_id": image_id,
                    "category_id": class_id,
                    "bbox": [ann['x'], ann['y'], ann['width'], ann['height']],
                    "area": ann['width'] * ann['height'],
                    "iscrowd": 0
                }
                
                coco_data["annotations"].append(coco_annotation)
                annotation_id += 1
            
            image_id += 1
        
        # Spara JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(coco_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ COCO dataset skapat: {output_file}")

    def save_combined_summary(self, output_file):
        """Spara en sammanfattning av alla kombinerade annotationer"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("KOMBINERADE ANNOTATIONER\n")
            f.write("=" * 50 + "\n\n")
            
            # Gruppera per bild
            images_annotations = {}
            for ann in self.combined_annotations:
                image_name = ann['image']
                if image_name not in images_annotations:
                    images_annotations[image_name] = []
                images_annotations[image_name].append(ann)
            
            for image_name, annotations in images_annotations.items():
                f.write(f"Bild: {image_name}\n")
                f.write(f"Annotationer: {len(annotations)}\n\n")
                
                for i, ann in enumerate(annotations, 1):
                    f.write(f"{i}. {ann['class'].capitalize()}: "
                           f"x={ann['x']:.0f}, y={ann['y']:.0f}, "
                           f"w={ann['width']:.0f}, h={ann['height']:.0f}\n")
                
                f.write("\n" + "-" * 40 + "\n\n")
            
            # Sammanfattning
            class_counts = {}
            for ann in self.combined_annotations:
                class_name = ann['class']
                class_counts[class_name] = class_counts.get(class_name, 0) + 1
            
            f.write("SAMMANFATTNING:\n")
            f.write(f"Totalt bilder: {len(images_annotations)}\n")
            f.write(f"Totalt annotationer: {len(self.combined_annotations)}\n")
            for class_name, count in class_counts.items():
                f.write(f"{class_name.capitalize()}: {count} st\n")
        
        print(f"✅ Sammanfattning sparad: {output_file}")

def main():
    combiner = AnnotationCombiner()
    
    print("🔗 ANNOTATIONSKOMBINERARE")
    print("=" * 40)
    
    # Ange mappar att skanna
    print("\nAnge mappar att skanna efter annotationsfiler:")
    print("(En mapp per rad, tryck Enter på tom rad för att avsluta)")
    
    folders = []
    while True:
        folder = input(f"Mapp {len(folders)+1}: ").strip()
        if not folder:
            break
        if os.path.exists(folder):
            folders.append(folder)
            print(f"✅ {folder} tillagd")
        else:
            print(f"❌ {folder} finns inte")
    
    if not folders:
        print("❌ Inga mappar angivna")
        return
    
    # Kombinera annotationer
    if not combiner.combine_annotations(folders):
        return
    
    # Exportalternativ
    print("\n📤 EXPORTALTERNATIV:")
    print("1. YOLO format (för YOLOv8/v9 träning)")
    print("2. COCO format (JSON)")
    print("3. Sammanfattning (textfil)")
    print("4. Alla ovanstående")
    
    choice = input("\nVälj (1-4): ").strip()
    
    if choice in ['1', '4']:
        output_folder = input("YOLO output-mapp (t.ex. yolo_dataset): ").strip() or "yolo_dataset"
        combiner.export_to_yolo(output_folder)
    
    if choice in ['2', '4']:
        output_file = input("COCO output-fil (t.ex. annotations.json): ").strip() or "annotations.json"
        combiner.export_to_coco(output_file)
    
    if choice in ['3', '4']:
        output_file = input("Sammanfattningsfil (t.ex. combined_summary.txt): ").strip() or "combined_summary.txt"
        combiner.save_combined_summary(output_file)
    
    print("\n🎉 Klar! Annotationerna har kombinerats och exporterats.")

if __name__ == "__main__":
    main()