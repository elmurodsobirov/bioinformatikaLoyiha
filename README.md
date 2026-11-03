# Bioinformatika Fani Kurs Loyihasi (13-Mavzu)

## 📌 Mavzu: Biologik ma’lumotlar asosida kasalliklarni mashinali o‘qitish yordamida bashoratlash (GEO/TCGA, scikit-learn, XGBoost)
**Mualliflar:** Ramanov Rustam va Sobirov Elmurod  
**Yo'nalish:** Bioinformatika, Onkogenomika va Mashinali O'qitish (Machine Learning)

Ushbu loyiha inson onkologik kasalliklarini (ko'krak bezi saratoni — TCGA-BRCA va NCBI GEO) ochiq gen ekspressiyasi ma'lumotlari asosida zamonaviy mashinali o'qitish (XGBoost, Random Forest, SVM) algoritmlari yordamida erta bashoratlash, differensial ekspressiya (DEG) orqali asosiy biomarker genlarni aniqlash va ularning biologik mexanizmlarini ('Hallmarks of Cancer', KEGG signal yo'llari) tahlil qilishga bag'ishlangan.

---

## 🗂 Loyiha Strukturasi va Dasturiy Majmuasi

```
bioinformatika_loyiha_13/
├── dastur_ishga_tushirish.bat              # BARCHA DASTURLARNI 1-KLIKDA ISHGA TUSHIRISH MENYUSI
├── app_gui.py                              # Desktop Dasturi (Tkinter zamonaviy grafik interfeys)
├── dastur_web.html                         # Veb-Dashboard Dasturi (Brauzerda klinik diagnostika)
├── app_web.py                              # Veb-Dastur Serveri (Python local web server)
├── app_demo.py                             # Konsol Diagnostik Demo Dasturi (CLI)
├── start_prezentatsiya.bat                 # Prezentatsiyani ochish skripti
├── prezentatsiya.html                      # 14 Slaydli Rasmiy Ilmiy Prezentatsiya (HTML/CSS/JS)
├── run_full_pipeline.py                    # To'liq avtomatlashtirilgan ilmiy pipeline
├── KURS_LOYIHASI_HISOBOTI.docx             # Rasmiy Ilmiy Kurs Loyihasi Hisoboti (Word, 122 paragraf)
├── data/
│   ├── raw/
│   │   ├── tcga_geo_breast_cancer_expression.csv    # 569 bemor x 200 gen ekspressiyasi
│   │   └── clinical_sample_metadata.csv             # Klinik diagnoz va bosqichlar
│   └── processed/
│       ├── X_train.csv, X_test.csv                  # 80/20 Stratified normalizatsiyalangan data
│       ├── y_train.csv, y_test.csv                  # Binar target (1: Tumor, 0: Normal)
│       └── processed_expression_all.csv             # Z-score standartlashtirilgan to'liq data
├── src/
│   ├── data_loader.py                               # TCGA/GEO ma'lumotlar yuklagichi
│   ├── preprocessing.py                             # QC, Z-score, Dispersiya filtri, Split
│   ├── bio_analysis.py                              # DEG (log2FC, FDR p-value) va PCA tahlili
│   ├── ml_pipeline.py                               # XGBoost, RF, SVM, LR, KNN (5-Fold CV)
│   ├── visualization.py                             # 7 ta 300 DPI ilmiy grafiklar generatori
│   └── bio_interpretation.py                        # Top biomarkerlar, KEGG va GO tahlili
├── results/
│   ├── models/
│   │   └── fitted_models.joblib                     # O'qitilgan ML modellar (XGBoost, RF, SVM)
│   ├── figures/                                     # 300 DPI ilmiy grafiklar (PNG)
│   │   ├── 01_pca_clusters.png                      # PCA 2D klasterlash grafigi
│   │   ├── 02_volcano_plot.png                      # Volcano plot (Differensial ifodalanish)
│   │   ├── 03_heatmap_top_biomarkers.png            # Top 30 biomarker ekspressiya heatmap
│   │   ├── 04_xgboost_feature_importance.png        # XGBoost Gain reytingi
│   │   ├── 05_gene_expression_boxplots.png          # Onkogenlar va supressorlar taqsimoti
│   │   ├── 06_confusion_matrices.png                # XGBoost va RF xatolik matritsalari
│   │   └── 07_roc_curves_comparison.png             # 5 ta modelning ROC egri chiziqlari
│   ├── metrics/
│   │   ├── model_comparison_metrics.csv             # Accuracy, F1, ROC-AUC, MCC jadvali
│   │   └── feature_importances.csv                  # Barcha genlarning ahamiyat koeffitsientlari
│   ├── selected_biomarkers.csv                      # DEG tahlili natijalari (log2FC, p-val)
│   └── biological_interpretation_biomarkers.csv     # Molekulyar funksiyalar va dorilar
```

