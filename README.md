# Solar Panel Detection Scripts
**YOLOv8-based solar panel detection from aerial orthophotos**

## 🎯 Best Model Performance
- **Model:** YOLOv8s (Small)
- **Training:** 100 epochs (improved_training/mega_improved_fast)
- **Recall:** 45.3% (detects 45% of all solar panels)
- **Precision:** 72.7% (72.7% of detections are correct)
- **mAP50:** 49.2%
- **Dataset:** 52 images, 1093 annotations

## 📁 Project Structure

### Training Scripts
- `train_improved_fast.py` - Best model training (100 epochs, 45% recall) ⭐
- `train_improved.py` - Training with aggressive augmentation
- `train_improved_yolov8m.py` - YOLOv8 Medium model training

### Testing & Evaluation
- `test_improved_model.py` - Test model on multiple images
- `test_single_image.py` - Test on a single image
- `training_stats.py` - Analyze training results
- `recall_analysis.py` - Detection rate analysis
- `performance_assessment.py` - Model performance evaluation
- `compare_results.py` - Compare different model versions

### Data Collection
- `lantmateriet_ortofoto.py` - Download orthophotos from Lantmäteriet API
- `download_rich_areas.py` - Download areas with many solar panels
- `download_from_annotations.py` - Download based on annotations
- `select_best_images.py` - Select best images for annotation

### Data Processing
- `convert_tiff_to_jpg.py` - Convert TIFF to JPG (better performance)
- `crop_large_orthos.py` - Crop large orthophotos into tiles
- `convert_tiff_to_yolo.py` - Convert annotations to YOLO format
- `combine_annotations.py` - Combine multiple annotation files
- `create_ultimate_dataset.py` - Create training dataset

### Annotation Tools
- `annotate_ortofoto.py` - Basic annotation tool
- `working_annotate.py` - Working annotation interface

### Configuration
- `dataset.yaml` - Dataset configuration

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install ultralytics opencv-python pillow pandas numpy
```

### 2. Train Model
```bash
python train_improved_fast.py
```

### 3. Test Model
```bash
python test_single_image.py path/to/image.jpg
```

## 📊 Model Details

### Training Configuration
- **Base model:** YOLOv8s pretrained
- **Image size:** 640x640
- **Batch size:** 6
- **Optimizer:** AdamW
- **Learning rate:** 0.0005
- **Device:** CPU
- **Augmentation:** Balanced (mosaic, color, geometric)

### Dataset Recommendations
- **Format:** PNG or JPG (not TIFF for best performance)
- **Resolution:** 640x640 pixels
- **Quality:** High contrast, clear lighting
- **Source:** Swedish orthophotos from Lantmäteriet

## ⚠️ Important Notes

### Generalization Warning
The model was trained and validated on the same data (no separate validation set). Expected performance on completely new images:
- **Recall:** ~20-35% (lower than reported 45%)
- **Precision:** ~40-60% (lower than reported 73%)

### Image Format Performance
- **Best:** PNG/JPG at 640x640
- **OK:** TIFF (but slower, may miss small panels)
- **Recommended:** Convert TIFF to JPG first using `convert_tiff_to_jpg.py`

## 🔄 Next Steps for Improvement

1. **Create proper train/val split** (80/20)
2. **Collect more diverse data** (200-300 images minimum)
3. **Try YOLOv8m** (Medium) for better accuracy (slower training)
4. **Add validation data** from completely new regions
5. **Increase dataset size** for better generalization

## 📝 License
Educational/Research use

## 🙏 Data Source
Orthophotos from [Lantmäteriet](https://www.lantmateriet.se/) (Swedish Mapping Authority)
