# 📋 Proje Yapılacaklar Listesi

## 🎯 Ana Hedefler
- [ ] **Odak Şehirler:** Veri setini sadece **Jeddah** ve **Riyadh** şehirlerine odakla ve diğerlerini filtrele.
- [ ] **Acente vs Geliştirici:** `Agency` ve `Developer` arasındaki farkları analiz et (Search agency ile developer difference).

## 🧹 Veri Temizliği (Data Cleaning)
- [x] **Görsel Format Sorunları:** Kullanıcı tarafındaki sayı gösterim hatası (12.50 vs 1250) incelendi (Scientific Notation düzeltmesi ile çözüldü).
- [x] **Veri Tipi Ayrıştırması:** 
    - [x] Sütunları `Numerical` ve `Categorical` olarak ayır.
    - [x] `ID`, `Building_No`, `Postal_Code`, `Additional_No`, `Deed_Number` sütunlarını **String** formatına çevir.
    - [x] `Lat` ve `Long` sütunlarını sayısal (float) formata çevir veya kategorik durumunu düzelt.
- [ ] **Eksik Veri (Missing Values) Analizi:**
    - [ ] Her sütundaki `null` sayısını belirle.
    - [ ] Kategorik değişkenlerdeki eksik verileri analiz et.
    - [ ] Sayısal değişkenlerdeki eksik verileri analiz et.
- [x] **Yinelenen Veriler (Duplicates):**
    - [x] `ID` bazında tekrar eden kayıtları sil.
    - [ ] `Deed_Number` (Tapu No) kontrollerini tamamla.

## ⚙️ Feature Engineering (Özellik Mühendisliği)
- [ ] **H3 Index:** `Lat` ve `Long` verilerini kullanarak Uber H3 coğrafi indekslerini oluştur.
- [ ] **Tarih İşlemleri:**
    - [ ] Tarih sütunlarının formatını standartlaştır (Date type).
    - [ ] `Yıl` ve `Ay` bilgilerini ayırarak yeni sütunlar oluştur.
- [ ] **Kategori Analizi:**
    - [ ] `Unfurnished` / `Furnished` / `Completed` / `Uncompleted` ayrımlarını ve farklarını netleştir.
    - [ ] Kategorik sütunlardaki `Unique` (benzersiz) değer sayılarını çıkar.

## 📝 Dokümantasyon ve Organizasyon
- [ ] **Sütun Listeleri:** Silinen ve saklanan sütunları not et, nedenlerini açıkla.
- [ ] **Kod Düzeni:** Scraping ve Analiz kodlarını klasörlere ayır.
