import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

# 1. Veriyi Yükle
csv_path = "final_sales_data_CLEANED.csv"
if not os.path.exists(csv_path):
    print(f"Hata: {csv_path} bulunamadı.")
    exit()

df = pd.read_csv(csv_path, encoding="utf-8-sig")

# 2. Temizlik ve Filtreleme (Notebook'taki mantıkla aynı)
df_clean = df[
    (df['price'].between(2000, 500000)) & 
    (df['rooms'].between(0, 10)) & 
    (df['Area_m2'].between(20, 2000))
].copy()

# Sütun ismini düzelt (Notebook'ta 'area_m2' ve 'Area_m2' karışık kullanılmış olabilir, CSV'den kontrol)
if 'Area_m2' in df_clean.columns:
    df_clean = df_clean.rename(columns={'Area_m2': 'area_m2'})

# Birim fiyat hesapla
df_clean['price_per_m2'] = df_clean['price'] / df_clean['area_m2']

# 3. Korelasyon Matrisi
cols_to_corr = ['price', 'rooms', 'bath', 'area_m2', 'price_per_m2']
corr_matrix = df_clean[cols_to_corr].corr()

# 4. Görselleştirme ve Kaydetme
plt.figure(figsize=(12, 8))
sns.heatmap(corr_matrix, 
            annot=True, 
            fmt=".2f", 
            cmap='coolwarm', 
            center=0,
            linewidths=0.5)

plt.title("Fiyat ve Özellikler Arasındaki İlişki (Korelasyon)", fontsize=15, pad=20)

# Resmi kaydet
output_image = "korelasyon_heatmap.png"
plt.savefig(output_image, dpi=300, bbox_inches='tight')
plt.close()

print(f"Başarılı: Isı haritası '{output_image}' olarak kaydedildi.")
