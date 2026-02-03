import argparse
import csv
import json
import time
from typing import Any, Dict, List, Optional

import httpx

ALGOLIA_URL = "https://ll8iz711cs-dsn.algolia.net/1/indexes/*/queries"

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

FILTERS_FURNISHED = (
    "purpose%3A%22for-rent%22%20AND%20"
    "furnishingStatus%3A%22furnished%22%20AND%20"
    "(category.slug%3A%22apartments%22)"
)

FILTERS_ALL_APTS = (
    "purpose%3A%22for-rent%22%20AND%20"
    "(category.slug%3A%22apartments%22)"
)

CSV_FIELDS = [
    # IDs / link
    "externalID", "slug", "id", "referenceNumber", "permitNumber",
    # core
    "title", "purpose", "price", "rentFrequency", "rooms", "baths", "area",
    "createdAt", "updatedAt", "reactivatedAt",
    # geo
    "lat", "lng",
    # location levels
    "loc0_name", "loc0_slug",
    "loc1_name", "loc1_slug",
    "loc2_name", "loc2_slug",
    "loc3_name", "loc3_slug",
    "loc4_name", "loc4_slug",
    # category levels
    "cat0_name", "cat0_slug",
    "cat1_name", "cat1_slug",
    "cat2_name", "cat2_slug",
    # media
    "coverPhoto_url", "photoCount", "videoCount", "photoIDs",
    # features/text-ish
    "amenities", "keywords",
    # nested packed
    "extraFields_json",
]

def build_params_str(page: int, hits_per_page: int, furnished_only: bool) -> str:
    filters = FILTERS_FURNISHED if furnished_only else FILTERS_ALL_APTS
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
    furnished_only: bool,
    max_retries: int = 6,
) -> Dict[str, Any]:
    payload = {
        "requests": [{
            "indexName": INDEX_NAME,
            "params": build_params_str(page, hits_per_page, furnished_only),
        }]
    }

    last_status = None
    for attempt in range(max_retries):
        r = client.post(
            ALGOLIA_URL,
            params=ALGOLIA_PARAMS,
            headers=ALGOLIA_HEADERS,
            json=payload,
            timeout=30,
        )
        last_status = r.status_code
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep(2 ** attempt)
            continue
        r.raise_for_status()
        return r.json()

    raise RuntimeError(f"Fetch failed page={page}. last_status={last_status}")

def safe_join(values: Optional[List[Any]]) -> str:
    if not values:
        return ""
    out = []
    for v in values:
        if isinstance(v, (str, int, float, bool)):
            out.append(str(v))
        else:
            out.append(json.dumps(v, ensure_ascii=False))
    return "|".join(out)

def get_list_level(items: Any, idx: int) -> Dict[str, str]:
    if not isinstance(items, list) or idx >= len(items) or not isinstance(items[idx], dict):
        return {"name": "", "slug": ""}
    return {
        "name": str(items[idx].get("name", "")) if items[idx].get("name") is not None else "",
        "slug": str(items[idx].get("slug", "")) if items[idx].get("slug") is not None else "",
    }

def coverphoto_url(hit: Dict[str, Any]) -> str:
    cp = hit.get("coverPhoto")
    if isinstance(cp, dict):
        return cp.get("url") or cp.get("webpUrl") or cp.get("path") or ""
    return ""

def redact_pii(obj: Any) -> Any:
    """
    Deep redaction:
    - Any key containing "phone" (case-insensitive) => "<REDACTED>"
    - Key exactly "contactName" => "<REDACTED>"
    Works for nested dicts/lists (extraFields included).
    """
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            lk = k.lower()
            if "phone" in lk or k == "contactName":
                out[k] = "<REDACTED>"
            else:
                out[k] = redact_pii(v)
        return out
    if isinstance(obj, list):
        return [redact_pii(x) for x in obj]
    return obj

