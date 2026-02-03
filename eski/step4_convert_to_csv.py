import pandas as pd
import json
import os

# --- AYARLAR ---
INPUT_FILE = "parsed_listings_sales_turbo.json"
OUTPUT_FILE = "final_sales_data.csv"

def json_to_csv_pandas():
    print(f"📂 '{INPUT_FILE}' okunuyor...")

    # 1. Dosya var mı kontrol et
    if not os.path.exists(INPUT_FILE):
        print("❌ HATA: JSON dosyası bulunamadı! Önce scrape işlemini yapmalısın.")
        return

    # 2. JSON'ı Yükle
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"📊 {len(data)} adet veri hafızaya alındı. Tabloya dönüştürülüyor...")

    # 3. Pandas DataFrame'e çevir
    df = pd.read_json(INPUT_FILE)

    # 4. TEMİZLİK: Liste olan sütunları düzelt (Excel'de ['a','b'] görünmesin)
    # Özellikle 'Amenities' ve 'all_pictures' gibi alanlar liste gelir.
    # Bunları "Klima, Havuz, Otopark" şekline çeviriyoruz.
    
    def list_to_string(val):
        if isinstance(val, list):
            return ", ".join(map(str, val)) # Virgülle birleştir
        return val

    # Tüm veri setine uygula (Otomatik algılar)
    df = df.applymap(list_to_string)

    print("💾 CSV olarak kaydediliyor...")

    # 5. CSV Olarak Kaydet
    # index=False -> Yanına 0,1,2 diye satır numarası eklemesin
    # encoding="utf-8-sig" -> Excel'in Arapça ve Türkçe karakterleri doğru açması için ŞART!
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print("-" * 40)
    print(f"✅ İŞLEM TAMAMLANDI!")
    print(f"📄 Dosya Adı: {OUTPUT_FILE}")
    print(f"🔢 Toplam Satır: {len(df)}")
    print(f"📏 Toplam Sütun: {len(df.columns)}")
    print("-" * 40)
    print("👉 Tavsiye: CSV dosyasını Excel ile açarken 'Veri -> Metinden/CSV'den' seçeneğini kullan.")

if __name__ == "__main__":
    json_to_csv_pandas()