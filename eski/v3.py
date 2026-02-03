import httpx
import json
import time
from datetime import datetime
import reverse_geocoder as rg 

# --- AYARLAR ---
ALGOLIA_URL = "https://ll8iz711cs-dsn.algolia.net/1/indexes/*/queries"
HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "x-algolia-agent": "strat-bayut-sa-production-frontend-client/6e8d90f0ce92a83fc926add897e80f9879615b81",
    "x-algolia-api-key": "5b970b39b22a4ff1b99e5167696eef3f",
    "x-algolia-application-id": "LL8IZ711CS",
    "referer": "https://www.bayut.sa/",
}

FILTERS = "purpose%3A%22for-sale%22%20AND%20(category.slug%3A%22apartments%22)"
INDEX_NAME = "bayut-sa-production-ads-verified-score-en"

# --- KONTROL ANAHTARLARI ---
BEKLEME_SURESI = 0.5  # Saniye

# 🟢 TURBO HARITA ANAHTARI
TURBO_HARITA_AKTIF = False 

# --- YARDIMCI FONKSİYONLAR ---

def get_turbo_location(lat, lng):
    if not lat or not lng: return None
    try:
        coordinates = (lat, lng)
        results = rg.search(coordinates, mode=1) 
        if results:
            mahalle = results[0].get('name', '')
            sehir = results[0].get('admin1', '')
            return f"{mahalle}, {sehir}"
    except Exception:
        return None
    return None

def fetch_raw_data(page_number):
    params = f"hitsPerPage=100&page={page_number}&filters={FILTERS}"
    payload = {"requests": [{"indexName": INDEX_NAME, "params": params}]}
    try:
        with httpx.Client() as client:
            resp = client.post(ALGOLIA_URL, headers=HEADERS, json=payload, timeout=15)
        return resp.json()["results"][0]["hits"]
    except Exception as e:
        print(f"Bağlantı Hatası: {e}")
        return []

def generate_image_links(photo_ids):
    if not photo_ids: return []
    base_url = "https://images.bayut.sa/thumbnails/{}-800x600.webp"
    return [base_url.format(img_id) for img_id in photo_ids]

def save_raw_sample(hit_item):
    try:
        with open("raw_sample.json", "w", encoding="utf-8") as f:
            json.dump(hit_item, f, ensure_ascii=False, indent=4)
        print("Elan 'raw_sample.json' olarak qeydolundu.")
    except Exception as e:
        print(f"Xam data qeydolunmadi: {e}")

def unix_to_date(ts):
    if ts and ts > 0:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
    return None

