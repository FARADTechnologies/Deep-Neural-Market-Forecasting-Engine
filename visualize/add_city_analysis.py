import json
import os

notebook_path = r'C:\Users\ACER\Documents\My Projects\DataScience\bayut_scrape\analiz.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# The new code block for per-city correlation
per_city_correlation_code = [
    "import pandas as pd\n",
    "import seaborn as sns\n",
    "import matplotlib.pyplot as plt\n",
    "\n",
    "# Şehir bazlı korelasyon hesaplayıcı\n",
    "def calculate_city_correlations(df):\n",
    "    results = []\n",
    "    processed_cities = df['city'].unique()\n",
    "    \n",
    "    for city in processed_cities:\n",
    "        city_data = df[df['city'] == city]\n",
    "        # En az 5 veri noktası olan şehirleri dikkate alalım (istatistiksel güvenilirlik)\n",
    "        if len(city_data) >= 5:\n",
    "            corr = city_data['price_norm'].corr(city_data['rooms_norm'])\n",
    "            results.append({\n",
    "                'city': city,\n",
    "                'correlation': corr,\n",
    "                'count': len(city_data)\n",
    "            })\n",
    "    \n",
    "    return pd.DataFrame(results).sort_values('correlation', ascending=False)\n",
    "\n",
    "city_corrs = calculate_city_correlations(df_analysis)\n",
    "\n",
    "print(\"--- ŞEHİR BAZLI ODA/FİYAT KORELASYONLARI ---\")\n",
    "print(city_corrs.to_string(index=False))\n",
    "\n",
    "# Görselleştirme\n",
    "plt.figure(figsize=(12, 6))\n",
    "sns.barplot(data=city_corrs, x='city', y='correlation', palette='viridis')\n",
    "plt.title(\"Şehir Bazlı Fiyat-Oda Sayısı Korelasyonu (Normalize Edilmiş)\", fontsize=15)\n",
    "plt.xticks(rotation=45)\n",
    "plt.ylabel(\"Korelasyon Katsayısı\")\n",
    "plt.axhline(0, color='black', linewidth=1)\n",
    "plt.show()\n"
]

# Create a new cell object
new_cell = {
    "cell_type": "code",
    "execution_count": None,
    "id": "city_corr_analysis",
    "metadata": {},
    "outputs": [],
    "source": per_city_correlation_code
}

# Insert it after the existing correlation matrix cell
# Let's find the heatmap cell first
inserted = False
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code' and "Konum Etkisinden Arındırılmış Bilimsel Korelasyon" in "".join(cell['source']):
        nb['cells'].insert(i + 1, new_cell)
        inserted = True
        break

if not inserted:
    # Fallback to appending if search fails
    nb['cells'].append(new_cell)

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("Per-city correlation analysis added to notebook.")
