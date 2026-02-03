import pandas as pd

# --- AYARLAR ---
CSV_FILE = "final_sales_data.csv"

def analyze_data():
    print(f" '{CSV_FILE}' dosyası yükleniyor...\n")
    
    # 1. Veriyi Oku
    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        print(" Dosya bulunamadı! Önce CSV oluşturmalısın.")
        return

    # --- A) TEMİZLİK & TİP DÖNÜŞÜMÜ ---
    
    # Tekrar eden ID'leri sil (Aynı ilan 2 kere çekildiyse)
    initial_count = len(df)
    df.drop_duplicates(subset=["id"], inplace=True)
    print(f" Temizlik: {initial_count - len(df)} adet tekrar eden satır silindi.")
    
    # 'price' ve 'Area_m2' sayısal mı emin olalım (Hataları NaN yapar)
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["Area_m2"] = pd.to_numeric(df["Area_m2"], errors="coerce")
    
    # Fiyatı veya Alanı olmayan/hatalı olanları çıkaralım
    df_clean = df.dropna(subset=["price", "Area_m2"]).copy()
    
    print("-" * 50)
    print(f" ANALİZE HAZIR VERİ SAYISI: {len(df_clean)}")
    print("-" * 50)

    # --- B) TEMEL İSTATİSTİKLER ---
    
    en_ucuz = df_clean["price"].min()
    en_pahali = df_clean["price"].max()
    ortalama_fiyat = df_clean["price"].mean()
    medyan_fiyat = df_clean["price"].median() # Ortalamadan daha güvenilirdir

    print(f"\n FİYAT İSTATİSTİKLERİ:")
    print(f"    En Ucuz Daire:  {en_ucuz:,.0f} SAR")
    print(f"    En Pahalı Daire: {en_pahali:,.0f} SAR")
    print(f"    Ortalama Fiyat:  {ortalama_fiyat:,.0f} SAR")
    print(f"    Medyan Fiyat:    {medyan_fiyat:,.0f} SAR")

    # --- C) BÖLGESEL ANALİZ ---
    
    print(f"\n EN ÇOK İLAN OLAN 5 BÖLGE (Region):")
    if "region" in df_clean.columns:
        print(df_clean["region"].value_counts().head(5))
    else:
        print("   (Region sütunu bulunamadı)")

    print(f"\n EN PAHALI 5 MAHALLE (Ortalama Fiyata Göre):")
    if "district" in df_clean.columns:
        # En az 10 ilanı olan mahalleleri baz alalım ki tek bir yalı ortalamayı bozmasın
        district_stats = df_clean.groupby("district")["price"].agg(["mean", "count"])
        populer_districts = district_stats[district_stats["count"] > 10]
        print(populer_districts.sort_values(by="mean", ascending=False).head(5))

    # --- D) METREKARE ANALİZİ ---
    print(f"\n METREKARE BAŞINA FİYAT:")
    df_clean["price_per_m2"] = df_clean["price"] / df_clean["Area_m2"]
    avg_m2_price = df_clean["price_per_m2"].mean()
    print(f"    Riyad Geneli m² Birim Fiyatı: {avg_m2_price:,.0f} SAR/m²")

if __name__ == "__main__":
    analyze_data()