def parse_single_listing(hit):
    if not hit: return {}

    extra_fields = hit.get("extraFields") or {}
    agency_info = hit.get("agency") or {}
    owner_agent = hit.get("ownerAgent") or {}

    loc_list = hit.get("location", [])
    location_name = loc_list[-1].get("name") if loc_list else "Bilinmir"
    
    seher = next((x["name"] for x in loc_list if x["level"] == 1), None)
    bolge = next((x["name"] for x in loc_list if x["level"] == 2), None)
    mehle = next((x["name"] for x in loc_list if x["level"] == 3), None)

    lat = hit.get("_geoloc", {}).get("lat")
    lng = hit.get("_geoloc", {}).get("lng")
    
    found_location_eng = None
    if TURBO_HARITA_AKTIF and lat and lng:
        found_location_eng = get_turbo_location(lat, lng)

    raw_ids = hit.get("photoIDs", [])
    linkler = generate_image_links(raw_ids)

    clean_data = {
        "id": hit.get("externalID"),
        "name": hit.get("title"),
        "price": hit.get("price"),
        "rooms": extra_fields.get("rega_property_specs_number_of_rooms"),
        "bath": hit.get("baths"),
        "Area_m2": extra_fields.get("rega_property_specs_area_size"),
        "location": location_name,
        "lat": lat,
        "long": lng,
        "offline_map_location": found_location_eng,
        "building_no": extra_fields.get("rega_location_building_number"),
        "Amenities": hit.get("amenities"),
        "Cover": hit.get("coverPhoto", {}).get("url"),
        "furnished": hit.get("furnishingStatus"),
        "completion_status": hit.get("completionStatus"),
        "createdAt": unix_to_date(hit.get("createdAt")),
        "updatedAt": unix_to_date(hit.get("updatedAt")),
        "reactivatedAt": unix_to_date(hit.get("reactivatedAt")),
        "city": seher,
        "region": bolge,
        "district": mehle,
        "link": f"https://www.bayut.sa/en/property/{hit.get('slug')}.html",
        "building_type": extra_fields.get("rega_property_specs_listing_type", {}).get("en"),
        "all_pictures": linkler,
        "purpose": hit.get("purpose"),
        "rentFrequency": hit.get("rentFrequency"),
        "state": hit.get("state"),
        "type": agency_info.get("type"),
        "beds": hit.get("rooms"),
        "street_name_original": extra_fields.get("rega_location_street_name"),
        "postal_code": extra_fields.get("rega_location_postal_code"),
        "additional_no": extra_fields.get("rega_location_additional_number"),
        "isVerified": hit.get("isVerified"),
        "truBroker": owner_agent.get("isTruBroker"),
        "keywords": hit.get("keywords"),
        "listing_age": (extra_fields.get("rega_additional_info_listing_age") or {}).get("en"),
        "listing_face": (extra_fields.get("rega_additional_info_listing_face") or {}).get("en"),
        "deed_number": extra_fields.get("rega_additional_info_deed_number"),
        "eastern_border_length": extra_fields.get("rega_borders_east_limit_length_char"),
        "western_border_length": extra_fields.get("rega_borders_west_limit_length_char"),
        "northern_border_length": extra_fields.get("rega_borders_north_limit_length_char"),
        "southern_border_length": extra_fields.get("rega_borders_south_limit_length_char"),
        "hasProject": hit.get("hasProject"),
        "is_listing_constrained": (extra_fields.get("rega_additional_info_is_listing_constrained") or {}).get("en"),
        "is_listing_pawned": (extra_fields.get("rega_additional_info_is_listing_pawned") or {}).get("en"),
        "isAgency?": (agency_info.get("type") == "agency"),
        "agency_name": agency_info.get("name"),
        "residence_type": hit.get("residenceType"),
    }
    return clean_data

def run_parsing_sales():
    print(f"--- TURBO SCRAPER BAŞLIYOR (Index: {INDEX_NAME}) ---")
    
    # --- ⏱️ SÜRE ÖLÇÜMÜ BAŞLANGICI ---
    baslangic_zamani = time.time()
    
    if TURBO_HARITA_AKTIF:
        print("🗺️  MOD: Turbo Harita AKTİF")
    else:
        print("⏩ MOD: Turbo Harita KAPALI")

    page_number = 0
    parsed_listings = []
    MAX_PAGE = 600
    
    last_request_time = 0 
    
    while True:
        current_time = time.time()
        
        if current_time - last_request_time >= BEKLEME_SURESI:
            last_request_time = current_time 
            
            simdi_saat = datetime.now().strftime("%H:%M:%S")
            print(f"[{simdi_saat}] 🚀 {page_number}. sayfa çekiliyor...", end=" ")

            raw_hits = fetch_raw_data(page_number)

            if not raw_hits:
                print("Data bitti.")
                break

            if page_number == 0 and len(raw_hits) > 0:
                save_raw_sample(raw_hits[0])

            for item in raw_hits:
                try:
                    temiz_paket = parse_single_listing(item)
                    if temiz_paket:
                        parsed_listings.append(temiz_paket)
                except Exception as e:
                    continue

            print(f"OK. (Toplam: {len(parsed_listings)})")

            page_number += 1
            if page_number >= MAX_PAGE:
                print("🛑 Hedeflenen sayfa sınırına ulaşıldı.")
                break

    filename = "parsed_listings_sales_turbo.json"
    print(f"\n💾 Veriler '{filename}' dosyasına kaydediliyor...")

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(parsed_listings, f, ensure_ascii=False, indent=2)

    print(f"🎉 BİTTİ! Toplam {len(parsed_listings)} satılık ilan kaydedildi.")
    
    # --- ⏱️ SÜRE ÖLÇÜMÜ BİTİŞİ ---
    bitis_zamani = time.time()
    gecen_sure = bitis_zamani - baslangic_zamani
    
    # Süreyi güzel formata çevir (Dakika:Saniye)
    dakika = int(gecen_sure // 60)
    saniye = int(gecen_sure % 60)
    
    print("-" * 40)
    print(f"⏱️  TOPLAM OPERASYON SÜRESİ: {dakika} dakika {saniye} saniye")
    print("-" * 40)

if __name__ == "__main__":
    run_parsing_sales()