def flatten_hit(hit: Dict[str, Any]) -> Dict[str, Any]:
    geo = hit.get("_geoloc") or {}
    loc = hit.get("location")
    cat = hit.get("category")

    loc0 = get_list_level(loc, 0); loc1 = get_list_level(loc, 1); loc2 = get_list_level(loc, 2)
    loc3 = get_list_level(loc, 3); loc4 = get_list_level(loc, 4)

    cat0 = get_list_level(cat, 0); cat1 = get_list_level(cat, 1); cat2 = get_list_level(cat, 2)

    extra = hit.get("extraFields")
    extra_json = json.dumps(extra, ensure_ascii=False) if isinstance(extra, dict) else ""

    return {
        "externalID": hit.get("externalID", ""),
        "slug": hit.get("slug", ""),
        "id": hit.get("id", ""),
        "referenceNumber": hit.get("referenceNumber", ""),
        "permitNumber": hit.get("permitNumber", ""),
        "title": hit.get("title", ""),
        "purpose": hit.get("purpose", ""),
        "price": hit.get("price", ""),
        "rentFrequency": hit.get("rentFrequency", ""),
        "rooms": hit.get("rooms", ""),
        "baths": hit.get("baths", ""),
        "area": hit.get("area", ""),
        "createdAt": hit.get("createdAt", ""),
        "updatedAt": hit.get("updatedAt", ""),
        "reactivatedAt": hit.get("reactivatedAt", ""),
        "lat": geo.get("lat", ""),
        "lng": geo.get("lng", ""),
        "loc0_name": loc0["name"], "loc0_slug": loc0["slug"],
        "loc1_name": loc1["name"], "loc1_slug": loc1["slug"],
        "loc2_name": loc2["name"], "loc2_slug": loc2["slug"],
        "loc3_name": loc3["name"], "loc3_slug": loc3["slug"],
        "loc4_name": loc4["name"], "loc4_slug": loc4["slug"],
        "cat0_name": cat0["name"], "cat0_slug": cat0["slug"],
        "cat1_name": cat1["name"], "cat1_slug": cat1["slug"],
        "cat2_name": cat2["name"], "cat2_slug": cat2["slug"],
        "coverPhoto_url": coverphoto_url(hit),
        "photoCount": hit.get("photoCount", ""),
        "videoCount": hit.get("videoCount", ""),
        "photoIDs": safe_join(hit.get("photoIDs")),
        "amenities": safe_join(hit.get("amenities")),
        "keywords": safe_join(hit.get("keywords")),
        "extraFields_json": extra_json,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-csv", default="listings.csv")
    ap.add_argument("--out-jsonl", default="listings_raw.jsonl")
    ap.add_argument("--hits-per-page", type=int, default=50)
    ap.add_argument("--sleep", type=float, default=0.2)
    ap.add_argument("--max-pages", type=int, default=None, help="Test için 20 gibi. None = hepsi")
    ap.add_argument("--all-apartments", action="store_true", help="furnished filtresini kapatır")
    ap.add_argument("--redact-pii", action="store_true", help="jsonl içinde phone/contact maskeler (deep)")
    args = ap.parse_args()

    furnished_only = not args.all_apartments

    scraped = 0
    unique_external = set()
    expected_nb_hits = None
    expected_nb_pages = None

    with httpx.Client() as client, \
         open(args.out_jsonl, "w", encoding="utf-8") as f_jsonl, \
         open(args.out_csv, "w", newline="", encoding="utf-8-sig") as f_csv:

        writer = csv.DictWriter(f_csv, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()

        first = fetch_page(client, 0, args.hits_per_page, furnished_only)
        res0 = first["results"][0]
        expected_nb_pages = int(res0.get("nbPages", 1))
        expected_nb_hits = res0.get("nbHits")

        nb_pages = expected_nb_pages
        if args.max_pages is not None:
            nb_pages = min(nb_pages, args.max_pages)

        print("Expected nbPages:", expected_nb_pages, " | Running pages:", nb_pages)
        print("Expected nbHits:", expected_nb_hits)

        for p in range(nb_pages):
            data = first if p == 0 else fetch_page(client, p, args.hits_per_page, furnished_only)
            hits = data["results"][0]["hits"]
            print(f"page {p}/{nb_pages-1} hits={len(hits)}")

            for hit in hits:
                row = flatten_hit(hit)
                writer.writerow(row)

                raw_obj = redact_pii(hit) if args.redact_pii else hit
                f_jsonl.write(json.dumps(raw_obj, ensure_ascii=False) + "\n")

                scraped += 1
                ext = hit.get("externalID")
                if ext is not None:
                    unique_external.add(str(ext))

            time.sleep(args.sleep)

    print("DONE")
    print("rows written:", scraped)
    print("unique externalID:", len(unique_external))
    if expected_nb_hits is not None:
        try:
            exp = int(expected_nb_hits)
            print("expected nbHits:", exp, " | delta:", exp - len(unique_external))
        except Exception:
            print("expected nbHits:", expected_nb_hits)

if __name__ == "__main__":
    main()
