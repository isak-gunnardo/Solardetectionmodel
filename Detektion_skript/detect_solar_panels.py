from ultralytics import YOLO
import cv2
import numpy as np

# Ladda modellen - din tränade YOLOv8m solpanelmodell
model = YOLO('runs/detect/solar_panels7/weights/best.pt')

# Ladda bilden - nyligen nedladdad
image_path = '59-2680_59-2680_100-0000_2023_101076.png'
image = cv2.imread(image_path)

# Förbättra bilden med histogramutjämning
img_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
image_eq = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)

# Kör detektering med anpassad förtroendetröskel för solpaneler
results = model(image_eq, conf=0.25)  # Anpassad tröskel för solpaneler

# Rita rektanglar runt detekterade solpaneler (klass-id 0 för solar_panel)
panel_boxes = []
for result in results:
    for box, cls, conf in zip(result.boxes.xyxy, result.boxes.cls, result.boxes.conf):
        if int(cls) == 0:  # Klass-id 0 är solar_panel (din tränade modell)
            x1, y1, x2, y2 = map(int, box[:4])
            w, h = x2 - x1, y2 - y1
            aspect_ratio = max(w, h) / max(min(w, h), 1)
            # Färglogik
            if conf > 0.7 and aspect_ratio < 2:
                color = (0, 255, 0)      # Grön: hög confidence, rimlig form
            elif conf > 0.4:
                color = (0, 255, 255)    # Gul: medel confidence
            elif aspect_ratio > 3:
                color = (255, 128, 0)    # Orange: avlång form
            else:
                color = (255, 0, 255)    # Magenta: övrigt
            cv2.rectangle(image_eq, (x1, y1), (x2, y2), color, 2)
            label = f"{conf:.2f}"
            cv2.putText(image_eq, label, (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            panel_boxes.append({'bbox': (x1, y1, x2, y2), 'conf': conf, 'aspect_ratio': aspect_ratio})

# --- Interaktivt OpenCV-fönster med tangentbordsstyrd zoom och pan ---
zoom = 1.0
pan_x, pan_y = 0, 0
win_name = 'Detected Solar Panels (Zoom: +/- | Pan: piltangenter | q: avsluta)'

while True:
    # Skala och panorera bilden
    h, w = image_eq.shape[:2]
    new_w, new_h = int(w * zoom), int(h * zoom)
    resized = cv2.resize(image_eq, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    # Beräkna panoreringsfönster
    view_w, view_h = min(w, new_w), min(h, new_h)
    x0 = min(max(pan_x, 0), max(new_w - view_w, 0))
    y0 = min(max(pan_y, 0), max(new_h - view_h, 0))
    view = resized[y0:y0+view_h, x0:x0+view_w]
    cv2.imshow(win_name, view)
    key = cv2.waitKey(30)
    # Debug: skriv ut key-värde
    # print("Key pressed:", key)
    if key == ord('q'):
        break
    elif key == ord('+') or key == ord('='):
        zoom = min(zoom * 1.2, 10.0)
    elif key == ord('-'):
        zoom = max(zoom / 1.2, 0.2)
    # Vänsterpil
    elif key in [81, 2424832, 65361]:
        pan_x = max(pan_x - int(50 * zoom), 0)
    # Högerpil
    elif key in [83, 2555904, 65363]:
        pan_x = min(pan_x + int(50 * zoom), max(new_w - view_w, 0))
    # Uppil
    elif key in [82, 2490368, 65362]:
        pan_y = max(pan_y - int(50 * zoom), 0)
    # Nedpil
    elif key in [84, 2621440, 65364]:
        pan_y = min(pan_y + int(50 * zoom), max(new_h - view_h, 0))
cv2.destroyAllWindows()