import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- AYARLAR ---
# DİKKAT: Artık temizlenmiş veriyi okuyoruz
CSV_FILE = "cleaned_sales_data.csv"

def visualize_clean_data():
    print("🎨 Temiz veri grafikleri hazırlanıyor...")
    
    if not os.path.exists(CSV_FILE):
        print("❌ HATA: 'cleaned_sales_data.csv' yok! Önce step6_clean_data.py çalıştır.")
        return

    # 1. Veriyi Oku
    df = pd.read_csv(CSV_FILE)
    
    # Not: step6'da zaten temizledik ama grafik görünümü için 
    # yine de çok aşırı uçuk fiyatları (50 Milyon üstü gibi) grafikte göstermeyebiliriz.
    # Şimdilik olduğu gibi alıyoruz çünkü step6 zaten temizledi.
    
    # Grafik Stili
    sns.set_style("whitegrid")

    # --- GRAFİK 1: FİYAT DAĞILIMI (TEMİZ) ---
    plt.figure(figsize=(10, 6))
    sns.histplot(df["price"], bins=50, kde=True, color="green") # Rengi yeşil yaptım fark edilsin diye
    plt.title("TEMİZ - Satılık Daire Fiyat Dağılımı", fontsize=15)
    plt.xlabel("Fiyat (SAR)")
    plt.ylabel("İlan Sayısı")
    plt.ticklabel_format(style='plain', axis='x')
    
    # Dosya adının başına 'TEMIZ_' ekledik
    plt.savefig("TEMIZ_grafik_1_fiyat_dagilimi.png")
    print("✅ 1. Grafik kaydedildi: TEMIZ_grafik_1_fiyat_dagilimi.png")

    # --- GRAFİK 2: BÖLGE DAĞILIMI (TEMİZ) ---
    plt.figure(figsize=(10, 6))
    top_cities = df["region"].value_counts().head(10)
    sns.barplot(x=top_cities.values, y=top_cities.index, hue=top_cities.index, palette="viridis", legend=False)
    plt.title("TEMİZ - En Çok İlan Olan 10 Bölge", fontsize=15)
    plt.xlabel("İlan Sayısı")
    plt.savefig("TEMIZ_grafik_2_bolge_dagilimi.png")
    print("✅ 2. Grafik kaydedildi: TEMIZ_grafik_2_bolge_dagilimi.png")

    # --- GRAFİK 3: ODA FİYAT (TEMİZ) ---
    plt.figure(figsize=(10, 6))
    df_rooms = df[df["rooms"].between(1, 5)]
    sns.boxplot(x="rooms", y="price", data=df_rooms, hue="rooms", palette="Set2", legend=False)
    plt.title("TEMİZ - Oda Sayısına Göre Fiyat", fontsize=15)
    plt.xlabel("Oda Sayısı")
    plt.ylabel("Fiyat (SAR)")
    plt.ticklabel_format(style='plain', axis='y')
    plt.savefig("TEMIZ_grafik_3_oda_fiyat.png")
    print("✅ 3. Grafik kaydedildi: TEMIZ_grafik_3_oda_fiyat.png")
    
    print("\n🎉 KARŞILAŞTIRMAYA HAZIR! Klasöründeki eski ve yeni resimlere bakabilirsin.")

if __name__ == "__main__":
    visualize_clean_data()