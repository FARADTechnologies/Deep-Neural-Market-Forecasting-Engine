import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Veriyi Yükle
# (Eğer temizlediğin dosyayı kullanmak istersen ismini 'final_sales_data_CLEANED.csv' yap)
df = pd.read_csv("final_sales_data.csv", encoding="utf-8-sig")

# 2. Şehirleri Say
sehir_sayilari = df['city'].value_counts()

print("📊 ŞEHİR BAŞINA İLAN SAYILARI:")
print("-" * 30)
print(sehir_sayilari)

# En çok ilanı olan şehri bul
lider_sehir = sehir_sayilari.idxmax()
lider_adet = sehir_sayilari.max()
print(f"\n🏆 ŞAMPİYON: {lider_sehir} ({lider_adet} ilan ile)")

# 3. GRAFİK ÇİZ (Görselleştirme)
plt.figure(figsize=(10, 6)) # Resmin boyutu
sns.barplot(x=sehir_sayilari.index, y=sehir_sayilari.values, palette="viridis")

plt.title("Hangi Şehirde Kaç İlan Var?", fontsize=16)
plt.xlabel("Şehirler", fontsize=12)
plt.ylabel("İlan Sayısı", fontsize=12)
plt.xticks(rotation=45) # Şehir isimleri sığmazsa yan çevir
plt.grid(axis='y', linestyle='--', alpha=0.7) # Arka plana çizgi ekle

plt.show()