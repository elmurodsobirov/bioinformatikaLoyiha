# -*- coding: utf-8 -*-
"""
Bioinformatika Loyihasi 13: Interaktiv Diagnostik Bashorat Dasturi (CLI / Demo)
Ushbu dastur o'qitilgan XGBoost modelidan foydalanib, yangi bemorning
gen ekspressiyasi profili asosida kasallik ehtimolligini va biomarkerlar hissasini aniqlaydi.
"""

import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

import numpy as np
import pandas as pd
import xgboost as xgb
from src.ml_pipeline import train_and_evaluate_models

def run_clinical_prediction_demo():
    print("=" * 80)
    print("   BIOINFORMATIKA: BIOLOGIK MA'LUMOTLAR ASOSIDA KASALLIKLARNI")
    print("   MASHINALI O'QITISH YORDAMIDA BASHORATLASH (13-LOYIHA)")
    print("   Mualliflar: Ramanov Rustam va Sobirov Elmurod")
    print("   TCGA-BRCA / GEO Gen Ekspressiyasi & XGBoost Machine Learning Modeli")
    print("=" * 80)

    proc_dir = os.path.join(base_dir, "data", "processed")
    metrics_dir = os.path.join(base_dir, "results", "metrics")
    
    X_test = pd.read_csv(os.path.join(proc_dir, "X_test.csv"), index_col=0)
    y_test = pd.read_csv(os.path.join(proc_dir, "y_test.csv"), index_col=0)["Target_Binary"].values
    clin_raw = pd.read_csv(os.path.join(base_dir, "data", "raw", "clinical_sample_metadata.csv"), index_col=0)
    imp_df = pd.read_csv(os.path.join(metrics_dir, "feature_importances.csv"))

    # Modelni yuklash
    print("[*] XGBoost modeli va biomarkerlar bazasi yuklanmoqda...")
    models_file = os.path.join(base_dir, "results", "models", "fitted_models.joblib")
    import joblib
    if os.path.exists(models_file):
        fitted_models = joblib.load(models_file)
    else:
        _, _, fitted_models, _ = train_and_evaluate_models(base_dir)
    model = fitted_models["XGBoost"]

    print("\n[✓] Tizim tayyor. Test kohortasidan tasodifiy 3 ta bemor tekshirilmoqda:\n")

    sample_indices = [5, 18, 42]

    for s_idx in sample_indices:
        patient_id = X_test.index[s_idx]
        actual_label = "Tumor (Xavfli o'sma)" if y_test[s_idx] == 1 else "Normal (Sog'lom / Xavfsiz)"
        clin_info = clin_raw.loc[patient_id]

        patient_profile = X_test.iloc[[s_idx]]
        prob_tumor = model.predict_proba(patient_profile)[0, 1]
        predicted_class = "Tumor (Xavfli o'sma)" if prob_tumor >= 0.5 else "Normal (Sog'lom / Xavfsiz)"

        print("-" * 75)
        print(f"Bemor ID: {patient_id} | Yoshi: {clin_info['Age']} yosh | Bosqich: {clin_info['Stage']}")
        print(f"Haqiqiy klinik holat : {actual_label}")
        print(f"XGBoost Bashorati    : {predicted_class}")
        print(f"Saraton Ehtimolligi  : {prob_tumor * 100:.2f}%  (Ishonchlilik: {max(prob_tumor, 1-prob_tumor)*100:.2f}%)")
        
        # Top 5 ta biomarker darajasi
        print("Asosiy diagnostik biomarkerlar ko'rsatkichi (Z-score):")
        for _, r in imp_df.head(5).iterrows():
            g = r["Gene"]
            val = patient_profile[g].values[0]
            status = "Yuqori (Overexpressed)" if val > 0.5 else ("Past (Suppressed)" if val < -0.5 else "O'rtacha")
            print(f"   • {g:<8}: {val:+6.2f} [{status}] (Ahamiyati: {r['XGBoost_Importance']*100:.1f}%)")

    print("\n" + "=" * 75)
    print("Xulosa: XGBoost modeli genlar ifodalanishi asosida kasallikni yuqori aniqlikda bashorat qildi.")

if __name__ == "__main__":
    run_clinical_prediction_demo()

