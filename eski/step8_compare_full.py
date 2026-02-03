import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- AYARLAR ---
FILE_DIRTY = "final_sales_data.csv"      # Kirli Veri
FILE_CLEAN = "cleaned_sales_data.csv"    # Temiz Veri

def compare_data():
    print("⚖️  KARŞILAŞTIRMA ANALİZİ BAŞLIYOR...\n")
    
    # 1. Verileri Yükle
    if not os.path.exists(FILE_DIRTY) or not os.path.exists(FILE_CLEAN):
        print("❌ Dosyalar eksik! Önce step2 ve step6 kodlarını çalıştır.")
        return

    df_dirty = pd.read_csv(FILE_DIRTY)
    df_clean = pd.read_csv(FILE_CLEAN)

    # Veri tiplerini düzelt
    df_dirty["price"] = pd.to_numeric(df_dirty["price"], errors="coerce")
    df_clean["price"] = pd.to_numeric(df_clean["price"], errors="coerce")

    # 2. Etiketleme (Hangisi kirli hangisi temiz bilinsin)
    df_dirty["Durum"] = "Kirli Veri (Eski)"
    df_clean["Durum"] = "Temiz Veri (Yeni)"

    # İkisini birleştiriyoruz (Tek grafik için)
    df_all = pd.concat([df_dirty, df_clean])

    # --- RAKAMSAL RAPOR (ACCURATE NUMBERS) ---
    print("📊 RAKAMSAL KARŞILAŞTIRMA TABLOSU")
    print("=" * 60)
    print(f"{'METRİK':<20} | {'KİRLİ VERİ':<15} | {'TEMİZ VERİ':<15}")
    print("-" * 60)
    
    stats = {
        "İlan Sayısı": (len(df_dirty), len(df_clean)),
        "Min Fiyat": (df_dirty["price"].min(), df_clean["price"].min()),
        "Max Fiyat": (df_dirty["price"].max(), df_clean["price"].max()),
        "Ortalama": (df_dirty["price"].mean(), df_clean["price"].mean()),
        "Medyan": (df_dirty["price"].median(), df_clean["price"].median())
    }

    for key, (val1, val2) in stats.items():
        print(f"{key:<20} | {val1:,.0f} SAR".ljust(38) + f"| {val2:,.0f} SAR")
    print("=" * 60 + "\n")

    # --- GRAFİK AYARLARI ---
    sns.set_style("whitegrid")
    
    # Görsel netliği için çok uçuk fiyatları grafikte 'Görünür Alan' dışı bırakalım
    # (Analizden atmıyoruz, sadece grafikte oraya zoom yapıyoruz)
    LIMIT_FIYAT = 5000000 # 5 Milyon SAR'a kadar olan kısmı odakla

    # --- GRAFİK 1: İKİ EĞRİLİ KARŞILAŞTIRMA (KDE PLOT) ---
    plt.figure(figsize=(12, 7))
    
    # KDE Plot: İki ayrı eğri çizer
    sns.kdeplot(data=df_dirty, x="price", color="red", label="Kirli Veri Eğrisi", fill=True, alpha=0.3, clip=(0, LIMIT_FIYAT))
    sns.kdeplot(data=df_clean, x="price", color="green", label="Temiz Veri Eğrisi", fill=True, alpha=0.3, clip=(0, LIMIT_FIYAT))
    
    plt.xlim(0, LIMIT_FIYAT) # X eksenini 5 Milyona sabitle
    plt.title("DETAYLI KARŞILAŞTIRMA: Fiyat Dağılım Eğrileri", fontsize=16)
    plt.xlabel("Fiyat (SAR)", fontsize=12)
    plt.ylabel("Yoğunluk", fontsize=12)
    plt.legend()
    plt.ticklabel_format(style='plain', axis='x') # 1e6 yazısını kaldır
    
    plt.savefig("KARSILASTIRMA_Egri_Grafigi.png")
    print("✅ 1. Grafik (Eğriler) kaydedildi: KARSILASTIRMA_Egri_Grafigi.png")

    # --- GRAFİK 2: YAN YANA KUTU GRAFİĞİ (BOXPLOT) ---
    plt.figure(figsize=(12, 7))
    
    sns.boxplot(data=df_all, x="Durum", y="price", palette={"Kirli Veri (Eski)": "salmon", "Temiz Veri (Yeni)": "lightgreen"})
    
    plt.ylim(0, LIMIT_FIYAT) # Y eksenini sabitle
    plt.title("Fiyat Aralıklarının Yan Yana Karşılaştırması", fontsize=16)
    plt.ylabel("Fiyat (SAR)")
    plt.ticklabel_format(style='plain', axis='y')
    
    plt.savefig("KARSILASTIRMA_Kutu_Grafigi.png")
    print("✅ 2. Grafik (Kutular) kaydedildi: KARSILASTIRMA_Kutu_Grafigi.png")
    
    print("\n🎉 İşlem Tamam! Grafikleri açıp farkı inceleyebilirsin.")

if __name__ == "__main__":
    compare_data()