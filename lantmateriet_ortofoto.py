import os
import requests
import base64
from pystac_client import Client
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
import glob

# --- CONFIGURATION ---
# OPTIMERAT: Hämtar bara den SENASTE bilden från varje stad (sparar tid & diskutrymme)
API_URL = "https://api.lantmateriet.se/stac-bild/v1/"
TOKEN_URL = "https://api.lantmateriet.se/token"
DOWNLOAD_DIR = "downloaded_orthophotos" # Här hamnar nedladdade filer
# SEARCH_BBOX = [15.02228860, 57.49061890, 15.02228860, 57.49061890] # Ekenässjön 57450
# SEARCH_BBOX = [14.165719, 57.7825634, 14.165719, 57.7825634] # Jönköping
# SEARCH_BBOX = [14.9013204, 57.3696208, 14.9013204, 57.3696208] # Landbro (tidigare använd)

# Nya områden att prova:
# SEARCH_BBOX = [18.0686, 59.3293, 18.0686, 59.3293] # Stockholm (Södermalm) - nyare bilder
# SEARCH_BBOX = [11.9746, 57.7089, 11.9746, 57.7089] # Göteborg (centrum)
# SEARCH_BBOX = [14.165719, 57.7825634, 14.165719, 57.7825634] # Jönköping (centrum)
# SEARCH_BBOX = [13.0038, 55.5950, 13.0038, 55.5950] # Malmö (centrum)
# SEARCH_BBOX = [12.9441, 55.3781, 12.9441, 55.3781] # Malmö villaområde (Limhamn - för mycket vatten)
# SEARCH_BBOX = [16.5448, 59.6099, 16.5448, 59.6099] # Västerås (centrum)
# SEARCH_BBOX = [17.6389, 59.8586, 17.6389, 59.8586] # Uppsala (centrum - bra villaområden)
# SEARCH_BBOX = [18.0686, 59.3293, 18.0686, 59.3293] # Stockholm (Södermalm) - nyare bilder
# SEARCH_BBOX = [18.0600, 59.3300, 18.0600, 59.3300] # Stockholm centrum - för o64000_3175_25_mr24
# SEARCH_BBOX = [15.6219, 58.4109, 15.6219, 58.4109] # Linköping (centrum - teknikstad med många solceller)
STAD_BBOXES = {
    "Stockholm": [18.0686, 59.3293, 18.0686, 59.3293],
    "Göteborg": [11.9746, 57.7089, 11.9746, 57.7089],
    "Malmö": [13.0038, 55.5950, 13.0038, 55.5950],
    "Uppsala": [17.6389, 59.8586, 17.6389, 59.8586],
    "Västerås": [16.5448, 59.6099, 16.5448, 59.6099],
    "Linköping": [15.6219, 58.4109, 15.6219, 58.4109],
    "Örebro": [15.2134, 59.2741, 15.2134, 59.2741],
    "Norrköping": [16.1924, 58.5877, 16.1924, 58.5877],
    "Helsingborg": [12.6945, 56.0465, 12.6945, 56.0465],
    "Jönköping": [14.1657, 57.7826, 14.1657, 57.7826],
    "Lund": [13.1947, 55.7047, 13.1947, 55.7047],
    "Umeå": [20.2653, 63.8258, 20.2653, 63.8258],
    "Gävle": [17.1417, 60.6749, 17.1417, 60.6749],
    "Borås": [12.9401, 57.7210, 12.9401, 57.7210],
    "Eskilstuna": [16.5103, 59.3713, 16.5103, 59.3713],
    "Sundsvall": [17.3069, 62.3908, 17.3069, 62.3908],
    "Södertälje": [17.6278, 59.1955, 17.6278, 59.1955],
    "Karlstad": [13.5040, 59.3793, 13.5040, 59.3793],
    "Täby": [18.0707, 59.4439, 18.0707, 59.4439],
    "Sundbyberg": [17.9711, 59.3601, 17.9711, 59.3601],
}

def download_second_latest_from_city(city, bbox, existing_ids):
    print(f"\n=== {city} ===")
    try:
        auth_headers = get_auth_headers()
        client = Client.open(API_URL, headers=auth_headers)
        print(f"Söker bilder i {city} BBOX: {bbox}")
        search = client.search(bbox=bbox, max_items=10)
        items = list(search.items())
        if not items or len(items) < 2:
            print(f"Hittade inte tillräckligt många bilder i {city}.")
            return None
        # Sortera efter datum, nyast först
        items_sorted = sorted(items, key=lambda x: x.datetime, reverse=True)
        # Hitta första bild som INTE redan finns
        for item in items_sorted[1:]:  # Hoppa över den allra senaste
            if item.id not in existing_ids:
                image_asset = None
                for key in ['file', 'data', 'visual', 'thumbnail']:
                    if key in item.assets:
                        image_asset = item.assets[key]
                        break
                if image_asset:
                    href = image_asset.href
                    ext = href.split('.')[-1]
                    if len(ext) > 4: ext = "tif"
                    filename = f"{item.id}.{ext}"
                    download_file(href, filename, headers=auth_headers)
                    print(f"Nedladdad: {filename}")
                    return item.id
        print(f"Ingen ny bild hittades i {city}.")
        return None
    except Exception as e:
        print(f"Fel vid nedladdning för {city}: {e}")
        return None
