import pandas as pd
import numpy as np
import os

# --- AYARLAR ---
INPUT_FILE = "final_sales_data.csv"
OUTPUT_FILE = "riyadh_jeddah_cleaned.csv"

def clean_and_analyze():
    print("VERI TEMIZLIGI VE FILTRELEME ISLEMI BASLATILIYOR...\n")

    if not os.path.exists(INPUT_FILE):
        print("HATA: CSV dosyasi bulunamadi.")
        return

    # 1. Veriyi Yukle
    df = pd.read_csv(INPUT_FILE)
    print(f"Islem Oncesi Toplam Veri Sayisi: {len(df)}")

    # ---------------------------------------------------------
    # GOREV 1: Sadece Jeddah ve Riyadh Sehirlerini Tut
    # ---------------------------------------------------------
    target_cities = ['Riyadh', 'Jeddah']
    
    # Sehir filtresi
    df = df[df['city'].isin(target_cities)].copy()
    
    print(f"Sehir Filtresi Sonrasi (Riyadh & Jeddah) Veri Sayisi: {len(df)}")

    # ---------------------------------------------------------
    # GOREV 3 & 4: Sayisal Donusumler ve Ondalik Hatasi Duzeltme
    # ---------------------------------------------------------
    # Lat/Long, Price, Area_m2 gibi sutunlari sayiya ceviriyoruz.
    # 12.50 degerinin 1250 olarak okunmasini engellemek icin once virgulleri noktaya ceviriyoruz.
    
    numeric_cols = ['price', 'Area_m2', 'lat', 'long', 'rooms', 'bath']
    
    for col in numeric_cols:
        if col in df.columns:
            # Once veriyi string'e cevirip virgulleri noktayla degistiriyoruz
            df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
            
            # Sayisal degere donusturuyoruz (hatali veriler NaN olur)
            df[col] = pd.to_numeric(df[col], errors='coerce')

    print("Sayisal sutunlar (Lat, Long, Price, m2) formatlandi.")

    # ---------------------------------------------------------
    # GOREV 2: Agency (Emlakci) vs Developer (Insaatci) Farki
    # ---------------------------------------------------------
    print("\n" + "="*40)
    print("AGENCY vs DEVELOPER ANALIZI")
    print("="*40)
    
    if 'type' in df.columns:
        print("Veri Setindeki Tur Dagilimi:")
        print(df['type'].value_counts())
        
        print("\nTur Bazinda Ortalama Fiyatlar:")
        print(df.groupby('type')['price'].mean().map('{:,.0f}'.format))
    else:
        print("UYARI: 'type' sutunu bulunamadi!")

    # ---------------------------------------------------------
    # GOREV 5: Furnished/Unfurnished & Completed/Off-plan Farki
    # ---------------------------------------------------------
    print("\n" + "="*40)
    print("ESYA VE INSAAT DURUMU ANALIZI")
    print("="*40)

    # A) Esya Durumu (Furnished)
    if 'furnished' in df.columns:
        print("\n--- Furnished (Esya) Durumu ---")
        print(df['furnished'].value_counts())
        print("Ortalama Fiyat:")
        print(df.groupby('furnished')['price'].mean().map('{:,.0f}'.format))

    # B) Insaat Durumu (Completion Status)
    if 'completion_status' in df.columns:
        print("\n--- Completion (Insaat) Durumu ---")
        print(df['completion_status'].value_counts())
        print("Ortalama Fiyat:")
        print(df.groupby('completion_status')['price'].mean().map('{:,.0f}'.format))

    # ---------------------------------------------------------
    # KAYDETME
    # ---------------------------------------------------------
    print("\n" + "-"*40)
    # Kritik verileri eksik olan satirlari temizle (Fiyat, Lat, Long)
    df_clean = df.dropna(subset=['price', 'lat', 'long'])
    
    print(f"Temizlenen veri kaydediliyor... (Son Satir Sayisi: {len(df_clean)})")
    df_clean.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print(f"Dosya Olusturuldu: {OUTPUT_FILE}")

if __name__ == "__main__":
    clean_and_analyze()