import json
import os

notebook_path = r'C:\Users\ACER\Documents\My Projects\DataScience\bayut_scrape\analiz.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Cell indices for the normalization and correlation analysis
# Based on the previous view_file, they were around the end.
# I'll search for the source content to be sure.

target_code_1 = "df_final.groupby('district')['price'].transform(lambda x: (x - x.mean()) / x.std() if x.std() > 0 else 0)"
target_code_2 = "df_final.groupby('district')['rooms'].transform(lambda x: (x - x.mean()) / x.std() if x.std() > 0 else 0)"

replacement_code_1 = "df_final.groupby('district')['price'].transform(lambda x: (x - x.mean()) / x.std() if pd.notna(x.std()) and x.std() > 0 else 0)"
replacement_code_2 = "df_final.groupby('district')['rooms'].transform(lambda x: (x - x.mean()) / x.std() if pd.notna(x.std()) and x.std() > 0 else 0)"

modified = False
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        if target_code_1 in source or target_code_2 in source:
            print(f"Found target cell. Replacing...")
            new_source = []
            for line in cell['source']:
                line = line.replace(target_code_1, replacement_code_1)
                line = line.replace(target_code_2, replacement_code_2)
                new_source.append(line)
            cell['source'] = new_source
            modified = True

if modified:
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
    print("Notebook updated successfully.")
else:
    print("Target code not found in notebook.")
