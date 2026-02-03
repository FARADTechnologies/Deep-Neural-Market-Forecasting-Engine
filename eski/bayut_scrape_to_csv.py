import time
import json
import httpx
import pandas as pd

URL = "https://ll8iz711cs-dsn.algolia.net/1/indexes/*/queries"

PARAMS = {
    "x-algolia-agent": "strat-bayut-sa-production-frontend-client/6e8d90f0ce92a83fc926add897e80f9879615b81",
    "x-algolia-api-key": "5b970b39b22a4ff1b99e5167696eef3f",
    "x-algolia-application-id": "LL8IZ711CS",
}

HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "origin": "https://www.bayut.sa",
    "referer": "https://www.bayut.sa/",
    "user-agent": "Mozilla/5.0",
}

INDEX_NAME = "bayut-sa-production-ads-verified-score-en"

def build_params_str(page: int, hits_per_page: int) -> str:
    # Şu an testtekiyle aynı: for-rent + furnished + apartments
    # İstersen furnishingStatus kısmını sonra kaldıracağız.
    filters = "purpose%3A%22for-rent%22%20AND%20furnishingStatus%3A%22furnished%22%20AND%20(category.slug%3A%22apartments%22)"
    return (
        f"page={page}"
        f"&hitsPerPage={hits_per_page}"
        f"&query="
        f"&attributesToRetrieve=*"
        f"&filters={filters}"
    )

def fetch_page(client: httpx.Client, page: int, hits_per_page: int) -> dict:
    payload = {
        "requests": [{
            "indexName": INDEX_NAME,
            "params": build_params_str(page, hits_per_page),
        }]
    }

    # basit retry/backoff
    for attempt in range(6):
        r = client.post(URL, params=PARAMS, headers=HEADERS, json=payload, timeout=30)
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep(2 ** attempt)
            continue
        r.raise_for_status()
        return r.json()

    raise RuntimeError(f"Too many failures on page={page}: last_status={r.status_code}")

def main():
    hits_per_page = 50  # verimli değer
    rows = []

    with httpx.Client() as client:
        first = fetch_page(client, 0, hits_per_page)
        res0 = first["results"][0]
        nb_pages = res0.get("nbPages", 1)
        print("nbPages:", nb_pages)

        for p in range(nb_pages):
            data = first if p == 0 else fetch_page(client, p, hits_per_page)
            hits = data["results"][0]["hits"]
            print(f"page {p}/{nb_pages-1} hits={len(hits)}")

            for h in hits:
                geo = h.get("_geoloc") or {}
                loc = h.get("location") or {}

                cover = h.get("coverPhoto")
                cover_url = None
                if isinstance(cover, dict):
                    # coverPhoto içinde url varsa yakalar
                    cover_url = cover.get("url") or cover.get("webpUrl") or cover.get("path")

                rows.append({
                    "id": h.get("id"),
                    "externalID": h.get("externalID"),
                    "slug": h.get("slug"),
                    "title": h.get("title"),
                    "price": h.get("price"),
                    "rentFrequency": h.get("rentFrequency"),
                    "rooms": h.get("rooms"),
                    "baths": h.get("baths"),
                    "area": h.get("area"),
                    "lat": geo.get("lat"),
                    "lng": geo.get("lng"),
                    "location_name": loc.get("name") if isinstance(loc, dict) else None,
                    "coverPhoto_url": cover_url,
                    "photoCount": h.get("photoCount"),
                    "photoIDs": "|".join(map(str, (h.get("photoIDs") or []))),
                    "createdAt": h.get("createdAt"),
                    "updatedAt": h.get("updatedAt"),
                })

            time.sleep(0.2)  # çok agresif gitmesin

    df = pd.DataFrame(rows)
    df.to_csv("bayut_apartments_furnished_for_rent.csv", index=False, encoding="utf-8-sig")
    print("OK -> bayut_apartments_furnished_for_rent.csv")

if __name__ == "__main__":
    main()
