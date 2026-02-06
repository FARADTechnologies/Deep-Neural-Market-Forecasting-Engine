import pandas as pd
import folium
from folium.plugins import MarkerCluster
import os

# 1. Veri Yükleme
csv_path = "df_clean.csv"
if not os.path.exists(csv_path):
    # visualize klasöründen çalıştırılırsa bir üst dizine bak
    csv_path = os.path.join("..", csv_path)
    if not os.path.exists(csv_path):
        print(f"Hata: {csv_path} bulunamadı.")
        exit()

print(f"Veri yükleniyor: {csv_path}")
df = pd.read_csv(csv_path)

# 2. Harita Oluşturma (Riyad merkezli)
riyadh_coords = [24.7136, 46.6753]
m = folium.Map(location=riyadh_coords, zoom_start=11, tiles="OpenStreetMap")

# Kümeleme (MarkerCluster) ekle
marker_cluster = MarkerCluster().add_to(m)

# 3. İlanları Haritaya Ekle
print("İlanlar haritaya işleniyor...")

def get_color(price):
    if price < 600000:
        return "green"    # Ekonomik
    elif price < 1200000:
        return "orange"   # Orta segment
    else:
        return "red"      # Lüks / Pahalı

for idx, row in df.iterrows():
    # Geçersiz koordinat kontrolü
    if pd.isna(row['lat']) or pd.isna(row['long']):
        continue
        
    # Popup içeriği (HTML formatında)
    bayut_link = f"https://www.bayut.sa/en/property/details-{row['id']}.html"
    popup_text = f"""
    <div style="font-family: Arial; width: 200px;">
        <h4>{row['name']}</h4>
        <hr>
        <b>Fiyat:</b> {row['price']:,.0f} SAR<br>
        <b>Alan:</b> {row['area_m2']} m²<br>
        <b>Oda:</b> {row['rooms']}<br>
        <br>
        <a href="{bayut_link}" target="_blank" style="color: blue; text-decoration: underline;">İlanı Gör (Bayut)</a>
    </div>
    """
    
    # Marker ekle
    folium.CircleMarker(
        location=[row['lat'], row['long']],
        radius=7,
        popup=folium.Popup(popup_text, max_width=250),
        color=get_color(row['price']),
        fill=True,
        fill_color=get_color(row['price']),
        fill_opacity=0.6,
        weight=2
    ).add_to(marker_cluster)

# 4. Kaydet
output_dir = "visualize"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_path = os.path.join(output_dir, "riyadh_real_estate_map_v2.html")
m.save(output_path)

print(f"✅ Başarılı: Harita kaydedildi -> {output_path}")
print(f"Toplam listelenen ilan sayısı: {len(df)}")
