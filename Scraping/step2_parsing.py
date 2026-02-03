import httpx
import json
import time
from datetime import datetime

ALGOLIA_URL = "https://ll8iz711cs-dsn.algolia.net/1/indexes/*/queries" #queriler endeksleri
HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "x-algolia-agent": "strat-bayut-sa-production-frontend-client/6e8d90f0ce92a83fc926add897e80f9879615b81",
    "x-algolia-api-key": "5b970b39b22a4ff1b99e5167696eef3f",
    "x-algolia-application-id": "LL8IZ711CS",
    "referer": "https://www.bayut.sa/",
}

FILTERS = "purpose%3A%22for-sale%22%20AND%20(category.slug%3A%22apartments%22)"
INDEX_NAME = "bayut-sa-production-ads-verified-score-en" # hamisi verified olan (rentdddekilerden deyil)



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
    if not photo_ids:
        return []
    base_url = "https://images.bayut.sa/thumbnails/{}-800x600.webp"
    return [base_url.format(img_id) for img_id in photo_ids]


def save_raw_sample(hit_item):

    try:
        with open("raw_sample.json", "w", encoding="utf-8") as f:
            json.dump(hit_item, f, ensure_ascii=False, indent=4)
        print("Elan'raw_sample.json' olarak qeydolullundu.")
    except Exception as e:
        print(f"xam data qeydolnmadi: {e}")


def unix_to_date(ts):
    if ts and ts > 0:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
    return None


def parse_single_listing(hit):
    raw_ids = hit.get("photoIDs", [])
    linkler = generate_image_links(raw_ids)

    loc_list = hit.get("location", [])
    location_name = loc_list[-1].get("name") if loc_list else "Bilinmir"

    owner_agent = hit.get("ownerAgent") or {}


    locs = hit.get("location", [])


    seher = next((x["name"] for x in locs if x["level"] == 1), None)
    bölgə = next((x["name"] for x in locs if x["level"] == 2), None)
    mehle = next((x["name"] for x in locs if x["level"] == 3), None)

    lat = hit.get("_geoloc", {}).get("lat")
    lng = hit.get("_geoloc", {}).get("lng")

    clean_data = {
        "id": hit.get("externalID"),
        "name": hit.get("title"),
        "price": hit.get("price"),

        "rooms": hit.get("extraFields", {}).get("rega_property_specs_number_of_rooms"),
        "bath": hit.get("baths"),

        "Area_m2": hit.get("extraFields", {}).get("rega_property_specs_area_size"),
        "location": location_name,
        "lat": lat,
        "long": lng,
        "building_no": hit.get("extraFields", {}).get("rega_location_building_number"),
        "Amenities": hit.get("amenities"),
        "Cover": hit.get("coverPhoto", {}).get("url"),
        "furnished": hit.get("furnishingStatus"),
        "completion_status": hit.get("completionStatus"),
        "createdAt": unix_to_date(hit.get("createdAt")),
        "updatedAt": unix_to_date(hit.get("updatedAt")),
        "reactivatedAt": unix_to_date(hit.get("reactivatedAt")),
        "city": seher,  # Riyadh seheri
        "region": bölgə,  # East Riyadh (serqi riyad)
        "district": mehle,
        "link": f"https://www.bayut.sa/en/property/{hit.get('slug')}.html",
        "building_type": hit.get("extraFields", {})
        .get("rega_property_specs_listing_type", {})
        .get("en"),
        "all_pictures": linkler,




        "purpose": hit.get("purpose"),
        "rentFrequency": hit.get("rentFrequency"),
        "state": hit.get("state"),
        "type": hit.get("agency", {}).get("type"),
        "beds": hit.get("rooms"),
        "street_name": hit.get("extraFields", {}).get("rega_location_street_name"),
        "postal_code": hit.get("extraFields", {}).get("rega_location_postal_code"),
        "additional_no": hit.get("extraFields", {}).get("rega_location_additional_number"),
        "isVerified": hit.get("isVerified"),
        "truBroker": owner_agent.get("isTruBroker"),
        "keywords": hit.get("keywords"),
        "listing_age": hit.get("extraFields", {}).get("rega_additional_info_listing_age", {}).get("en"),
        "listing_face": hit.get("extraFields", {}).get("rega_additional_info_listing_face", {}).get("en"),
        "deed_number": hit.get("extraFields", {}).get("rega_additional_info_deed_number", {}),
        "eastern_border_length": hit.get("extraFields", {}).get("rega_borders_east_limit_length_char"),
        "western_border_length": hit.get("extraFields", {}).get("rega_borders_west_limit_length_char"),
        "northern_border_length": hit.get("extraFields", {}).get("rega_borders_north_limit_length_char"),
        "southern_border_length": hit.get("extraFields", {}).get("rega_borders_south_limit_length_char"),
        "hasProject": hit.get("hasProject: "),
        "is_listing_constrained": hit.get("extraFields", {}).get("rega_additional_info_is_listing_constrained", {}).get("en"),
        "is_listing_pawned": hit.get("extraFields", {}).get("rega_additional_info_is_listing_pawned", {}).get("en"),

        "isAgency?": (hit.get("agency", {}).get("type") == "agency"),
        "agency_name": hit.get("agency", {}).get("name"),
        "residence_type": hit.get("residenceType"),


        



    }
    return clean_data


#demeli esasi axagida olacaq
#qeydler
#bayaq evezin dediyi tarix meselesi elave edecem 2. faetureleri qoy 3. csv sini cixard

"""





Description------

Score - nedir? - ???????

Street

productRefreshedAt





"""


def run_parsing_sales():
    print(f"--- data endirme basladilir (index: {INDEX_NAME}) ---")

    page_number = 0
    parsed_listings = []
    MAX_PAGE = 10  # 200 nece dene olmalidi ekstra 400 herehtimal

    while True:
        print(f"🔄 {page_number}. ci sehife data cekilir...", end=" ")

        raw_hits = fetch_raw_data(page_number)

        if not raw_hits:
            print("Data bitti.")
            break

        if page_number == 1 and len(raw_hits) > 1:
            save_raw_sample(raw_hits[1])

        for item in raw_hits:
            temiz_paket = parse_single_listing(item)
            parsed_listings.append(temiz_paket)

        print(f"OK. (Toplam: {len(parsed_listings)})")

        page_number += 1

        if page_number >= MAX_PAGE:
            print("🛑 Hedeflenen sayfa sınırına ulaşıldı.")
            break

        time.sleep(0.5)

    filename = "parsed_listings_sales.json"
    print(f"\nData '{filename}' dosyasına kaydediliyor...")

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(parsed_listings, f, ensure_ascii=False, indent=2)

    print(f" BİTTİ! Toplam {len(parsed_listings)} satılık ilan kaydedildi.")


if __name__ == "__main__":
    run_parsing_sales() #2 cini d'yisdir
