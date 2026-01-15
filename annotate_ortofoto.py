import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, Circle
from PIL import Image
import numpy as np
import glob

DOWNLOAD_DIR = "downloaded_orthophotos"

def show_and_annotate_images():
    """Visa och annotera ortofoto"""
    
    # Hitta alla bildfiler och sortera på senaste ändringsdatum
    # Prioritera beskurna bilder (cropped_*.tif) om de finns
    cropped_files = glob.glob(os.path.join(DOWNLOAD_DIR, "cropped_*.tif"))
    if cropped_files:
        image_files = sorted(cropped_files, key=lambda x: os.path.getmtime(x), reverse=True)
    else:
        image_files = glob.glob(os.path.join(DOWNLOAD_DIR, "*.tif"))
        image_files = sorted(image_files, key=lambda x: os.path.getmtime(x), reverse=True)
    if not image_files:
        print(f"Inga bildfiler hittades i {DOWNLOAD_DIR}")
        return
    newest_images = image_files[:6]
    print(f"Automatiskt valda bilder för annotering:")
    for i, img_path in enumerate(newest_images):
        print(f"{i+1}. {os.path.basename(img_path)}")
    for selected_image in newest_images:
        print(f"\nÖppnar: {os.path.basename(selected_image)}")
    
    # Öppna och visa bilden
    try:
        img = Image.open(selected_image)
        
        # Konvertera till RGB om nödvändigt
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Visa bilden med matplotlib för interaktiv annotering
        fig, ax = plt.subplots(1, 1, figsize=(15, 10))
        ax.imshow(img)
        ax.set_title(f'Ortofoto: {os.path.basename(selected_image)} - Klicka för att annotera')
        
        # Lista för att lagra annotationer
        annotations = []
        
        def on_click(event):
            if event.inaxes != ax:
                return
            
            x, y = event.xdata, event.ydata
            if x is None or y is None:
                return
            
            print(f"Klick på position: ({int(x)}, {int(y)})")
            
            # Fråga vad användaren vill annotera
            annotation_type = input("Vad vill du markera? (s=solpanel, b=byggnad, t=text, c=cirkel): ").lower()
            
            if annotation_type == 's':
                # Markera solpanel (grön rektangel)
                width = int(input("Bredd (pixlar): ") or "50")
                height = int(input("Höjd (pixlar): ") or "30")
                rect = Rectangle((x-width//2, y-height//2), width, height, 
                               linewidth=2, edgecolor='lime', facecolor='none', alpha=0.8)
                ax.add_patch(rect)
                ax.text(x, y-height//2-10, "Solpanel", color='lime', fontsize=10, ha='center', weight='bold')
                annotations.append(f"Solpanel: ({int(x)}, {int(y)})")
                
            elif annotation_type == 'b':
                # Markera byggnad (blå rektangel)
                width = int(input("Bredd (pixlar): ") or "80")
                height = int(input("Höjd (pixlar): ") or "60")
                rect = Rectangle((x-width//2, y-height//2), width, height, 
                               linewidth=2, edgecolor='blue', facecolor='none', alpha=0.8)
                ax.add_patch(rect)
                ax.text(x, y-height//2-10, "Byggnad", color='blue', fontsize=10, ha='center', weight='bold')
                annotations.append(f"Byggnad: ({int(x)}, {int(y)})")
                
            elif annotation_type == 'c':
                # Markera med cirkel
                radius = int(input("Radie (pixlar): ") or "25")
                circle = Circle((x, y), radius, linewidth=2, edgecolor='red', facecolor='none', alpha=0.8)
                ax.add_patch(circle)
                label = input("Etikett: ") or "Markering"
                ax.text(x, y-radius-10, label, color='red', fontsize=10, ha='center', weight='bold')
                annotations.append(f"{label}: ({int(x)}, {int(y)})")
                
            elif annotation_type == 't':
                # Lägg till text
                text = input("Text att lägga till: ")
                if text:
                    ax.text(x, y, text, color='yellow', fontsize=12, ha='center', 
                           bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.7), weight='bold')
                    annotations.append(f"Text '{text}': ({int(x)}, {int(y)})")
            
            plt.draw()
            print("Annotering tillagd! Klicka igen för att lägga till fler, eller stäng fönstret när du är klar.")
        
        # Anslut klick-händelse
        fig.canvas.mpl_connect('button_press_event', on_click)
        
        print("\nInstruktioner:")
        print("- Klicka på bilden för att lägga till annotationer")
        print("- Välj typ: s=solpanel (grön), b=byggnad (blå), c=cirkel (röd), t=text (gul)")
        print("- Stäng fönstret när du är klar")
        
        plt.show()
        
        # Spara annoterad version
        if annotations:
            save_choice = input("Vill du spara den annoterade bilden? (j/n): ").lower()
            if save_choice == 'j':
                output_name = f"annotated_{os.path.basename(selected_image)}.png"
                output_path = os.path.join(DOWNLOAD_DIR, output_name)
                fig.savefig(output_path, dpi=150, bbox_inches='tight')
                print(f"Annoterad bild sparad som: {output_path}")
                
                # Spara textfil med annotationer
                txt_name = f"annotations_{os.path.basename(selected_image)}.txt"
                txt_path = os.path.join(DOWNLOAD_DIR, txt_name)
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(f"Annotationer för {os.path.basename(selected_image)}:\n")
                    f.write("-" * 50 + "\n")
                    for annotation in annotations:
                        f.write(annotation + "\n")
                print(f"Annotationer sparade som: {txt_path}")
        
    except Exception as e:
        print(f"Kunde inte öppna {selected_image}: {e}")

if __name__ == "__main__":
    show_and_annotate_images()