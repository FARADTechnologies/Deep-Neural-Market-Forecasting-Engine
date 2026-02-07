
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import os

def visualize_ml_results():
    # 1. Load data
    data_path = "data/processed/df_final_ml.csv"
    if not os.path.exists(data_path):
        data_path = "../../data/processed/df_final_ml.csv"
    
    if not os.path.exists(data_path):
        print("Data not found.")
        return
    df = pd.read_csv(data_path)

    # 2. Re-run model for visualization data
    amenity_cols = [c for c in df.columns if c.startswith('has_')]
    features = ['rooms', 'area_m2', 'district', 'city'] + amenity_cols
    target = 'price'
    df_model = df[features + [target]].dropna()
    X = df_model[features]
    y = df_model[target]

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', 'passthrough', ['rooms', 'area_m2'] + amenity_cols),
            ('cat', OneHotEncoder(handle_unknown='ignore'), ['district', 'city'])
        ])

    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', LinearRegression())
    ])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # --- VISUALIZATION 1: Actual vs Predicted ---
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, y_pred, alpha=0.5, color='blue')
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    plt.xlabel('Gerçek Fiyat (Actual SAR)')
    plt.ylabel('Tahmin Edilen Fiyat (Predicted SAR)')
    plt.title('Doğrusal Regresyon: Gerçek vs Tahmin')
    plt.grid(True)
    os.makedirs("reports/figures", exist_ok=True)
    plt.savefig('reports/figures/ml_actual_vs_pred.png')
    plt.close()

    # --- VISUALIZATION 2: Top Coefficients ---
    ohe = model.named_steps['preprocessor'].named_transformers_['cat']
    cat_names = ohe.get_feature_names_out(['district', 'city']).tolist()
    all_names = (['rooms', 'area_m2'] + amenity_cols) + cat_names
    coeffs = model.named_steps['regressor'].coef_
    
    coeff_df = pd.DataFrame({'Feature': all_names, 'Coeff': coeffs})
    top_coeffs = coeff_df.sort_values(by='Coeff', ascending=False).head(15)

    plt.figure(figsize=(12, 8))
    sns.barplot(data=top_coeffs, x='Coeff', y='Feature', palette='viridis')
    plt.title('Fiyatı En Çok Artıran İlk 15 Faktör')
    plt.xlabel('Katsayı Etkisi (SAR)')
    plt.ylabel('Özellik / Mahalle')
    plt.tight_layout()
    plt.savefig('reports/figures/ml_feature_importance.png')
    plt.close()

    print("Görseller ml_actual_vs_pred.png ve ml_feature_importance.png olarak kaydedildi.")

if __name__ == "__main__":
    visualize_ml_results()
