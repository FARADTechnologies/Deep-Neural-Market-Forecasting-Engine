import httpx
import json

# --- 1. AYARLAR (CONFIGURATION) ---
# Burası "Kimiz ve Nereye Gidiyoruz?" kısmı.

# Hedef Adres (Algolia API Endpoint)
ALGOLIA_URL = "https://ll8iz711cs-dsn.algolia.net/1/indexes/*/queries"

# Kimlik Bilgileri (Tarayıcıdan kopyalanan sabit anahtarlar)
# Bu bilgiler sunucuya "Biz yetkili bir istemciyiz" der.
HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "x-algolia-agent": "strat-bayut-sa-production-frontend-client/6e8d90f0ce92a83fc926add897e80f9879615b81",
    "x-algolia-api-key": "5b970b39b22a4ff1b99e5167696eef3f",
    "x-algolia-application-id": "LL8IZ711CS",
    "referer": "https://www.bayut.sa/",  # Geldiğimiz yer (Önemli!)
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" # Tarayıcı taklidi
}

# --- 2. İSTEK PARAMETRELERİ (PAYLOAD) ---
# Burası "Ne İstiyoruz?" kısmı.

# Aradığımız filtreler: Kiralık (for-rent) VE Daire (apartments)
# Bu string URL-Encoded formatındadır.
FILTERS = "purpose%3A%22for-rent%22%20AND%20(category.slug%3A%22apartments%22)"

def get_listings_page():
    """
    Siteye bağlanır ve ilanların olduğu ham sayfayı (JSON) çeker.
    """
    
    # Algolia'ya göndereceğimiz parametreler
    # hitsPerPage=25 -> Sayfa başına 25 ilan istiyoruz.
    params_string = f"hitsPerPage=25&page=1&filters={FILTERS}"

    # Algolia POST isteği gövdesi (Body)
    payload = {
        "requests": [
            {
                "indexName": "bayut-sa-production-ads-verified-score-en", # Hangi veritabanı?
                "params": params_string
            }
        ]
    }

    print("📡 Sunucuya istek gönderiliyor...")

    # httpx ile POST isteği atıyoruz
    # (requests kütüphanesinin daha modern halidir)
    with httpx.Client() as client:
        response = client.post(
            ALGOLIA_URL,
            headers=HEADERS,
            json=payload,
            timeout=10 # 10 saniye içinde cevap gelmezse hata ver
        )

    # --- 3. SONUÇ KONTROLÜ ---
    if response.status_code == 200:
        print("✅ BAŞARILI! Sunucu cevap verdi.")
        
        # Gelen veriyi JSON formatına çevirelim
        data = response.json()
        
        # İçindeki ilan listesine ulaşalım (Algolia yapısı standarttır)
        # results -> 0. eleman -> hits (ilanlar burada)
        hits = data["results"][0]["hits"]
        total_pages = data["results"][0]["nbPages"]
        
        print(f"📄 Toplam Sayfa Sayısı: {total_pages}")
        print(f"🏠 Bu sayfada bulunan ilan sayısı: {len(hits)}")
        
        # İlk ilanın sadece başlığını yazdıralım ki doğru yerde miyiz görelim
        if hits:
            print(f"🔎 Örnek İlan Başlığı: {hits[0].get('title')}")
            
        return hits # İlan listesini döndürür
        
    else:
        print(f"❌ HATA! Durum Kodu: {response.status_code}")
        print("Cevap:", response.text)
        return []

# --- 4. ÇALIŞTIRMA ---
if __name__ == "__main__":
    listings = get_listings_page()
    # Şu an elimizde "listings" adında ham bir liste var.
    # Henüz detaylarına girmedik.