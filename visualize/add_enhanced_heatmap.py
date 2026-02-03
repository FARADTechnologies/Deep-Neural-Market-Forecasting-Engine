import json
import os

notebook_path = r'C:\Users\ACER\Documents\My Projects\DataScience\bayut_scrape\analiz.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Code for the new heatmap
heatmap_code = [
    "import pandas as pd\n",
    "import numpy as np\n",
    "import seaborn as sns\n",
    "import matplotlib.pyplot as plt\n",
    "\n",
    "# 1. Sütun İsimlerini Senkronize Et ve Birim Fiyatı Hesapla\n",
    "df_analysis['price_per_m2'] = df_analysis['price'] / df_analysis['area_m2']\n",
    "\n",
    "# 2. Korelasyon Matrisi Oluşturma\n",
    "cols_to_corr = ['price', 'rooms', 'bath', 'area_m2', 'price_per_m2']\n",
    "corr_matrix = df_analysis[cols_to_corr].corr()\n",
    "\n",
    "# 3. Görselleştirme (Kullanıcının İstediği Format)\n",
    "plt.figure(figsize=(10, 7))\n",
    "sns.heatmap(corr_matrix, \n",
    "            annot=True, \n",
    "            fmt=\".2f\", \n",
    "            cmap='coolwarm', # Veya 'RdBu_r'\n",
    "            center=0,\n",
    "            linewidths=0.5)\n",
    "\n",
    "plt.title(\"Fiyat ve Özellikler Arasındaki İlişki (Korelasyon)\", fontsize=15, pad=20)\n",
    "plt.show()\n"
]

# Create new cell
new_cell = {
    "cell_type": "code",
    "execution_count": None,
    "id": "enhanced_heatmap",
    "metadata": {},
    "outputs": [],
    "source": heatmap_code
}

# Find proper insertion point (after the previous heatmap or at the end)
inserted = False
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code' and "Konum Etkisinden Arındırılmış Bilimsel Korelasyon" in "".join(cell['source']):
        nb['cells'].insert(i + 1, new_cell)
        inserted = True
        break

if not inserted:
    nb['cells'].append(new_cell)

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("Enhanced heatmap added to notebook.")
