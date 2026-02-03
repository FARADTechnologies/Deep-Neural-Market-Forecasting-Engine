import json

# 1. Mevcut (Senin oluşturduğun) büyük listeyi oku
input_filename = "parsed_listings.json"
output_filename = "bayut_data.jsonl"  # Uzantısı .jsonl olur

print(f"📂 '{input_filename}' dosyası okunuyor...")

try:
    with open(input_filename, "r", encoding="utf-8") as f:
        data = json.load(f) # Tüm listeyi hafızaya alır
    
    print(f"✅ {len(data)} ilan bulundu. Dönüştürülüyor...")

    # 2. Satır satır (JSON Lines) olarak yaz
    with open(output_filename, "w", encoding="utf-8") as f:
        for item in data:
            # ensure_ascii=False -> Türkçe karakterleri bozmaz
            # indent kullanmıyoruz -> Tek satır olsun diye
            json_line = json.dumps(item, ensure_ascii=False)
            f.write(json_line + "\n") # Her objeden sonra bir alt satıra geç

    print(f"🎉 BİTTİ! Dosyan hazır: {output_filename}")
    print("Artık her satırda tek bir ilan var.")

except FileNotFoundError:
    print("❌ HATA: 'parsed_listings.json' dosyası bulunamadı. İsmi doğru mu?")