
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

def run_linear_regression():
    # 1. Load the cleaned data
    data_path = "data/processed/df_final_ml.csv"
    if not os.path.exists(data_path):
        # Fallback for running from within src/models/
        data_path = "../../data/processed/df_final_ml.csv"
    
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        return
    
    df = pd.read_csv(data_path, encoding="utf-8-sig")

    # 2. Select Features and Target
    # We use numerical features and encoded categorical features
    amenity_cols = [c for c in df.columns if c.startswith('has_')]
    features = ['rooms', 'area_m2', 'district', 'city'] + amenity_cols
    target = 'price'

    # Filter out any rows with NaNs in these columns
    df_model = df[features + [target]].dropna()
    
    X = df_model[features]
    y = df_model[target]

    print(f"Dataset size for modeling: {len(df_model)} rows.")

    # 3. Preprocessing Pipeline
    # OneHotEncoding for categorical, passthrough for numerical
    categorical_features = ['district', 'city']
    numerical_features = ['rooms', 'area_m2'] + amenity_cols # amenities are already 0/1

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', 'passthrough', numerical_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])

    # 4. Create Regression Pipeline
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', LinearRegression())
    ])

    # 5. Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 6. Train
    model.fit(X_train, y_train)

    # 7. Evaluate
    y_pred = model.predict(X_test)
    
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    print("\n--- Model Performansı ---")
    print(f"R² Skoru (Başarı Oranı): {r2:.4f}")
    print(f"MAE (Ortalama Hata): {mae:,.0f} SAR")
    print(f"RMSE (Hata Standart Sapması): {rmse:,.0f} SAR")
    
    # 8. Feature Importance (Slopes)
    # Getting feature names after encoding
    ohe = model.named_steps['preprocessor'].named_transformers_['cat']
    cat_feature_names = ohe.get_feature_names_out(categorical_features).tolist()
    all_feature_names = numerical_features + cat_feature_names
    
    coeffs = model.named_steps['regressor'].coef_
    
    coeff_df = pd.DataFrame({'Feature': all_feature_names, 'Coefficient': coeffs})
    print("\n--- Önemli Katsayılar (İlk 10) ---")
    print(coeff_df.sort_values(by='Coefficient', ascending=False).head(10))

    # Save metrics to a file
    res_path = "reports/figures/ml_results.txt"
    os.makedirs(os.path.dirname(res_path), exist_ok=True)
    with open(res_path, "w", encoding="utf-8") as f:
        f.write(f"R2: {r2}\nMAE: {mae}\nRMSE: {rmse}\n")
        f.write(coeff_df.sort_values(by='Coefficient', ascending=False).to_string())

import os
if __name__ == "__main__":
    run_linear_regression()
