# -*- coding: utf-8 -*-
"""
Bioinformatika Loyihasi 13: Mashinali O'qitish (Machine Learning) Moduli
- XGBoost (XGBClassifier)
- Random Forest Classifier
- Support Vector Machine (SVM)
- Logistic Regression (L2 / ElasticNet)
- K-Nearest Neighbors (KNN)
- 5-Fold Stratified Cross-Validation
- Kompleks baholash metrikalari (Accuracy, Precision, Recall, Specificity, F1, ROC-AUC, PR-AUC, MCC)
- Feature Importance (Biomarker ahamiyati)
"""

import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
import xgboost as xgb

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, matthews_corrcoef,
    confusion_matrix, roc_curve, precision_recall_curve
)
from sklearn.model_selection import StratifiedKFold, cross_val_score

def train_and_evaluate_models(base_dir=None, random_state=42):
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    proc_dir = os.path.join(base_dir, "data", "processed")
    metrics_dir = os.path.join(base_dir, "results", "metrics")
    os.makedirs(metrics_dir, exist_ok=True)

    # 1. Ma'lumotlarni yuklash
    X_train = pd.read_csv(os.path.join(proc_dir, "X_train.csv"), index_col=0)
    X_test = pd.read_csv(os.path.join(proc_dir, "X_test.csv"), index_col=0)
    y_train = pd.read_csv(os.path.join(proc_dir, "y_train.csv"), index_col=0)["Target_Binary"].values
    y_test = pd.read_csv(os.path.join(proc_dir, "y_test.csv"), index_col=0)["Target_Binary"].values

    print(f"[*] Mashinali o'qitish boshlandi: Train={X_train.shape}, Test={X_test.shape}")

    # 2. Modellarni aniqlash
    models = {
        "XGBoost": xgb.XGBClassifier(
            n_estimators=150, max_depth=4, learning_rate=0.08,
            subsample=0.85, colsample_bytree=0.8,
            eval_metric="logloss", random_state=random_state
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=150, max_depth=6, max_features="sqrt",
            random_state=random_state
        ),
        "Support Vector Machine (RBF)": SVC(
            C=1.5, kernel="rbf", probability=True,
            random_state=random_state
        ),
        "Logistic Regression": LogisticRegression(
            C=0.5, penalty="l2", max_iter=1000,
            random_state=random_state
        ),
        "K-Nearest Neighbors (KNN)": KNeighborsClassifier(
            n_neighbors=5, weights="distance"
        )
    }

    results = []
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)
    roc_curves_data = {}
    fitted_models = {}

    for name, clf in models.items():
        print(f"[*] O'qitilmoqda: {name}...")
        
        # 5-Fold Cross-Validation
        cv_scores = cross_val_score(clf, X_train, y_train, cv=cv, scoring="roc_auc")
        cv_auc_mean = np.mean(cv_scores)
        cv_auc_std = np.std(cv_scores)

        # Fit model
        clf.fit(X_train, y_train)
        fitted_models[name] = clf

        # Predict
        y_pred = clf.predict(X_test)
        y_prob = clf.predict_proba(X_test)[:, 1] if hasattr(clf, "predict_proba") else y_pred

        # Metrics
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_prob)
        pr_auc = average_precision_score(y_test, y_prob)
        mcc = matthews_corrcoef(y_test, y_pred)

        # Specificity
        tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0

        # ROC Curve ma'lumotlari
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        roc_curves_data[name] = (fpr, tpr, roc_auc)

        results.append({
            "Model": name,
            "Accuracy": round(acc, 4),
            "Precision": round(prec, 4),
            "Recall (Sensitivity)": round(rec, 4),
            "Specificity": round(spec, 4),
            "F1-Score": round(f1, 4),
            "ROC-AUC (Test)": round(roc_auc, 4),
            "5-Fold CV ROC-AUC": f"{cv_auc_mean:.4f} ± {cv_auc_std:.4f}",
            "PR-AUC": round(pr_auc, 4),
            "MCC": round(mcc, 4)
        })

    # Natijalar jadvali
    res_df = pd.DataFrame(results).sort_values(by="ROC-AUC (Test)", ascending=False)
    metrics_file = os.path.join(metrics_dir, "model_comparison_metrics.csv")
    res_df.to_csv(metrics_file, index=False)
    print(f"\n[OK] Modellarni taqqoslash natijalari saqlandi: {metrics_file}")
    print(res_df.to_string(index=False))

    # 3. XGBoost Feature Importance (Biomarker genlar darajalanishi)
    xgb_model = fitted_models["XGBoost"]
    rf_model = fitted_models["Random Forest"]

    feature_names = X_train.columns
    xgb_importance = xgb_model.feature_importances_
    rf_importance = rf_model.feature_importances_

    importance_df = pd.DataFrame({
        "Gene": feature_names,
        "XGBoost_Importance": xgb_importance,
        "RandomForest_Importance": rf_importance
    })
    importance_df["Mean_Importance"] = (importance_df["XGBoost_Importance"] + importance_df["RandomForest_Importance"]) / 2
    importance_df = importance_df.sort_values(by="XGBoost_Importance", ascending=False)
    
    importance_file = os.path.join(metrics_dir, "feature_importances.csv")
    importance_df.to_csv(importance_file, index=False)
    print(f"\n[OK] Top biomarker genlar ahamiyati saqlandi: {importance_file}")
    print("Top 10 ta eng kuchli prediktor genlar:")
    print(importance_df[["Gene", "XGBoost_Importance", "RandomForest_Importance"]].head(10).to_string(index=False))

    # 4. O'qitilgan modellarni saqlash (Tezkor yuklanish uchun)
    models_dir = os.path.join(base_dir, "results", "models")
    os.makedirs(models_dir, exist_ok=True)
    models_path = os.path.join(models_dir, "fitted_models.joblib")
    joblib.dump(fitted_models, models_path)
    print(f"[OK] Barcha o'qitilgan modellar saqlandi: {models_path}")

    # Saqlash ROC ma'lumotlari
    roc_dict_df = pd.DataFrame()
    for mname, (fpr, tpr, auc_val) in roc_curves_data.items():
        # Vaqtincha saqlash
        pass

    return res_df, importance_df, fitted_models, roc_curves_data

if __name__ == "__main__":
    train_and_evaluate_models()

