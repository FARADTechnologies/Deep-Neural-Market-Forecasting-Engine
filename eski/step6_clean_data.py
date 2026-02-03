import pandas as pd
import os

# --- AYARLAR ---
INPUT_FILE = "final_sales_data.csv"       # Kirli Veri
OUTPUT_FILE = "cleaned_sales_data.csv"    # Temiz Veri

def clean_data():
    print(f" TEMİZLİK OPERASYONU BAŞLIYOR: '{INPUT_FILE}' okunuyor...\n")
    
    if not os.path.exists(INPUT_FILE):
        print(" Dosya yok!")
        return

    # 1. Yükle
    df = pd.read_csv(INPUT_FILE)
    print(f"📦 Başlangıç Veri Sayısı: {len(df)}")

    # --- ADIM 1: TEKRAR EDENLERİ SİL (DUPLICATES) ---
    # Bazen Algolia aynı ilanı sayfa geçişlerinde 2 kere verebilir.
    # 'id' sütunu aynı olanları siler.
    df.drop_duplicates(subset=["id"], inplace=True)
    print(f"    Tekrar edenler silindi. Kalan: {len(df)}")

    # --- ADIM 2: MANTIKSIZ FİYATLARI SİL ---
    # Kural: Fiyatı 50.000 SAR'dan az, 100 Milyon SAR'dan çok olanları at.
    # (1 SAR'lık hatalar burada gider)
    
    # Önce sayıya çevirelim (Hatalı karakter varsa NaN olsun)
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    
    df = df[ (df["price"] > 50000) & (df["price"] < 100000000) ]
    print(f"    Mantıksız fiyatlar (1 SAR vb.) silindi. Kalan: {len(df)}")

    # --- ADIM 3: MANTIKSIZ METREKARELERİ SİL ---
    # Kural: 20 m2'den küçük ev olmaz. (Bazıları 0 veya 1 girilmiş olabilir)
    df["Area_m2"] = pd.to_numeric(df["Area_m2"], errors="coerce")
    df = df[df["Area_m2"] > 20]
    print(f"    Hatalı m² (20 m² altı) silindi. Kalan: {len(df)}")

    # --- ADIM 4: ŞEHİR FİLTRESİ (OPSİYONEL) ---
    # Senin analizinde "North Jeddah" çıkmıştı. Eğer sadece Riyad çalışacaksan:
    # (Şimdilik kapatıyorum, sadece Riyad kalsın istersen başındaki # işaretini kaldır)
    
    # df = df[df["city"].str.contains("Riyadh", na=False, case=False)]
    # print(f"   ✅ Sadece Riyad verileri tutuldu. Kalan: {len(df)}")

    # --- ADIM 5: TEMİZ VERİYİ KAYDET ---
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    
    print("-" * 40)
    print(f" TEMİZLİK BİTTİ! Dosya oluşturuldu: {OUTPUT_FILE}")
    print(f"Toplam atılan çöp veri: {22791 - len(df)} adet")

if __name__ == "__main__":
    clean_data()