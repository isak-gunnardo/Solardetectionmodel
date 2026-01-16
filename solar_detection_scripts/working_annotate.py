import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import numpy as np
import glob

# Öka gräns för bildstorlek
Image.MAX_IMAGE_PIXELS = None

DOWNLOAD_DIR = "downloaded_orthophotos"

class WorkingAnnotator:
    def __init__(self, image_path):
        self.image_path = image_path
        
        # Ladda och förminska bild
        self.img = Image.open(image_path)
        if self.img.mode != 'RGB':
            self.img = self.img.convert('RGB')
        
        # Kraftig förminskning för bättre prestanda
        max_size = 6000
        if max(self.img.size) > max_size:
            ratio = max_size / max(self.img.size)
            new_size = (int(self.img.size[0] * ratio), int(self.img.size[1] * ratio))
            self.img = self.img.resize(new_size, Image.Resampling.LANCZOS)
            print(f"📏 Bild förminskas till {self.img.size}")
        
        # Variabler
        self.mode = 'solpanel'
        self.start_point = None
        self.annotations = []
        self.annotation_patches = []
        self.annotation_mode_active = True  # True = annotation, False = navigation
        self.drawing = False  # För drag-annotation
        
        # Skapa figur MED normal toolbar för zoom
        self.fig, self.ax = plt.subplots(figsize=(14, 9))
        self.ax.imshow(self.img)
        
        # Spara ursprungliga gränser
        self.original_xlim = self.ax.get_xlim()
        self.original_ylim = self.ax.get_ylim()
        
        # Få referens till toolbar för att kunna stänga av/på
        self.toolbar = self.fig.canvas.toolbar
        
        self.update_title()
        
        # Koppla events för drag-annotation
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        
        # Stäng av matplotlib's standardtangentkombinationer för piltangenter
        # Detta förhindrar konflikter med vår egen panorering
        if hasattr(plt, 'rcParams'):
            plt.rcParams['keymap.back'] = []  # Ingen bakåt-funktion på piltangenter
            plt.rcParams['keymap.forward'] = []  # Ingen framåt-funktion
            plt.rcParams['keymap.pan'] = []  # Ingen standard-panorering 
            plt.rcParams['keymap.zoom'] = []  # Ingen standard-zoom
        
        # Temporär rektangel för live-feedback
        self.temp_rect = None
        
        self.show_instructions()

    def show_instructions(self):
        print("\n🎯 KONTROLLER:")
        print("   📝 ANNOTATION-LÄGE:")
        print("      🖱️ HÅLL NED + DRA = Rita rektangel") 
        print("      🚫 Zoom/pan AVSTÄNGT")
        print("")
        print("   🔍 NAVIGATION-LÄGE:")
        print("      🖱️ Mushjul = Normal zoom (matplotlib)")
        print("      🖱️ Toolbar = Normal pan/zoom")
        print("      ⌨️ Piltangenter = Panorera")
        print("      ⌨️ +/- = Finjustera zoom")
        print("      🚫 Drag gör INGENTING")
        print("")
        print("   🔄 VÄXLING:")
        print("      ⌨️ SPACE = Växla ANNOTATION ↔ NAVIGATION")
        print("      ⌨️ S = Solpanel-läge")
        print("      ⌨️ B = Byggnad-läge")
        print("      ⌨️ Z = Ångra")
        print("      ⌨️ R = Återställ zoom")
        print("      ⌨️ Q = Spara")
        print("\n💡 Tangentbords-navigation fungerar bara i navigation-läge!")

    def update_title(self):
        mode_text = "📝 ANNOTATION" if self.annotation_mode_active else "🔍 NAVIGATION"
        type_text = "🟢 SOLPANEL" if self.mode == 'solpanel' else "🟠 BYGGNAD"
        title = f"{mode_text} - {type_text} - Markeringar: {len(self.annotations)}"
        self.ax.set_title(title, fontsize=12, fontweight='bold')
        self.fig.canvas.draw_idle()

    def on_press(self, event):
        if event.inaxes != self.ax or event.button != 1:
            return
            
        # BARA hantera drag i annotation-läge
        if not self.annotation_mode_active:
            return  # Låt matplotlib hantera allt i navigation-läge
            
        # STÄNG AV matplotlib navigation
        if self.toolbar:
            # Inaktivera alla toolbar-verktyg
            if hasattr(self.toolbar, '_active') and self.toolbar._active:
                self.toolbar._active = None
            if hasattr(self.toolbar, 'mode') and self.toolbar.mode != '':
                self.toolbar.mode = ''
                
        # ANNOTATION-LÄGE: Starta drag
        self.start_point = (event.xdata, event.ydata)
        self.drawing = True
        print(f"🎨 Startar ritning från ({int(event.xdata)}, {int(event.ydata)})")

    def on_motion(self, event):
        # BARA i annotation-läge under drag
        if not self.drawing or self.start_point is None or event.inaxes != self.ax or not self.annotation_mode_active:
            return
            
        # Ta bort tidigare temporär rektangel
        if self.temp_rect:
            self.temp_rect.remove()
            
        # Rita ny temporär rektangel
        x1, y1 = self.start_point
        x2, y2 = event.xdata, event.ydata
        
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        x = min(x1, x2)
        y = min(y1, y2)
        
        # Färg baserad på läge
        color = 'lime' if self.mode == 'solpanel' else 'orange'
        
        # Skapa temporär rektangel
        self.temp_rect = patches.Rectangle((x, y), width, height,
                                         linewidth=2, edgecolor=color,
                                         facecolor='none', alpha=0.7,
                                         linestyle='--')
        self.ax.add_patch(self.temp_rect)
        self.fig.canvas.draw_idle()

    def on_release(self, event):
        if not self.drawing or self.start_point is None or event.button != 1:
            return
            
        # BARA i annotation-läge
        if not self.annotation_mode_active:
            self.drawing = False
            self.start_point = None
            return
            
        # Avsluta ritning
        if event.inaxes == self.ax:
            end_point = (event.xdata, event.ydata)
            self.add_annotation(self.start_point, end_point)
        
        # Rensa
        if self.temp_rect:
            self.temp_rect.remove()
            self.temp_rect = None
            
        self.drawing = False
        self.start_point = None

    def add_annotation(self, start, end):
        x1, y1 = start
        x2, y2 = end
        
        # Beräkna rektangel
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        x = min(x1, x2)
        y = min(y1, y2)
        
        # Minsta storlek
        if width < 5 or height < 5:
            print("❌ För liten markering")
            return
        
        # Färg baserad på läge
        color = 'lime' if self.mode == 'solpanel' else 'orange'
        
        # Skapa rektangel
        rect = patches.Rectangle((x, y), width, height,
                               linewidth=3, edgecolor=color,
                               facecolor=color, alpha=0.3)
        self.ax.add_patch(rect)
        
        # Spara annotation
        annotation = {
            'type': self.mode,
            'bbox': (x, y, width, height),
            'color': color
        }
        self.annotations.append(annotation)
        self.annotation_patches.append(rect)
        
        print(f"✅ {self.mode.capitalize()} markerad: {int(width)}x{int(height)}")
        self.update_title()
        self.fig.canvas.draw()

    def toggle_annotation_mode(self):
        self.annotation_mode_active = not self.annotation_mode_active
        
        if self.annotation_mode_active:
            # STÄNG AV matplotlib navigation helt
            if self.toolbar:
                if hasattr(self.toolbar, '_active') and self.toolbar._active:
                    self.toolbar._active = None
                if hasattr(self.toolbar, 'mode'):
                    self.toolbar.mode = ''
                # Återställ alla toolbar-knappar
                try:
                    self.toolbar.update()
                except:
                    pass
            print("📝 ANNOTATION-LÄGE: Drag för att rita rektanglar (zoom AVSTÄNGT)")
        else:
            print("🔍 NAVIGATION-LÄGE: Normal matplotlib zoom/pan aktiv")
            
        self.update_title()

    def on_key(self, event):        
        if event.key == ' ':  # Mellanslag
            self.toggle_annotation_mode()
        elif event.key == 's':
            self.mode = 'solpanel'
            print("🟢 SOLPANEL-LÄGE aktiverat")
            self.update_title()
        elif event.key == 'b':
            self.mode = 'byggnad'
            print("🟠 BYGGNAD-LÄGE aktiverat")
            self.update_title()
        elif event.key == 'z':
            self.undo_last_annotation()
        elif event.key == 'r':
            self.reset_zoom()
        elif event.key == 'q':
            self.save()
        # TANGENTBORDS-NAVIGATION (bara i navigation-läge)
        elif not self.annotation_mode_active:
            if event.key == 'left':
                self.keyboard_pan('left')
            elif event.key == 'right':
                self.keyboard_pan('right')
            elif event.key == 'up':
                self.keyboard_pan('up')
            elif event.key == 'down':
                self.keyboard_pan('down')
            elif event.key == '+' or event.key == '=':
                self.keyboard_zoom(zoom_in=True)
            elif event.key == '-':
                self.keyboard_zoom(zoom_in=False)

    def undo_last_annotation(self):
        if self.annotations:
            self.annotations.pop()
            patch = self.annotation_patches.pop()
            patch.remove()
            self.fig.canvas.draw()
            print(f"↩️ Ångrade markering. Kvar: {len(self.annotations)}")
            self.update_title()
        else:
            print("❌ Inga markeringar att ångra")

    def reset_zoom(self):
        self.ax.set_xlim(self.original_xlim)
        self.ax.set_ylim(self.original_ylim)
        self.fig.canvas.draw()
        print("🔄 Zoom återställd")

    def keyboard_zoom(self, zoom_in=True):
        """Finjustera zoom med +/- (bara i navigation-läge)"""
        if self.annotation_mode_active:
            return  # Blockera i annotation-läge
            
        zoom_factor = 1.1 if zoom_in else 0.9  # Mindre zoom-steg för finjustering
        
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        
        # Centrera zoom kring mitten av nuvarande vy
        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2
        
        width = (xlim[1] - xlim[0]) / zoom_factor
        height = (ylim[1] - ylim[0]) / zoom_factor
        
        new_xlim = [x_center - width/2, x_center + width/2]
        new_ylim = [y_center - height/2, y_center + height/2]
        
        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)
        self.fig.canvas.draw_idle()
        
        action = "in" if zoom_in else "ut"
        print(f"🔍 Finjusterade zoom {action}")

    def keyboard_pan(self, direction):
        """Panorera med piltangenter (bara i navigation-läge)"""
        if self.annotation_mode_active:
            return  # Blockera i annotation-läge
            
        try:
            # Extra skydd: Stäng av toolbar navigation tillfälligt
            if hasattr(self.fig.canvas, 'toolbar') and self.fig.canvas.toolbar:
                original_mode = self.fig.canvas.toolbar.mode
                self.fig.canvas.toolbar.mode = ''
            
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            
            # Panoreringsavstånd (10% av synlig area för mjukare rörelse)
            x_range = xlim[1] - xlim[0]
            y_range = ylim[1] - ylim[0]
            x_step = x_range * 0.10
            y_step = y_range * 0.10
            
            if direction == 'left':
                new_xlim = [xlim[0] - x_step, xlim[1] - x_step]
                self.ax.set_xlim(new_xlim)
            elif direction == 'right':
                new_xlim = [xlim[0] + x_step, xlim[1] + x_step]
                self.ax.set_xlim(new_xlim)
            elif direction == 'up':
                new_ylim = [ylim[0] - y_step, ylim[1] - y_step]
                self.ax.set_ylim(new_ylim)
            elif direction == 'down':
                new_ylim = [ylim[0] + y_step, ylim[1] + y_step]
                self.ax.set_ylim(new_ylim)
            
            # Återställ toolbar-läget
            if hasattr(self.fig.canvas, 'toolbar') and self.fig.canvas.toolbar:
                self.fig.canvas.toolbar.mode = original_mode
            
            self.fig.canvas.draw_idle()
            print(f"🧭 Panorerade {direction}")
        except Exception as e:
            print(f"❌ Panoreringsfel: {e}")

    def save(self):
        if self.annotations:
            filename = f"annotations_{os.path.basename(self.image_path)}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Bild: {self.image_path}\n")
                f.write(f"Totalt markeringar: {len(self.annotations)}\n\n")
                
                for i, ann in enumerate(self.annotations, 1):
                    f.write(f"{i}. {ann['type'].capitalize()}: "
                           f"x={ann['bbox'][0]:.0f}, y={ann['bbox'][1]:.0f}, "
                           f"w={ann['bbox'][2]:.0f}, h={ann['bbox'][3]:.0f}\n")
            
            print(f"💾 Sparade {len(self.annotations)} markeringar till {filename}")
        else:
            print("📝 Inga markeringar att spara")
            
        plt.close()

    def run(self):
        plt.show()

def select_image():
    images = glob.glob(os.path.join(DOWNLOAD_DIR, "*.tif"))
    
    if not images:
        print(f"❌ Inga TIFF-bilder hittades i {DOWNLOAD_DIR}")
        return None
    
    print("🖼️ Tillgängliga bilder:")
    for i, img_path in enumerate(images, 1):
        filename = os.path.basename(img_path)
        print(f"{i}. {filename}")
    
    while True:
        try:
            choice = int(input("\nVälj bild nummer: "))
            if 1 <= choice <= len(images):
                return images[choice-1]
            else:
                print("❌ Ogiltigt val, försök igen")
        except (ValueError, KeyboardInterrupt):
            print("❌ Avbruten")
            return None

def main():
    image_path = select_image()
    if image_path:
        print(f"\n🚀 Öppnar {os.path.basename(image_path)}")
        annotator = WorkingAnnotator(image_path)
        annotator.run()

if __name__ == "__main__":
    main()