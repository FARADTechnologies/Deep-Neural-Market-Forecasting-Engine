import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- AYARLAR ---
CSV_FILE = "final_sales_data.csv"

def visualize_data():
    print(" Grafikler hazırlanıyor...")
    
    # 1. Veriyi Oku ve Temizle
    df = pd.read_csv(CSV_FILE)
    
    # Hatalı verileri (1 Riyal gibi) temizleyelim
    # Fiyatı 50.000 SAR'dan küçük olanları atıyoruz (Mantiklı sınır)
    df = df[df["price"] > 50000].copy() 
    
    # Çok uçuk fiyatları (5 Milyon üstü) grafik düzgün görünsün diye şimdilik filtreleyelim
    # (Analizden atmıyoruz, sadece grafikte 'zoom' yapıyoruz)
    df_plot = df[df["price"] < 5000000].copy()

    # Grafik Stili
    sns.set_style("whitegrid")

    # --- GRAFİK 1: FİYAT DAĞILIMI (HISTOGRAM) ---
    plt.figure(figsize=(10, 6))
    sns.histplot(df_plot["price"], bins=50, kde=True, color="skyblue")
    plt.title("Satılık Daire Fiyat Dağılımı (5 Milyon SAR altı)", fontsize=15)
    plt.xlabel("Fiyat (SAR)")
    plt.ylabel("İlan Sayısı")
    plt.ticklabel_format(style='plain', axis='x') # Bilimsel gösterimi (1e6) kapat
    plt.savefig("grafik_1_fiyat_dagilimi.png")
    print("✅ Grafik 1 kaydedildi: grafik_1_fiyat_dagilimi.png")

    # --- GRAFİK 2: ŞEHİRLERE GÖRE İLAN SAYISI ---
    plt.figure(figsize=(10, 6))
    # En çok ilanı olan ilk 10 şehri/bölgeyi al
    top_cities = df["region"].value_counts().head(10)
    sns.barplot(x=top_cities.values, y=top_cities.index, hue=top_cities.index, palette="viridis", legend=False)
    plt.title("En Çok İlan Olan 10 Bölge", fontsize=15)
    plt.xlabel("İlan Sayısı")
    plt.savefig("grafik_2_bolge_dagilimi.png")
    print(" Grafik 2 kaydedildi: grafik_2_bolge_dagilimi.png")

    # --- GRAFİK 3: ODA SAYISINA GÖRE FİYAT (BOX PLOT) ---
    plt.figure(figsize=(10, 6))
    # Oda sayısı 1 ile 5 arasında olanlara bakalım
    df_rooms = df_plot[df_plot["rooms"].between(1, 5)]
    sns.boxplot(x="rooms", y="price", data=df_rooms, hue="rooms", palette="Set2", legend=False)
    plt.title("Oda Sayısına Göre Fiyat Değişimi", fontsize=15)
    plt.xlabel("Oda Sayısı")
    plt.ylabel("Fiyat (SAR)")
    plt.ticklabel_format(style='plain', axis='y')
    plt.savefig("grafik_3_oda_fiyat.png")
    print("✅ Grafik 3 kaydedildi: grafik_3_oda_fiyat.png")
    
    print("\n Tüm grafikler oluşturuldu! Klasörünü kontrol et.")

if __name__ == "__main__":
    visualize_data()