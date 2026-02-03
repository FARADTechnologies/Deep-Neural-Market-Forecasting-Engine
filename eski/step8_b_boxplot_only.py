import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- AYARLAR ---
FILE_DIRTY = "final_sales_data.csv"      # Kirli Veri
FILE_CLEAN = "cleaned_sales_data.csv"    # Temiz Veri

def show_boxplot():
    print("📦 BOX PLOT (Kutu Grafiği) Hazırlanıyor...\n")
    
    # 1. Dosyaları Yükle
    if not os.path.exists(FILE_DIRTY) or not os.path.exists(FILE_CLEAN):
        print("❌ Dosyalar eksik!")
        return

    df_dirty = pd.read_csv(FILE_DIRTY)
    df_clean = pd.read_csv(FILE_CLEAN)

    # Veri tiplerini onar
    df_dirty["price"] = pd.to_numeric(df_dirty["price"], errors="coerce")
    df_clean["price"] = pd.to_numeric(df_clean["price"], errors="coerce")

    # 2. Etiketle ve Birleştir
    df_dirty["Veri Seti"] = "1. Kirli Veri (Eski)"
    df_clean["Veri Seti"] = "2. Temiz Veri (Yeni)"
    
    # Sadece grafik için birleştiriyoruz
    df_all = pd.concat([df_dirty, df_clean])

    # 3. GRAFİK AYARLARI
    plt.figure(figsize=(12, 8))
    sns.set_style("whitegrid")

    # --- BOX PLOT ÇİZİMİ ---
    # showfliers=True -> O minik noktaları (Aykırı değerleri) göster demektir.
    sns.boxplot(
        data=df_all, 
        x="Veri Seti", 
        y="price", 
        palette={"1. Kirli Veri (Eski)": "#e74c3c", "2. Temiz Veri (Yeni)": "#2ecc71"},
        width=0.5,
        linewidth=1.5
    )

    # 4. ZOOM AYARI (Çok Önemli)
    # Kirli veride 100 Milyonluk evler olduğu için grafik bozulmasın diye
    # Kamerayı 0 ile 5 Milyon arasına odaklıyoruz.
    plt.ylim(-100000, 5000000) 

    plt.title("KİRLİ vs TEMİZ VERİ: Fiyat Dağılımı ve Aykırı Değerler", fontsize=16)
    plt.ylabel("Fiyat (SAR)", fontsize=12)
    plt.xlabel("", fontsize=12)
    
    # Y eksenindeki sayıları düzelt (1e6 yerine 1,000,000 yazsın)
    plt.ticklabel_format(style='plain', axis='y')

    # Kaydet
    filename = "KARSILASTIRMA_Sadece_BoxPlot.png"
    plt.savefig(filename)
    print(f"✅ Grafik kaydedildi: {filename}")
    print("👉 Bu grafiği ekibine göster!")

if __name__ == "__main__":
    show_boxplot()