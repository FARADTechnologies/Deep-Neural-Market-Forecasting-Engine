import httpx
import json

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

# DİKKAT: Filtreyi "for-sale" (Satılık) yaptık!
FILTERS = "purpose%3A%22for-sale%22%20AND%20(category.slug%3A%22apartments%22)"

def get_total_count(index_name):
    """
    Verilen indeks ismindeki toplam ilan sayısını sorar.
    """
    # hitsPerPage=0 -> Sadece sayıyı ver, veriyi indirme.
    params = f"hitsPerPage=0&page=0&filters={FILTERS}"
    payload = {
        "requests": [{"indexName": index_name, "params": params}]
    }
    
    try:
        with httpx.Client() as client:
            resp = client.post(ALGOLIA_URL, headers=HEADERS, json=payload, timeout=5)
            if resp.status_code == 200:
                return resp.json()["results"][0]["nbHits"]
            else:
                return f"Hata: {resp.status_code}"
    except Exception as e:
        return f"Bağlantı Hatası: {e}"

def main():
    print("--- SATILIK HAVUZU KONTROLÜ BAŞLIYOR ---\n")

    # 1. Eski Kullandığımız Index (Verified)
    index_eski = "bayut-sa-production-ads-verified-score-en"
    sayi_eski = get_total_count(index_eski)
    print(f"📦 ESKİ HAVUZ (Verified): {sayi_eski} ilan")

    # 2. Network'ten Bulduğun Yeni Index (City Level)
    index_yeni = "bayut-sa-production-ads-city-level-score-en"
    sayi_yeni = get_total_count(index_yeni)
    print(f"🌍 YENİ HAVUZ (City Level): {sayi_yeni} ilan")

    print("\n--------------------------------")
    
    if isinstance(sayi_yeni, int) and isinstance(sayi_eski, int):
        fark = sayi_yeni - sayi_eski
        if fark > 0:
            print(f"✅ EVET! Yeni havuzda {fark} adet daha fazla ilan var.")
            print("Ana kodda 'city-level-score' kullanmalısın.")
        elif fark == 0:
            print("⚠️ Sayılar eşit. İkisini de kullanabilirsin ama yenisi daha garantidir.")
        else:
            print("❓ İlginç. Eski havuzda daha çok ilan görünüyor.")

if __name__ == "__main__":
    main()