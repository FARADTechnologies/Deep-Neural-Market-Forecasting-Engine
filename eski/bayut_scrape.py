import argparse
import json
import time
from typing import Any, Dict, List, Optional

import httpx
import pandas as pd

# ========== SABİT AYARLAR ==========
ALGOLIA_URL = "https://ll8iz711cs-dsn.algolia.net/1/indexes/*/queries"

# Senin cURL'den aldığımız 3 değer (aynı kalsın)
ALGOLIA_PARAMS = {
    "x-algolia-agent": "strat-bayut-sa-production-frontend-client/6e8d90f0ce92a83fc926add897e80f9879615b81",
    "x-algolia-api-key": "5b970b39b22a4ff1b99e5167696eef3f",
    "x-algolia-application-id": "LL8IZ711CS",
}

ALGOLIA_HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "origin": "https://www.bayut.sa",
    "referer": "https://www.bayut.sa/",
    "user-agent": "Mozilla/5.0",
}

INDEX_NAME = "bayut-sa-production-ads-verified-score-en"

# İlk etapta cURL ile birebir: for-rent + furnished + apartments
FILTERS_ENCODED_FURNISHED = (
    "purpose%3A%22for-rent%22%20AND%20"
    "furnishingStatus%3A%22furnished%22%20AND%20"
    "(category.slug%3A%22apartments%22)"
)

# İstersen sonra furnished kaldırmak için hazır (şimdilik kullanmıyoruz)
FILTERS_ENCODED_ALL = (
    "purpose%3A%22for-rent%22%20AND%20"
    "(category.slug%3A%22apartments%22)"
)


def build_params_str(page: int, hits_per_page: int, furnished_only: bool = True) -> str:
    filters = FILTERS_ENCODED_FURNISHED if furnished_only else FILTERS_ENCODED_ALL
    return (
        f"page={page}"
        f"&hitsPerPage={hits_per_page}"
        f"&query="
        f"&attributesToRetrieve=*"
        f"&filters={filters}"
    )


def fetch_page(
    client: httpx.Client,
    page: int,
    hits_per_page: int,
    furnished_only: bool = True,
    timeout_s: int = 30,
    max_retries: int = 6,
) -> Dict[str, Any]:
    payload = {
        "requests": [
            {
                "indexName": INDEX_NAME,
                "params": build_params_str(page, hits_per_page, furnished_only=furnished_only),
            }
        ]
    }

    last_status = None
    for attempt in range(max_retries):
        r = client.post(
            ALGOLIA_URL,
            params=ALGOLIA_PARAMS,
            headers=ALGOLIA_HEADERS,
            json=payload,
            timeout=timeout_s,
        )
        last_status = r.status_code

        # geçici hatalar / rate limit
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep(2 ** attempt)
            continue

        r.raise_for_status()
        return r.json()

    raise RuntimeError(f"Fetch failed page={page}. last_status={last_status}")


def inspect_first_hit(h: Dict[str, Any]) -> None:
    photo_like_keys = [k for k in h.keys() if "photo" in k.lower() or "image" in k.lower()]
    print("photo-like keys:", photo_like_keys)

    cover = h.get("coverPhoto")
    print("coverPhoto raw:", json.dumps(cover, ensure_ascii=False)[:1000])

    photo_ids = h.get("photoIDs") or []
    print("first 10 photoIDs:", photo_ids[:10])

    print("some keys:", list(h.keys())[:35])


def extract_row(h: Dict[str, Any]) -> Dict[str, Any]:
    geo = h.get("_geoloc") or {}
    loc = h.get("location") or {}

    cover = h.get("coverPhoto")
    cover_url = None
    if isinstance(cover, dict):
        # Bayut JSON'unda url alanı bazen farklı isimle gelebilir
        cover_url = cover.get("url") or cover.get("webpUrl") or cover.get("path")

    return {
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
    }


def run_test(hits_per_page: int, furnished_only: bool) -> None:
    with httpx.Client() as client:
        data = fetch_page(client, page=0, hits_per_page=hits_per_page, furnished_only=furnished_only)
        res0 = data["results"][0]
        hits = res0["hits"]
        nb_pages = res0.get("nbPages")

        print("OK")
        print("hits:", len(hits))
        print("nbPages:", nb_pages)

        if hits:
            inspect_first_hit(hits[0])


def run_full(
    hits_per_page: int,
    furnished_only: bool,
    max_pages: Optional[int],
    sleep_s: float,
    out_csv: str,
) -> None:
    rows: List[Dict[str, Any]] = []

    with httpx.Client() as client:
        first = fetch_page(client, page=0, hits_per_page=hits_per_page, furnished_only=furnished_only)
        res0 = first["results"][0]
        nb_pages = int(res0.get("nbPages", 1))

        if max_pages is not None:
            nb_pages = min(nb_pages, max_pages)

        print("nbPages (to scrape):", nb_pages)
        for p in range(nb_pages):
            data = first if p == 0 else fetch_page(
                client, page=p, hits_per_page=hits_per_page, furnished_only=furnished_only
            )
            hits = data["results"][0]["hits"]
            print(f"page {p}/{nb_pages-1} hits={len(hits)}")

            for h in hits:
                rows.append(extract_row(h))

            time.sleep(sleep_s)

    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    print("OK ->", out_csv)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["test", "full"], default="test")
    parser.add_argument("--hits-per-page", type=int, default=50)
    parser.add_argument("--furnished-only", action="store_true", default=True)
    parser.add_argument("--all-furnished", dest="furnished_only", action="store_false")  # furnished filtresini kapatır
    parser.add_argument("--max-pages", type=int, default=None)  # test için 3-10 ver
    parser.add_argument("--sleep", type=float, default=0.2)
    parser.add_argument("--out", type=str, default="bayut_apartments.csv")
    args = parser.parse_args()

    if args.mode == "test":
        run_test(hits_per_page=min(args.hits_per_page, 10), furnished_only=args.furnished_only)
    else:
        run_full(
            hits_per_page=args.hits_per_page,
            furnished_only=args.furnished_only,
            max_pages=args.max_pages,
            sleep_s=args.sleep,
            out_csv=args.out,
        )


if __name__ == "__main__":
    main()