# SEARCH_BBOX = [17.6389, 59.8586, 17.6389, 59.8586] # Uppsala (centrum - bra villaområden)
# SEARCH_BBOX = [14.8059, 56.8777, 14.8059, 56.8777] # Växjö (miljöstad med MÅNGA solceller, men 2017)

# --- AUTHENTICATION SETTINGS ---
# Set this to True to use Email/Password. Set to False to use API Keys (OAuth).
USE_BASIC_AUTH = True

# OPTION 1: Basic Authentication (Email & Password)
# For private persons, use your Geotorget email and password.
load_dotenv()

USER_EMAIL = os.getenv("USER_EMAIL")
USER_PASSWORD = os.getenv("USER_PASSWORD")

def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def get_auth_headers():
    """Generates the correct Authorization header based on settings."""
    if USE_BASIC_AUTH:
        print(f"Using Basic Authentication (User: {USER_EMAIL})")
        # Basic Auth requires "Basic base64(user:pass)"
        credentials = f"{USER_EMAIL}:{USER_PASSWORD}"
        base64_creds = base64.b64encode(credentials.encode()).decode()
        return {'Authorization': f'Basic {base64_creds}'}
   
    else:
        # OAuth Flow
        if CONSUMER_KEY == "YOUR_CONSUMER_KEY_HERE":
            print("⚠️  No API Keys provided. Script may fail.")
            return {}
           
        print("Authenticating with OAuth 2.0...")
        try:
            response = requests.post(
                TOKEN_URL,
                data={'grant_type': 'client_credentials'},
                auth=(CONSUMER_KEY, CONSUMER_SECRET)
            )
            response.raise_for_status()
            token = response.json()['access_token']
            print("✓ OAuth Token received")
            return {'Authorization': f'Bearer {token}'}
        except Exception as e:
            print(f"❌ OAuth Authentication failed: {e}")
            raise

def download_file(url, filename, headers=None):
    """Downloads a file in chunks, using the auth headers."""
    print(f"Starting download: {filename}...")
    try:
        with requests.get(url, stream=True, headers=headers) as r:
            r.raise_for_status()
            file_path = os.path.join(DOWNLOAD_DIR, filename)
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"✓ Saved to {file_path}")
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")

def view_downloaded_images():
    """Visar alla nedladdade bilder i mappen"""
    if not os.path.exists(DOWNLOAD_DIR):
        print(f"Mappen {DOWNLOAD_DIR} finns inte än. Kör skriptet först för att ladda ner bilder.")
        return
    
    # Hitta alla bildfiler
    image_files = []
    for ext in ['*.tif', '*.jpg', '*.jpeg', '*.png']:
        image_files.extend(glob.glob(os.path.join(DOWNLOAD_DIR, ext)))
    
    if not image_files:
        print(f"Inga bildfiler hittades i {DOWNLOAD_DIR}")
        return
    
    print(f"Hittade {len(image_files)} bild(er):")
    
    # Visa varje bild
    for i, img_path in enumerate(image_files):
        print(f"\nVisar bild {i+1}: {os.path.basename(img_path)}")
        
        try:
            # Öppna bilden med PIL för att hantera olika format
            img = Image.open(img_path)
            
            # Konvertera till RGB om nödvändigt (för TIFF-filer)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Visa bilden
            plt.figure(figsize=(12, 8))
            plt.imshow(img)
            plt.title(f'Ortofoto: {os.path.basename(img_path)}')
            plt.axis('off')  # Dölj axlar
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            print(f"Kunde inte visa {img_path}: {e}")

def main():
    ensure_directory(DOWNLOAD_DIR)
    # Hämta redan nedladdade bild-ID:n
    existing_files = os.listdir(DOWNLOAD_DIR)
    existing_ids = set()
    for fname in existing_files:
        if fname.endswith('.tif') or fname.endswith('.jpg'):
            id_part = fname.split('.')[0]
            existing_ids.add(id_part)

    for city, bbox in STAD_BBOXES.items():
        download_second_latest_from_city(city, bbox, existing_ids)

    print("\n--- Visar alla nedladdade bilder ---")
    view_downloaded_images()
    view_downloaded_images()

# Funktion för att bara visa befintliga bilder utan att ladda ner nya
def show_existing_images():
    """Visa bara befintliga bilder utan att ladda ner nya"""
    view_downloaded_images()

if __name__ == "__main__":
    # Kör alltid nedladdning och visning automatiskt (Stockholm)
    main()