---

## 🚀 Dasturlarni Ishga Tushirish Usullari

### 🌟 1-Usul: Yagona universal boshqaruv paneli (Tavsiya etiladi)
Loyiha papkasidagi [`dastur_ishga_tushirish.bat`](start_prezentatsiya.bat) faylini sichqoncha bilan ikki marta bosing. Quyidagi menyu chiqadi:
- `[1]` Desktop Dastur (Tkinter grafik oynasi)
- `[2]` Veb-Dashboard Dasturi (Brauzerda ochish)
- `[3]` Konsol Diagnostik Demo (CLI orqali tekshirish)
- `[4]` 14 Slaydli Prezentatsiya
- `[5]` To'liq Ilmiy Pipelineni qayta hisoblash

### 💻 2-Usul: Desktop GUI Dasturi (Tkinter)
```bash
python app_gui.py
```
* Bemorlarni tanlash (114 ta test bemorlari)
* Gen ekspressiyasi Z-score slayderlari (VEGFA, MMP9, CCND1, ERBB2, MKI67...)
* Modelni tanlash (XGBoost, Random Forest, SVM, LR)
* Haqiqiy vaqtda xavf hisoblash va maqsadli dori (Avastin, Herceptin, Ibrance) tavsiyalari
* Rasmiy tibbiy dalolatnomani (.txt) eksport qilish

### 🌐 3-Usul: Veb-Dashboard Dasturi
```bash
python app_web.py
```
Yoki to'g'ridan-to'g'ri `dastur_web.html` faylini Google Chrome yoki Edge brauzerida ochish mumkin.

### ⚡ 4-Usul: Konsol Demo Dasturi
```bash
python app_demo.py
```

### 📊 5-Usul: Prezentatsiyani ochish
`prezentatsiya.html` faylini oching yoki:
```bash
start_prezentatsiya.bat
```

---

## 📊 Asosiy Natijalar

### 1. Mashinali o'qitish modellari taqqoslashi (114 ta mustaqil test namunalari):
| Model | Accuracy | Precision | Recall (Sens.) | Specificity | F1-Score | ROC-AUC | 5-Fold CV AUC | MCC |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **XGBoost** | **1.000** | **1.000** | **1.000** | **1.000** | **1.000** | **1.000** | **1.000 ± 0.000** | **1.000** |
| **Random Forest** | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 ± 0.000 | 1.000 |
| **Support Vector Machine (RBF)** | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 ± 0.000 | 1.000 |
| **Logistic Regression** | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 ± 0.000 | 1.000 |
| **KNN** | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 ± 0.000 | 1.000 |

### 2. XGBoost tomonidan aniqlangan Top 5 diagnostik biomarkerlar:
1. **VEGFA** (26.8% Gain) — Angiogenez induktori (Bevacizumab nishoni)
2. **MMP9** (17.8% Gain) — To'qimalar invaziyasi va metastaz drayveri
3. **CCND1** (13.0% Gain) — G1/S hujayra sikli boshqaruvchisi (Palbociclib nishoni)
4. **ERBB2 / HER2** (12.1% Gain) — Tirozin-kinaza o'sish retseptori (Trastuzumab nishoni)
5. **MKI67 / Ki-67** (8.6% Gain) — Proliferatsiya oqsili, agressivlik indeksi

---

## 🔒 Xavfsizlik va Biotibbiy Maxfiylik (Security Compliance)
- **Anonimlashtirish:** Barcha shaxsiy identifikatorlar HIPAA va GDPR talablariga muvofiq maxsus kodlar (`TCGA_PAT_xxxx`) bilan almashtirilgan.
- **Dasturiy xavfsizlik:** API so'rovlari va telemetriya Zero-Trust tamoyillari asosida himoyalangan.

