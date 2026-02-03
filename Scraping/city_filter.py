import pandas as pd
import os

# --- AYARLAR ---
GIRIS_DOSYASI = "final_sales_data.csv"
CIKIS_DOSYASI = "final_sales_data_CLEANED.csv" # Temizlenmiş hali buraya kaydedilecek

def sehirleri_filtrele():
    print("🧹 ŞEHİR FİLTRELEME İŞLEMİ BAŞLIYOR...\n")

    # 1. Dosya var mı kontrol et
    if not os.path.exists(GIRIS_DOSYASI):
        print(f"❌ HATA: '{GIRIS_DOSYASI}' dosyası bulunamadı!")
        return

    # 2. Veriyi Oku
    df = pd.read_csv(GIRIS_DOSYASI)
    ilk_sayi = len(df)
    print(f"📥 Toplam İlan Sayısı (Başlangıç): {ilk_sayi}")

    # 3. Hangi şehirler kalacak?
    hedef_sehirler = ["Riyadh", "Jeddah"]

    # 4. Filtreleme İşlemi (Pandas Sihiri)
    # Mantık: Şehri, hedef_sehirler listesinde OLANLARI al.
    df_clean = df[df['city'].isin(hedef_sehirler)]

    son_sayi = len(df_clean)
    silinen_sayi = ilk_sayi - son_sayi

    print("-" * 30)
    print(f"🏙️  Kalan Şehirler: {hedef_sehirler}")
    print(f"✅ Kalan İlan Sayısı: {son_sayi}")
    print(f"🗑️  Silinen (Diğer Şehirler): {silinen_sayi}")
    print("-" * 30)

    # 5. Yeni CSV olarak kaydet
    df_clean.to_csv(CIKIS_DOSYASI, index=False, encoding="utf-8-sig")
    
    print(f"💾 Temiz dosya kaydedildi: {CIKIS_DOSYASI}")
    print("👉 Artık analizlerini bu yeni dosya üzerinde yapabilirsin.")

if __name__ == "__main__":
    sehirleri_filtrele()