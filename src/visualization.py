# -*- coding: utf-8 -*-
"""
Bioinformatika Loyihasi 13: Vizualizatsiya Moduli
Ilmiy maqola va dissertatsiya darajasidagi yuqori aniqlikdagi (300 DPI) grafiklar:
1. PCA 2D Klaster grafigi (Tumor vs Normal)
2. Volcano Plot (Differensial ekspressiya: log2FC vs -log10(p-val))
3. Top 30 Biomarker Genlar Klaster Heatmap'i
4. XGBoost Top 20 Feature Importance (Genlar reytingi)
5. Asosiy markerlarning ekspressiya Boxplot taqsimotlari
6. XGBoost va Random Forest ning Confusion Matrix'lari
7. Modellarning ROC egri chiziqlari taqqoslashi (ROC Curves)
"""

import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, roc_curve, auc

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.8

def generate_all_visualizations(target_dir=None):
    if target_dir is None:
        target_dir = base_dir
    
    fig_dir = os.path.join(target_dir, "results", "figures")
    proc_dir = os.path.join(target_dir, "data", "processed")
    metrics_dir = os.path.join(target_dir, "results", "metrics")
    os.makedirs(fig_dir, exist_ok=True)

    print("[*] 1. PCA 2D klaster grafigi chizilmoqda...")
    pca_df = pd.read_csv(os.path.join(target_dir, "results", "pca_transformed_data.csv"), index_col=0)
    
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    colors = {"Tumor": "#D9534F", "Normal": "#2E86C1"}
    for diag, grp in pca_df.groupby("Diagnosis"):
        ax.scatter(grp["PC1"], grp["PC2"], label=f"{diag} (n={len(grp)})",
                   color=colors[diag], alpha=0.75, edgecolors='w', s=55)
    ax.set_title("TCGA-BRCA: Asosiy Komponentlar Tahlili (PCA 2D Klasterlash)", fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel("Asosiy Komponent 1 (PC1 - 18.10%)", fontsize=11, fontweight='bold')
    ax.set_ylabel("Asosiy Komponent 2 (PC2 - 2.89%)", fontsize=11, fontweight='bold')
    ax.legend(title="To'qima turi", frameon=True, facecolor='#F8F9FA')
    ax.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    p1 = os.path.join(fig_dir, "01_pca_clusters.png")
    plt.savefig(p1)
    plt.close()
    print(f"     [OK] Saqlandi: {p1}")

    print("[*] 2. Volcano Plot (Differensial ekspressiya) chizilmoqda...")
    deg_df = pd.read_csv(os.path.join(target_dir, "results", "selected_biomarkers.csv"))
    
    fig, ax = plt.subplots(figsize=(9, 6.5), dpi=300)
    
    up_genes = deg_df[deg_df["Significance"] == "Upregulated (Tumor)"]
    down_genes = deg_df[deg_df["Significance"] == "Downregulated (Normal)"]
    ns_genes = deg_df[deg_df["Significance"] == "Not Significant"]

    ax.scatter(ns_genes["log2FC"], ns_genes["neg_log10_p"], color="#95A5A6", alpha=0.4, s=25, label="O'zgarmagan (NS)")
    ax.scatter(up_genes["log2FC"], up_genes["neg_log10_p"], color="#C0392B", alpha=0.85, s=45, label=f"Upregulated (n={len(up_genes)})")
    ax.scatter(down_genes["log2FC"], down_genes["neg_log10_p"], color="#2980B9", alpha=0.85, s=45, label=f"Downregulated (n={len(down_genes)})")

    ax.axvline(x=1.0, color='gray', linestyle='--', alpha=0.7)
    ax.axvline(x=-1.0, color='gray', linestyle='--', alpha=0.7)
    ax.axhline(y=-np.log10(0.05), color='gray', linestyle='--', alpha=0.7)

    top_label_genes = ["MKI67", "ERBB2", "VEGFA", "CCND1", "MMP9", "PTEN", "CDH1", "BRCA1", "FOXO3", "CDKN2A"]
    for _, row in deg_df.iterrows():
        if row["Gene"] in top_label_genes:
            ax.annotate(row["Gene"], (row["log2FC"], row["neg_log10_p"]),
                        textcoords="offset points", xytext=(4, 4), ha='left',
                        fontsize=8.5, fontweight='bold', color='#111111')

    ax.set_title("Volcano Plot: Differensial Ekspressiyalangan Onkogenlar va Supressorlar", fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel("log2 Fold Change (log2FC: Tumor vs Normal)", fontsize=11, fontweight='bold')
    ax.set_ylabel("-log10 (FDR p-value)", fontsize=11, fontweight='bold')
    ax.legend(title="Statistik holat", frameon=True, facecolor='#F8F9FA')
    ax.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    p2 = os.path.join(fig_dir, "02_volcano_plot.png")
    plt.savefig(p2)
    plt.close()
    print(f"     [OK] Saqlandi: {p2}")

    print("[*] 3. Top 30 Biomarker Klaster Heatmap'i chizilmoqda...")
    expr_raw = pd.read_csv(os.path.join(target_dir, "data", "raw", "tcga_geo_breast_cancer_expression.csv"), index_col=0)
    clin_raw = pd.read_csv(os.path.join(target_dir, "data", "raw", "clinical_sample_metadata.csv"), index_col=0)
    
    top_30_genes = deg_df.head(30)["Gene"].tolist()
    sub_expr = expr_raw[top_30_genes]

    sorted_samples = clin_raw.sort_values(by="Diagnosis").index
    sub_expr = sub_expr.loc[sorted_samples]
    sub_expr_z = (sub_expr - sub_expr.mean()) / sub_expr.std()

    fig, ax = plt.subplots(figsize=(11, 7), dpi=300)
    sns.heatmap(sub_expr_z.T, cmap="vlag", center=0, cbar_kws={'label': 'Gen ekspressiyasi Z-score'},
                yticklabels=True, xticklabels=False, ax=ax)
    ax.set_title("Top 30 Diagnostik Biomarker Genlarning Ekspressiya Heatmap Profili", fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel("Bemor namunalari (Chapda: Normal to'qima | O'ngda: Saraton to'qimasi)", fontsize=11, fontweight='bold')
    ax.set_ylabel("Biomarker Genlar", fontsize=11, fontweight='bold')
    plt.tight_layout()
    p3 = os.path.join(fig_dir, "03_heatmap_top_biomarkers.png")
    plt.savefig(p3)
    plt.close()
    print(f"     [OK] Saqlandi: {p3}")

    print("[*] 4. XGBoost Feature Importance grafigi chizilmoqda...")
    imp_df = pd.read_csv(os.path.join(metrics_dir, "feature_importances.csv"))
    top20 = imp_df.head(20).iloc[::-1]

    fig, ax = plt.subplots(figsize=(9, 7), dpi=300)
    bars = ax.barh(top20["Gene"], top20["XGBoost_Importance"], color="#16A085", edgecolor="#0E6251", height=0.65)
    ax.set_title("XGBoost Modeli Bo'yicha Eng Muhim Top 20 Prediktor Genlar (Gain)", fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel("XGBoost Nisbiy Ahamiyati (Feature Importance Gain)", fontsize=11, fontweight='bold')
    ax.set_ylabel("Gen belgisi (HGNC Gene Symbol)", fontsize=11, fontweight='bold')
    ax.grid(True, axis='x', linestyle="--", alpha=0.5)

    for bar in bars:
        w = bar.get_width()
        ax.text(w + 0.003, bar.get_y() + bar.get_height()/2, f"{w:.3f}",
                va='center', ha='left', fontsize=8.5, color='#2C3E50', fontweight='bold')

    plt.tight_layout()
    p4 = os.path.join(fig_dir, "04_xgboost_feature_importance.png")
    plt.savefig(p4)
    plt.close()
    print(f"     [OK] Saqlandi: {p4}")

    print("[*] 5. Asosiy markerlarning ekspressiya Boxplot taqsimotlari chizilmoqda...")
    expr_all = pd.read_csv(os.path.join(proc_dir, "processed_expression_all.csv"), index_col=0)
    key_genes_plot = ["VEGFA", "ERBB2", "MKI67", "PTEN", "BRCA1", "CDH1"]
    
    fig, axes = plt.subplots(2, 3, figsize=(12, 7.5), dpi=300)
    axes = axes.flatten()

    for i, g in enumerate(key_genes_plot):
        sns.boxplot(data=expr_all, x="Diagnosis", y=g, hue="Diagnosis", ax=axes[i], legend=False,
                    palette={"Tumor": "#E74C3C", "Normal": "#3498DB"}, width=0.5, boxprops=dict(alpha=0.85))
        sns.stripplot(data=expr_all, x="Diagnosis", y=g, ax=axes[i],
                      color='black', alpha=0.25, jitter=0.2, size=3)
        axes[i].set_title(f"{g} gen ekspressiyasi", fontsize=11, fontweight='bold')
        axes[i].set_ylabel("Standartlashtirilgan ekspressiya", fontsize=9.5)
        axes[i].set_xlabel("")
        axes[i].grid(True, linestyle="--", alpha=0.3)

    plt.suptitle("Onkogenlar va Supressorlarning Tumor va Normal To'qimalardagi Taqqoslanishi", fontsize=13, fontweight='bold', y=0.99)
    plt.tight_layout()
    p5 = os.path.join(fig_dir, "05_gene_expression_boxplots.png")
    plt.savefig(p5)
    plt.close()
    print(f"     [OK] Saqlandi: {p5}")

    print("[*] 6. Confusion Matrix va ROC Curve chizilmoqda...")
    from src.ml_pipeline import train_and_evaluate_models
    res_df, importance_df, fitted_models, roc_data = train_and_evaluate_models(target_dir)

    X_test = pd.read_csv(os.path.join(proc_dir, "X_test.csv"), index_col=0)
    y_test = pd.read_csv(os.path.join(proc_dir, "y_test.csv"), index_col=0)["Target_Binary"].values

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), dpi=300)
    for idx, m_name in enumerate(["XGBoost", "Random Forest"]):
        clf = fitted_models[m_name]
        y_pred = clf.predict(X_test)
        cm = confusion_matrix(y_test, y_pred)
        
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False, ax=axes[idx],
                    xticklabels=["Normal (0)", "Tumor (1)"],
                    yticklabels=["Normal (0)", "Tumor (1)"],
                    annot_kws={"size": 13, "weight": "bold"})
        axes[idx].set_title(f"{m_name} - Confusion Matrix", fontsize=12, fontweight='bold', pad=10)
        axes[idx].set_xlabel("Bashorat qilingan sinf (Predicted)", fontsize=10.5, fontweight='bold')
        axes[idx].set_ylabel("Haqiqiy klinik diagnoz (Actual)", fontsize=10.5, fontweight='bold')

    plt.tight_layout()
    p6 = os.path.join(fig_dir, "06_confusion_matrices.png")
    plt.savefig(p6)
    plt.close()
    print(f"     [OK] Saqlandi: {p6}")

    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    color_map = {
        "XGBoost": "#E74C3C",
        "Random Forest": "#27AE60",
        "Support Vector Machine (RBF)": "#8E44AD",
        "Logistic Regression": "#2980B9",
        "K-Nearest Neighbors (KNN)": "#F39C12"
    }
    for m_name, (fpr, tpr, auc_val) in roc_data.items():
        c = color_map.get(m_name, "#333333")
        ax.plot(fpr, tpr, label=f"{m_name} (AUC = {auc_val:.3f})", color=c, lw=2.2)

    ax.plot([0, 1], [0, 1], 'k--', lw=1.2, alpha=0.7, label="Tasodifiy taxmin (AUC = 0.500)")
    ax.set_title("Mashinali O'qitish Modellarining ROC Egri Chiziqlari Taqqoslanishi", fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel("False Positive Rate (1 - Specificity)", fontsize=11, fontweight='bold')
    ax.set_ylabel("True Positive Rate (Sensitivity / Recall)", fontsize=11, fontweight='bold')
    ax.legend(title="ML Modellari", loc="lower right", frameon=True, facecolor='#F8F9FA')
    ax.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    p7 = os.path.join(fig_dir, "07_roc_curves_comparison.png")
    plt.savefig(p7)
    plt.close()
    print(f"     [OK] Saqlandi: {p7}")

    print("\n[OK] Barcha 7 ta ilmiy grafiklar yuqori sifatda (300 DPI) yaratildi!")

if __name__ == "__main__":
    generate_all_visualizations()
