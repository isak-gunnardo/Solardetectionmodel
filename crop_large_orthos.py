import os
from PIL import Image
Image.MAX_IMAGE_PIXELS = None  # Inaktivera decompression bomb-skyddet temporärt

def crop_and_resize_large_images(directory, max_pixels=178956970, crop_size=(4000, 4000)):
    image_files = [f for f in os.listdir(directory) if f.endswith('.tif')]
    for fname in image_files:
        path = os.path.join(directory, fname)
        try:
            img = Image.open(path)
            img.load()
            if img.size[0]*img.size[1] > max_pixels:
                # Beskär en ruta från övre vänstra hörnet
                left, upper = 0, 0
                right = min(left + crop_size[0], img.size[0])
                lower = min(upper + crop_size[1], img.size[1])
                cropped = img.crop((left, upper, right, lower))
                out_name = f"cropped_{fname}"
                out_path = os.path.join(directory, out_name)
                cropped.save(out_path)
                print(f"Sparade beskuren bild: {out_path}")
            else:
                print(f"Redan liten nog: {fname}")
        except Exception as e:
            print(f"Fel vid beskärning av {fname}: {e}")

if __name__ == "__main__":
    crop_and_resize_large_images("downloaded_orthophotos")
