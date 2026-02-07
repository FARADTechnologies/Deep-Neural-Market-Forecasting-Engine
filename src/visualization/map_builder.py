
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import branca.colormap as cm
import random
import os

def generate_comprehensive_map():
    # 1. Load the CLEANED data
    data_path = "data/processed/df_final_ml.csv"
    if not os.path.exists(data_path):
        data_path = "../../data/processed/df_final_ml.csv"
    
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        return
    
    df = pd.read_csv(data_path, encoding="utf-8-sig")

    # 2. Prepare Data
    # Convert bools/others
    amenity_cols = [c for c in df.columns if c.startswith('has_')]
    for c in amenity_cols:
        df[c] = df[c].fillna(0).astype(int)

    # Calculate District Stats for the District Layer
    agg_dict = {
        'price': 'mean',
        'area_m2': 'mean',
        'lat': 'mean',
        'long': 'mean',
        'id': 'count'
    }
    for c in amenity_cols:
        agg_dict[c] = 'mean'
    
    district_stats = df.groupby('district').agg(agg_dict).reset_index()
    district_stats.rename(columns={'id': 'listing_count'}, inplace=True)
    district_stats['price_per_m2'] = district_stats['price'] / district_stats['area_m2']

    # 3. Create Map
    m = folium.Map(location=[24.7136, 46.6753], zoom_start=11, tiles="CartoDB dark_matter")

    # --- LAYER 1: Individual Properties (Marker Cluster) ---
    prop_cluster = MarkerCluster(name="Bireysel İlanlar", show=True, spiderfyOnMaxZoom=True)
    
    for _, row in df.iterrows():
        # Jittering to prevent overlap
        lat_j = row['lat'] + random.uniform(-0.00008, 0.00008)
        long_j = row['long'] + random.uniform(-0.00008, 0.00008)
        
        # Color logic based on price (simple)
        if row['price'] > 2000000: color = 'darkred'
        elif row['price'] > 1200000: color = 'red'
        elif row['price'] > 800000: color = 'orange'
        else: color = 'green'

        popup_html = f"""
        <div style="font-family: Arial; width: 220px;">
            <h5 style="margin-bottom:5px;">{row['name'][:50]}...</h5>
            <hr style="margin:5px 0;">
            <b>Fiyat:</b> {row['price']:,.0f} SAR<br>
            <b>Alan:</b> {row['area_m2']:.2f} m²<br>
            <b>Oda:</b> {row['rooms']}<br>
            <b>Banyo:</b> {row['bath']}<br>
            <hr style="margin:5px 0;">
            <a href="{row['link']}" target="_blank" style="color: #007bff; font-weight:bold;">Bayut'ta Gör</a>
        </div>
        """
        
        folium.CircleMarker(
            location=[lat_j, long_j],
            radius=6,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{row['price']:,.0f} SAR"
        ).add_to(prop_cluster)
    
    prop_cluster.add_to(m)

    # --- RADIUS CALCULATION HACK (WITHOUT GEOPY) ---
    def get_district_radius(grp):
        if len(grp) <= 1: return 800 # Default 800m for single listing
        center_lat, center_lon = grp['lat'].mean(), grp['long'].mean()
        # Simplified distance for small area (SAR)
        # 1 deg lat ~ 111km, 1 deg lon ~ 100km (at 24N)
        dist_sq = ((grp['lat'] - center_lat)*111000)**2 + ((grp['long'] - center_lon)*100000)**2
        max_dist = dist_sq.max()**0.5
        return min(max(max_dist * 1.15, 600), 4500) # Buffer + Min/Max cap

    # Re-calculate stats with city+district to avoid different cities' matching districts merging
    agg_dict = {
        'price': 'mean',
        'area_m2': 'mean',
        'lat': 'mean',
        'long': 'mean',
        'id': 'count'
    }
    for c in amenity_cols:
        agg_dict[c] = 'mean'
    
    district_groups = df.groupby(['city', 'district'])
    district_stats = district_groups.agg(agg_dict).reset_index()
    district_stats.rename(columns={'id': 'listing_count'}, inplace=True)
    district_stats['price_per_m2'] = district_stats['price'] / district_stats['area_m2']
    
    # Calculate dynamic radii
    radii_map = {}
    for (city, dist), grp in district_groups:
        radii_map[(city, dist)] = get_district_radius(grp)

    # --- LAYER 2: District Analysis (Circles) ---
    dist_layer = folium.FeatureGroup(name="Mahalle Analizleri", show=False)
    
    # Color scale for districts
    min_p = district_stats['price_per_m2'].quantile(0.1)
    max_p = district_stats['price_per_m2'].quantile(0.9)
    colormap = cm.LinearColormap(colors=['green', 'yellow', 'red', 'purple'], 
                                 index=[min_p, min_p + (max_p-min_p)*0.33, min_p + (max_p-min_p)*0.66, max_p],
                                 vmin=min_p, vmax=max_p,
                                 caption='Mahalle Ortalama m2 Fiyatı (SAR)')
    
    for _, row in district_stats.iterrows():
        if pd.isna(row['lat']) or pd.isna(row['long']): continue
            
        ams_html = ""
        ams = [(c.replace('has_', '').replace('_', ' ').title(), row[c] * 100) for c in amenity_cols]
        ams.sort(key=lambda x: x[1], reverse=True)
        for name, val in ams[:6]:
            if val > 1: ams_html += f"<li>{name}: {val:.1f}%</li>"
            
        popup_html = f"""
        <div style="font-family: Arial; width: 240px; padding:5px;">
            <h4 style="margin-top:0;">{row['district']} ({row['city']})</h4>
            <b>Ort. Fiyat:</b> {row['price']:,.0f} SAR<br>
            <b>Ort. m2 Fiyatı:</b> {row['price_per_m2']:,.0f} SAR/m²<br>
            <b>Toplam İlan:</b> {row['listing_count']}<br>
            <hr style="margin:5px 0;">
            <b>Özellik Oranları:</b>
            <ul style="padding-left:15px; margin-bottom:0;">{ams_html}</ul>
        </div>
        """
        
        # USE folium.Circle for meter-based radius
        folium.Circle(
            location=[row['lat'], row['long']],
            radius=radii_map[(row['city'], row['district'])], 
            color=colormap(row['price_per_m2']),
            fill=True,
            fill_color=colormap(row['price_per_m2']),
            fill_opacity=0.4, # Lower opacity for better clarity
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=f"{row['district']} ({row['city']})"
        ).add_to(dist_layer)
        
    dist_layer.add_to(m)
    m.add_child(colormap)

    # 4. Layer Control
    folium.LayerControl(collapsed=False).add_to(m)

    # 5. Save
    os.makedirs("reports/interactive", exist_ok=True)
    output_path = "reports/interactive/riyadh_map.html"
    m.save(output_path)
    print(f"Comprehensive map generated at: {output_path}")

if __name__ == "__main__":
    generate_comprehensive_map()
