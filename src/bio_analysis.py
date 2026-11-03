# -*- coding: utf-8 -*-
"""
Bioinformatika Loyihasi 13: Bioinformatik Tahlil Moduli
- Differensial Ekspressiyalangan Genlar tahlili (DEG Analysis: log2FC, p-value, FDR)
- Asosiy Komponentlar Tahlili (PCA - Principal Component Analysis)
- Statistik ishonchlilik (Benjamini-Hochberg False Discovery Rate)
- Top diagnostik biomarker genlarni saralab olish
"""

import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.decomposition import PCA

def benjamini_hochberg(p_values):
    """Benjamini-Hochberg FDR (False Discovery Rate) tuzatish algoritmi"""
    p_values = np.asarray(p_values, dtype=float)
    n = len(p_values)
    sorted_indices = np.argsort(p_values)
    sorted_p = p_values[sorted_indices]
    fdr = np.empty(n)
    
    cummin = 1.0
    for i in range(n - 1, -1, -1):
        rank = i + 1
        calc = (sorted_p[i] * n) / rank
        cummin = min(cummin, calc)
        fdr[sorted_indices[i]] = cummin
    return np.clip(fdr, 0, 1)

def run_differential_expression_analysis(base_dir=None):
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    raw_file = os.path.join(base_dir, "data", "raw", "tcga_geo_breast_cancer_expression.csv")
    clinical_file = os.path.join(base_dir, "data", "raw", "clinical_sample_metadata.csv")
    
    expr_df = pd.read_csv(raw_file, index_col=0)
    clinical_df = pd.read_csv(clinical_file, index_col=0)

    tumor_samples = clinical_df[clinical_df["Diagnosis"] == "Tumor"].index
    normal_samples = clinical_df[clinical_df["Diagnosis"] == "Normal"].index

    print(f"[*] DEG tahlili o'tkazilmoqda ({len(tumor_samples)} Tumor vs {len(normal_samples)} Normal)...")

    deg_results = []

    for gene in expr_df.columns:
        tumor_vals = expr_df.loc[tumor_samples, gene].values
        normal_vals = expr_df.loc[normal_samples, gene].values

        mean_tumor = np.mean(tumor_vals)
        mean_normal = np.mean(normal_vals)
        log2_fc = mean_tumor - mean_normal  # Chunki qiymatlar allaqachon log2 miqyosida

        # Welch's t-test (dispersiyalar tengsizligi hisobga olingan)
        t_stat, p_val = stats.ttest_ind(tumor_vals, normal_vals, equal_var=False)

        deg_results.append({
            "Gene": gene,
            "Mean_Tumor": round(mean_tumor, 4),
            "Mean_Normal": round(mean_normal, 4),
            "log2FC": round(log2_fc, 4),
            "t_statistic": round(t_stat, 4),
            "p_value": p_val
        })

    deg_df = pd.DataFrame(deg_results)
    deg_df["FDR_adj_p"] = benjamini_hochberg(deg_df["p_value"].values)
    deg_df["neg_log10_p"] = -np.log10(np.clip(deg_df["p_value"], 1e-300, 1.0))

    # Differensial statusni belgilash
    deg_df["Significance"] = "Not Significant"
    deg_df.loc[(deg_df["log2FC"] >= 1.0) & (deg_df["FDR_adj_p"] < 0.05), "Significance"] = "Upregulated (Tumor)"
    deg_df.loc[(deg_df["log2FC"] <= -1.0) & (deg_df["FDR_adj_p"] < 0.05), "Significance"] = "Downregulated (Normal)"

    # Saralash (eng yuqori o'zgarishga qarab)
    deg_df = deg_df.sort_values(by="FDR_adj_p", ascending=True)

    out_csv = os.path.join(base_dir, "results", "selected_biomarkers.csv")
    deg_df.to_csv(out_csv, index=False)

    n_up = (deg_df["Significance"] == "Upregulated (Tumor)").sum()
    n_down = (deg_df["Significance"] == "Downregulated (Normal)").sum()
    print(f"[OK] DEG tahlili yakunlandi: {out_csv}")
    print(f"     - Upregulated genlar (saraton to'qimada faollashgan): {n_up} ta")
    print(f"     - Downregulated genlar (supressor, pasaygan): {n_down} ta")

    # 2. PCA tahlili
    print("[*] Asosiy komponentlar tahlili (PCA) bajarilmoqda...")
    pca = PCA(n_components=5)
    pca_coords = pca.fit_transform(expr_df)
    pca_df = pd.DataFrame(pca_coords, index=expr_df.index, columns=[f"PC{i+1}" for i in range(5)])
    pca_df["Diagnosis"] = clinical_df.loc[expr_df.index, "Diagnosis"]
    pca_df.to_csv(os.path.join(base_dir, "results", "pca_transformed_data.csv"))

    var_ratio = pca.explained_variance_ratio_
    print(f"     - PC1 tushuntirilgan dispersiya: {var_ratio[0]*100:.2f}%")
    print(f"     - PC2 tushuntirilgan dispersiya: {var_ratio[1]*100:.2f}%")
    print(f"     - Jami 2 ta komponent dispersiyasi: {(var_ratio[0]+var_ratio[1])*100:.2f}%")

    return deg_df, pca_df

if __name__ == "__main__":
    run_differential_expression_analysis()
