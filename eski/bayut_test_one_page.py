import httpx
import json

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

def main():
    page = 0
    hits_per_page = 5  # şimdilik 5 test

    # cURL'de kullanılan filtre: for-rent + furnished + apartments
    params_str = (
        f"page={page}"
        f"&hitsPerPage={hits_per_page}"
        f"&query="
        f"&attributesToRetrieve=*"
        f"&filters=purpose%3A%22for-rent%22%20AND%20furnishingStatus%3A%22furnished%22%20AND%20(category.slug%3A%22apartments%22)"
    )

    payload = {"requests": [{"indexName": INDEX_NAME, "params": params_str}]}

    r = httpx.post(URL, params=PARAMS, headers=HEADERS, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()

    res0 = data["results"][0]
    hits = res0["hits"]

    nb_pages = res0.get("nbPages")
    nb_hits = res0.get("nbHits")  # varsa eksiksizlik kontrolünde kullanacağız

    print("OK")
    print("hits:", len(hits))
    print("nbPages:", nb_pages)
    print("nbHits:", nb_hits)

    # Ekibe atmak için "text/ham json" örneği: ilk sayfanın hits'lerini dosyaya yaz
    with open("sample_hits.json", "w", encoding="utf-8") as f:
        json.dump(hits, f, ensure_ascii=False, indent=2)
    print("Wrote sample_hits.json")

    if hits:
        h0 = hits[0]
        photo_keys = [k for k in h0.keys() if "photo" in k.lower() or "image" in k.lower()]
        print("photo-like keys:", photo_keys)

        # coverPhoto ve photoIDs’i detay görmek için
        print("coverPhoto raw:", json.dumps(h0.get("coverPhoto"), ensure_ascii=False)[:1000])
        print("first 10 photoIDs:", (h0.get("photoIDs") or [])[:10])

        print("some keys:", list(h0.keys())[:30])

if __name__ == "__main__":
    main()
