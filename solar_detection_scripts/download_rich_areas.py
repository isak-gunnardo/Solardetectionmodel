"""
Ladda ner ortofoto från svenska villaområden med många solpaneler
Fokuserar på storstadsregioner där solpaneler är vanliga
"""

import os
import requests
import base64
from pystac_client import Client
from dotenv import load_dotenv
import time

# --- CONFIGURATION ---
API_URL = "https://api.lantmateriet.se/stac-bild/v1/"
DOWNLOAD_DIR = "rich_solar_areas"

load_dotenv()
USER_EMAIL = os.getenv("USER_EMAIL")
USER_PASSWORD = os.getenv("USER_PASSWORD")

def get_auth_headers():
    credentials = f"{USER_EMAIL}:{USER_PASSWORD}"
    base64_creds = base64.b64encode(credentials.encode()).decode()
    return {'Authorization': f'Basic {base64_creds}'}

def download_file(url, filename, headers=None):
    with requests.get(url, stream=True, headers=headers) as r:
        r.raise_for_status()
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        file_path = os.path.join(DOWNLOAD_DIR, filename)
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return file_path

def download_orthophoto(east, north, output_dir="rich_solar_areas"):
    """Download orthophoto using SWEREF99 TM coordinates"""
    # Convert SWEREF99 TM to WGS84 (approximation for bbox)
    # Note: This is a simple approximation
    lat = 58.0 + (north - 6400000) / 111000
    lon = 15.0 + (east - 500000) / 111000 * 1.5
    
    bbox = [lon, lat, lon, lat]
    
    try:
        auth_headers = get_auth_headers()
        client = Client.open(API_URL, headers=auth_headers)
        search = client.search(bbox=bbox, max_items=5)
        items = list(search.items())
        
        if not items:
            return None
        
        # Take the latest image
        items_sorted = sorted(items, key=lambda x: x.datetime, reverse=True)
        item = items_sorted[0]
        
        image_asset = None
        for key in ['file', 'data', 'visual', 'thumbnail']:
            if key in item.assets:
                image_asset = item.assets[key]
                break
        
        if image_asset:
            href = image_asset.href
            ext = href.split('.')[-1]
            if len(ext) > 4:
                ext = "tif"
            filename = f"{item.id}.{ext}"
            return download_file(href, filename, headers=auth_headers)
        
        return None
    except Exception as e:
        raise e

# Svenska villaområden/förorter kända för många solpaneler
# Koordinater i SWEREF99 TM (öst, nord) i meter
locations = [
    # Stockholm region (villområden)
    (673000, 6580000, "Sollentuna"),
    (669000, 6582000, "Täby"),
    (658000, 6577000, "Bromma"),
    (663000, 6571000, "Älvsjö"),
    (671000, 6575000, "Vallentuna"),
    (651000, 6583000, "Upplands_Väsby"),
    (675000, 6585000, "Åkersberga"),
    
    # Göteborg region
    (319000, 6399000, "Mölndal"),
    (325000, 6401000, "Partille"),
    (307000, 6398000, "Kungsbacka"),
    (330000, 6405000, "Lerum"),
    
    # Malmö/Skåne region  
    (373000, 6165000, "Lomma"),
    (378000, 6170000, "Lund_Väster"),
    (365000, 6160000, "Malmö_Limhamn"),
    (390000, 6175000, "Staffanstorp"),
    
    # Uppsala
    (664000, 6645000, "Uppsala_Gottsunda"),
    (670000, 6648000, "Uppsala_Täljesten"),
    
    # Västerås
    (560000, 6635000, "Västerås_Skiljebo"),
    
    # Örebro
    (533000, 6484000, "Örebro_Söder"),
    
    # Linköping
    (521000, 6471000, "Linköping_Lambohov"),
]

print("=" * 60)
print("NEDLADDNING AV ORTOFOTO FRÅN VILLAOMRÅDEN")
print("=" * 60)
print(f"Kommer ladda ner {len(locations)} bilder från områden med troligen många solpaneler")
print("\nDetta tar ca 5-10 minuter...")
print("=" * 60)

downloaded = 0
failed = 0

for idx, (east, north, name) in enumerate(locations, 1):
    print(f"\n[{idx}/{len(locations)}] {name} (E:{east}, N:{north})")
    
    try:
        result = download_orthophoto(east, north, "rich_solar_areas")
        if result:
            print(f"  ✅ Nedladdat: {result}")
            downloaded += 1
        else:
            print(f"  ⚠️ Ingen bild tillgänglig")
            failed += 1
    except Exception as e:
        print(f"  ❌ Fel: {e}")
        failed += 1
    
    # Vänta lite mellan requests
    if idx < len(locations):
        time.sleep(1)

print("\n" + "=" * 60)
print("NEDLADDNING KLAR")
print("=" * 60)
print(f"Lyckade: {downloaded}")
print(f"Misslyckade: {failed}")
print(f"\nBilder sparade i: rich_solar_areas/")
print("\nNästa steg: Kör modellen på dessa för att hitta de bästa!")
