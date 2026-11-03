# -*- coding: utf-8 -*-
"""
Bioinformatika Loyihasi 13: Preprocessing (Dastlabki qayta ishlash) moduli
- Sifat nazorati (Quality Control)
- Yetishmayotgan qiymatlarni to'ldirish (Imputation)
- Kam dispersiyali genlarni filtrlash (Variance Filtering)
- Z-score / MinMax normalizatsiyasi
- Stratified Train-Test ajratish (80/20)
"""

import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.feature_selection import VarianceThreshold

def preprocess_bio_data(raw_data_dir=None, processed_data_dir=None, test_size=0.2, random_state=42):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if raw_data_dir is None:
        raw_data_dir = os.path.join(base_dir, "data", "raw")
    if processed_data_dir is None:
        processed_data_dir = os.path.join(base_dir, "data", "processed")
    os.makedirs(processed_data_dir, exist_ok=True)

    expr_file = os.path.join(raw_data_dir, "tcga_geo_breast_cancer_expression.csv")
    clinical_file = os.path.join(raw_data_dir, "clinical_sample_metadata.csv")

    expr_df = pd.read_csv(expr_file, index_col=0)
    clinical_df = pd.read_csv(clinical_file, index_col=0)

    print("[*] 1. Sifat nazorati (Quality Control) tekshirilmoqda...")
    # Missing values tekshiruvi
    null_count = expr_df.isnull().sum().sum()
    print(f"    - Aniqlangan bo'sh (NaN) qiymatlar soni: {null_count}")
    if null_count > 0:
        expr_df = expr_df.fillna(expr_df.median())

    # 2. Kam dispersiyali genlarni filtrlash (Low variance filtering)
    print("[*] 2. Kam dispersiyali (axborotsiz) genlarni filtrlash...")
    selector = VarianceThreshold(threshold=0.1)
    selector.fit(expr_df)
    kept_genes = expr_df.columns[selector.get_support()].tolist()
    filtered_expr_df = expr_df[kept_genes]
    print(f"    - Boshlang'ich genlar: {expr_df.shape[1]} ta -> Saqlab qolingan genlar: {len(kept_genes)} ta")

    # 3. Nishon o'zgaruvchi (Target)
    y = clinical_df.loc[filtered_expr_df.index, "Target_Binary"].values
    X = filtered_expr_df.copy()

    # 4. Stratified Train / Test bo'lish
    print(f"[*] 3. Stratified Train/Test ga ajratish ({int((1-test_size)*100)}% / {int(test_size*100)}%)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, stratify=y, random_state=random_state
    )

    # 5. Normalizatsiya (StandardScaler - Z-score: mean=0, std=1)
    print("[*] 4. Z-score standartlashtirish (StandardScaler)...")
    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), index=X_train.index, columns=X_train.columns)
    X_test_scaled = pd.DataFrame(scaler.transform(X_test), index=X_test.index, columns=X_test.columns)

    # 6. Saqlash
    X_train_scaled.to_csv(os.path.join(processed_data_dir, "X_train.csv"))
    X_test_scaled.to_csv(os.path.join(processed_data_dir, "X_test.csv"))
    pd.DataFrame({"Target_Binary": y_train}, index=X_train.index).to_csv(os.path.join(processed_data_dir, "y_train.csv"))
    pd.DataFrame({"Target_Binary": y_test}, index=X_test.index).to_csv(os.path.join(processed_data_dir, "y_test.csv"))

    # To'liq qayta ishlangan ma'lumotlar
    full_processed = pd.DataFrame(scaler.transform(X), index=X.index, columns=X.columns)
    full_processed["Diagnosis"] = clinical_df.loc[X.index, "Diagnosis"]
    full_processed["Target_Binary"] = y
    full_processed.to_csv(os.path.join(processed_data_dir, "processed_expression_all.csv"))

    print(f"[OK] Dastlabki qayta ishlash yakunlandi!")
    print(f"     - Train to'plam: {X_train_scaled.shape[0]} ta namuna (Tumor: {sum(y_train)}, Normal: {len(y_train)-sum(y_train)})")
    print(f"     - Test to'plam: {X_test_scaled.shape[0]} ta namuna (Tumor: {sum(y_test)}, Normal: {len(y_test)-sum(y_test)})")

    return X_train_scaled, X_test_scaled, y_train, y_test

if __name__ == "__main__":
    preprocess_bio_data()

