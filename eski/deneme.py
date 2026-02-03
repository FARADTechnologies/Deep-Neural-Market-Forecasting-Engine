import httpx
import json
import os

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
INDEX_NAME = "bayut-sa-production-ads-verified-score-en"

# Sadece 5 tane çekmek için ayar
PARAMS = "hitsPerPage=5&page=0&filters=purpose%3A%22for-sale%22%20AND%20(category.slug%3A%22apartments%22)"

def fetch_samples():
    print("🎣 Algolia havuzundan 5 adet numune veri çekiliyor...")

    payload = {
        "requests": [{"indexName": INDEX_NAME, "params": PARAMS}]
    }

    try:
        with httpx.Client() as client:
            resp = client.post(ALGOLIA_URL, headers=HEADERS, json=payload, timeout=10)
            
        data = resp.json()
        hits = data["results"][0]["hits"]
        
        if not hits:
            print("❌ Veri gelmedi! Bir sorun olabilir.")
            return

        print(f"✅ Başarılı! {len(hits)} adet ham veri yakalandı.")

        # --- LİNK EKLEME İŞLEMİ (SENİN İSTEDİĞİN KISIM) ---
        formatted_hits = []
        for item in hits:
            slug = item.get("slug")
            # Linki oluştur
            full_link = f"https://www.bayut.sa/en/property/{slug}.html"
            
            # Sözlüğün EN BAŞINA linki koymak için yeni bir sözlük yapıyoruz
            new_item = {
                "!!!_LINKI_ACMAK_ICIN_TIKLA": full_link  # En üstte görünsün diye
            }
            # Eski ham veriyi altına ekliyoruz
            new_item.update(item)
            formatted_hits.append(new_item)

        # 1. Terminale İlk İlanın Özetini Basalım
        ilk_ilan = formatted_hits[0]
        print("\n--- ÖRNEK: İLK İLAN ---")
        print(f"🔗 LİNK: {ilk_ilan.get('!!!_LINKI_ACMAK_ICIN_TIKLA')}")
        print(f"🏠 Başlık: {ilk_ilan.get('title')}")
        print(f"💰 Fiyat: {ilk_ilan.get('price')}")
        print("-" * 40)

        # 2. Dosyaya Kaydedelim
        filename = "numune_veri.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(formatted_hits, f, ensure_ascii=False, indent=4)
            
        print(f"💾 Tüm numuneler linkleriyle beraber '{filename}' dosyasına kaydedildi.")
        print("👉 Dosyayı aç, en üstteki '!!!_LINKI_ACMAK_ICIN_TIKLA' kısmına Ctrl+Click yap.")

    except Exception as e:
        print(f"❌ Hata oluştu: {e}")

if __name__ == "__main__":
    fetch_samples()