# -*- coding: utf-8 -*-
"""
Bioinformatika Loyihasi 13: Bemorlarni Tashxislash va Kasallikni Bashoratlash Dasturi
Mualliflar: Ramanov Rustam va Sobirov Elmurod
Grafik Interfeys (Desktop GUI - Tkinter)
"""

import os
import sys
import json
import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk

# UTF-8 stdout
if sys.stdout is not None:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

import numpy as np
import pandas as pd
import joblib

class BioinfoClinicalApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Bioinformatika: Biologik Ma'lumotlar Asosida Kasalliklarni Mashinali O'qitish Yordamida Bashoratlash (GEO/TCGA, scikit-learn, XGBoost)")
        self.geometry("1200x820")
        self.minsize(1050, 720)
        
        # Windows dark-modern background styling
        self.configure(bg="#0b1120")

        # Load models and data
        self.load_system_data()

        # Build UI
        self.setup_ui_styles()
        self.create_widgets()

        # Load default patient
        self.select_random_patient()

    def load_system_data(self):
        try:
            proc_dir = os.path.join(base_dir, "data", "processed")
            metrics_dir = os.path.join(base_dir, "results", "metrics")
            models_dir = os.path.join(base_dir, "results", "models")
            raw_dir = os.path.join(base_dir, "data", "raw")

            self.X_test = pd.read_csv(os.path.join(proc_dir, "X_test.csv"), index_col=0)
            self.y_test = pd.read_csv(os.path.join(proc_dir, "y_test.csv"), index_col=0)["Target_Binary"].values
            self.clin_raw = pd.read_csv(os.path.join(raw_dir, "clinical_sample_metadata.csv"), index_col=0)
            self.imp_df = pd.read_csv(os.path.join(metrics_dir, "feature_importances.csv"))
            self.metrics_df = pd.read_csv(os.path.join(metrics_dir, "model_comparison_metrics.csv"))

            # Top 10 biomarkers
            self.top_genes = self.imp_df["Gene"].head(10).tolist()

            # Load fitted models
            models_path = os.path.join(models_dir, "fitted_models.joblib")
            if os.path.exists(models_path):
                self.models = joblib.load(models_path)
            else:
                from src.ml_pipeline import train_and_evaluate_models
                _, _, self.models, _ = train_and_evaluate_models(base_dir)

            self.current_patient_id = self.X_test.index[0]
            self.gene_vars = {}

        except Exception as e:
            messagebox.showerror("Yuklashda Xatolik", f"Ma'lumotlar yoki modellarni yuklashda xatolik:\n{str(e)}")
            self.destroy()

    def setup_ui_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        # Configure colors
        bg_dark = "#0b1120"
        card_bg = "#1e293b"
        accent_blue = "#38bdf8"
        text_white = "#f8fafc"

        style.configure(".", background=bg_dark, foreground=text_white, font=("Segoe UI", 10))
        style.configure("TFrame", background=bg_dark)
        style.configure("Card.TFrame", background=card_bg, relief="flat")
        
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#38bdf8", background=bg_dark)
        style.configure("SubHeader.TLabel", font=("Segoe UI", 10), foreground="#94a3b8", background=bg_dark)
        style.configure("CardTitle.TLabel", font=("Segoe UI", 11, "bold"), foreground="#f1f5f9", background=card_bg)
        
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), background="#0284c7", foreground="#ffffff")
        style.map("Primary.TButton", background=[("active", "#0369a1")])

        style.configure("Success.TButton", font=("Segoe UI", 10, "bold"), background="#10b981", foreground="#ffffff")
        style.map("Success.TButton", background=[("active", "#059669")])

        style.configure("TCombobox", fieldbackground="#334155", background="#475569", foreground="#ffffff")

        style.configure("TNotebook", background=bg_dark, tabmargins=[2, 5, 2, 0])
        style.configure("TNotebook.Tab", background="#1e293b", foreground="#cbd5e1", padding=[12, 6], font=("Segoe UI", 9, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#0284c7")], foreground=[("selected", "#ffffff")])

    def create_widgets(self):
        # 1. Top Header Bar
        header_frame = tk.Frame(self, bg="#0f172a", height=75, padx=20, pady=10)
        header_frame.pack(side=tk.TOP, fill=tk.X)

        title_lbl = tk.Label(header_frame, text="🧬 BIOLOGIK MA'LUMOTLAR ASOSIDA KASALLIKLARNI MASHINALI O'QITISH YORDAMIDA BASHORATLASH",
                             font=("Segoe UI", 14, "bold"), fg="#38bdf8", bg="#0f172a")
        title_lbl.pack(anchor="w")

        sub_lbl = tk.Label(header_frame, 
                           text="13-Mavzu • GEO va TCGA Ochiq Biologik Resurslari | scikit-learn va XGBoost Kutubxonalari | Onkologik Kasalliklar Diagnostikasi Misolida | Mualliflar: Ramanov Rustam va Sobirov Elmurod",
                           font=("Segoe UI", 9), fg="#94a3b8", bg="#0f172a")
        sub_lbl.pack(anchor="w", pady=(2, 0))

        # Main Body Layout (Left Controls, Right Results)
        body_paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg="#0b1120", sashwidth=4)
        body_paned.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)

        # ---------------- LEFT PANEL: Patient Selection & Biomarkers ----------------
        left_frame = tk.Frame(body_paned, bg="#1e293b", padx=15, pady=15, relief="flat", bd=1)
        body_paned.add(left_frame, minsize=420)

        left_title = tk.Label(left_frame, text="🧪 Bemor va Gen Ekspressiyasi Ko'rsatkichlari", 
                              font=("Segoe UI", 12, "bold"), fg="#f8fafc", bg="#1e293b")
        left_title.pack(anchor="w", pady=(0, 10))

        # Patient Selector Box
        sel_box = tk.Frame(left_frame, bg="#0f172a", padx=10, pady=10, bd=1, relief="solid")
        sel_box.pack(fill=tk.X, pady=(0, 12))

        tk.Label(sel_box, text="Test kohortasidan bemor tanlang:", font=("Segoe UI", 9, "bold"), fg="#94a3b8", bg="#0f172a").pack(anchor="w")
        
        pat_row = tk.Frame(sel_box, bg="#0f172a")
        pat_row.pack(fill=tk.X, pady=(5, 5))

        self.patient_combo = ttk.Combobox(pat_row, values=list(self.X_test.index), state="readonly", width=22)
        self.patient_combo.pack(side=tk.LEFT, padx=(0, 8))
        self.patient_combo.bind("<<ComboboxSelected>>", self.on_patient_change)

        rand_btn = tk.Button(pat_row, text="🎲 Tasodifiy", command=self.select_random_patient,
                             bg="#334155", fg="#f8fafc", font=("Segoe UI", 9, "bold"), relief="flat", padx=8)
        rand_btn.pack(side=tk.LEFT)

        # Patient Info Display
        self.lbl_patient_info = tk.Label(sel_box, text="Yuklanmoqda...", font=("Segoe UI", 9), fg="#38bdf8", bg="#0f172a", justify="left")
        self.lbl_patient_info.pack(anchor="w", pady=(4, 0))

        # Model Selection
        model_row = tk.Frame(left_frame, bg="#1e293b")
        model_row.pack(fill=tk.X, pady=(0, 10))

        tk.Label(model_row, text="Mashinali o'qitish modeli:", font=("Segoe UI", 9, "bold"), fg="#cbd5e1", bg="#1e293b").pack(side=tk.LEFT, padx=(0, 10))
        self.model_combo = ttk.Combobox(model_row, values=list(self.models.keys()), state="readonly", width=24)
        self.model_combo.set("XGBoost")
        self.model_combo.pack(side=tk.LEFT)
        self.model_combo.bind("<<ComboboxSelected>>", lambda e: self.run_prediction())

        # Gene Sliders Scrollable Area
        tk.Label(left_frame, text="Asosiy Biomarker Genlar (Normalizatsiyalangan Z-Score):", 
                 font=("Segoe UI", 9, "bold"), fg="#94a3b8", bg="#1e293b").pack(anchor="w", pady=(5, 5))

        sliders_outer = tk.Frame(left_frame, bg="#1e293b")
        sliders_outer.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(sliders_outer, bg="#1e293b", highlightthickness=0)
        scrollbar = ttk.Scrollbar(sliders_outer, orient="vertical", command=canvas.yview)
        self.sliders_inner = tk.Frame(canvas, bg="#1e293b")

        self.sliders_inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.sliders_inner, anchor="nw", width=380)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create sliders for top 10 genes
        for gene in self.top_genes:
            g_frame = tk.Frame(self.sliders_inner, bg="#1e293b", pady=3)
            g_frame.pack(fill=tk.X)

            head_row = tk.Frame(g_frame, bg="#1e293b")
            head_row.pack(fill=tk.X)

            gene_lbl = tk.Label(head_row, text=gene, font=("Segoe UI", 9, "bold"), fg="#f1f5f9", bg="#1e293b")
            gene_lbl.pack(side=tk.LEFT)

            val_var = tk.DoubleVar(value=0.0)
            self.gene_vars[gene] = val_var

            val_lbl = tk.Label(head_row, text="+0.00", font=("Segoe UI", 9), fg="#38bdf8", bg="#1e293b")
            val_lbl.pack(side=tk.RIGHT)

            slider = tk.Scale(g_frame, from_=-3.5, to=3.5, resolution=0.05, orient=tk.HORIZONTAL,
                              variable=val_var, showvalue=False, bg="#334155", fg="#38bdf8",
                              troughcolor="#0f172a", activebackground="#0284c7", bd=0, highlightthickness=0,
                              command=lambda val, lbl=val_lbl: self.on_slider_move(val, lbl))
            slider.pack(fill=tk.X)

        # Action Buttons
        btn_box = tk.Frame(left_frame, bg="#1e293b", pady=10)
        btn_box.pack(fill=tk.X, side=tk.BOTTOM)

        predict_btn = tk.Button(btn_box, text="⚡ Bashorat Qilish (Diagnostika)", command=self.run_prediction,
                                bg="#0284c7", fg="#ffffff", font=("Segoe UI", 10, "bold"), relief="flat", pady=8)
        predict_btn.pack(fill=tk.X, pady=(0, 6))

        reset_btn = tk.Button(btn_box, text="🔄 Bemorning Asl Qiymatlariga Qaytarish", command=self.reset_current_patient_values,
                              bg="#334155", fg="#cbd5e1", font=("Segoe UI", 9), relief="flat", pady=4)
        reset_btn.pack(fill=tk.X)

        # ---------------- RIGHT PANEL: Results, Interpretations & Analytics ----------------
        right_frame = tk.Frame(body_paned, bg="#0b1120", padx=10, pady=0)
        body_paned.add(right_frame, minsize=550)

        # Results Top Summary Card
        res_card = tk.Frame(right_frame, bg="#1e293b", padx=16, pady=16, relief="flat", bd=1)
        res_card.pack(fill=tk.X, pady=(0, 10))

        tk.Label(res_card, text="📊 KLINIK TASHXIS VA BASHORAT NATIJASI", 
                 font=("Segoe UI", 11, "bold"), fg="#94a3b8", bg="#1e293b").pack(anchor="w")

        diag_row = tk.Frame(res_card, bg="#1e293b")
        diag_row.pack(fill=tk.X, pady=(10, 8))

        self.lbl_diagnosis_badge = tk.Label(diag_row, text="BASHORAT QILINMOQDA...", font=("Segoe UI", 14, "bold"),
                                            fg="#ffffff", bg="#0284c7", padx=16, pady=8)
        self.lbl_diagnosis_badge.pack(side=tk.LEFT)

        stats_box = tk.Frame(diag_row, bg="#1e293b", padx=15)
        stats_box.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.lbl_prob_text = tk.Label(stats_box, text="Saraton Ehtimolligi: --%", font=("Segoe UI", 11, "bold"), fg="#f8fafc", bg="#1e293b")
        self.lbl_prob_text.pack(anchor="w")

        # Custom progress meter
        self.prob_canvas = tk.Canvas(stats_box, width=280, height=14, bg="#0f172a", highlightthickness=0)
        self.prob_canvas.pack(anchor="w", pady=(4, 4))
        self.prob_bar = self.prob_canvas.create_rectangle(0, 0, 0, 14, fill="#ef4444")

        self.lbl_conf_text = tk.Label(stats_box, text="Ishonchlilik: --% | Haqiqiy Holat: --", font=("Segoe UI", 9), fg="#94a3b8", bg="#1e293b")
        self.lbl_conf_text.pack(anchor="w")

        # Targeted Therapy Box
        self.therapy_frame = tk.Frame(res_card, bg="#0f172a", padx=12, pady=10, relief="solid", bd=1)
        self.therapy_frame.pack(fill=tk.X, pady=(6, 0))

        tk.Label(self.therapy_frame, text="💊 Tavsiya Etiladigan Molekulyar Maqsadli Terapiya (Target Therapy):", 
                 font=("Segoe UI", 9, "bold"), fg="#38bdf8", bg="#0f172a").pack(anchor="w")
        
        self.lbl_therapy_recommendations = tk.Label(self.therapy_frame, text="Tahlil qilinmoqda...", 
                                                    font=("Segoe UI", 9), fg="#e2e8f0", bg="#0f172a", justify="left")
        self.lbl_therapy_recommendations.pack(anchor="w", pady=(4, 0))

        # Right Notebook Tabs
        notebook = ttk.Notebook(right_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Top Biomarkers table
        tab_bio = tk.Frame(notebook, bg="#1e293b", padx=10, pady=10)
        notebook.add(tab_bio, text="🧬 Biomarkerlar Profili")
        self.build_biomarkers_tab(tab_bio)

        # Tab 2: Model Comparisons
        tab_models = tk.Frame(notebook, bg="#1e293b", padx=10, pady=10)
        notebook.add(tab_models, text="📈 5 ta Model Taqqoslashi")
        self.build_models_tab(tab_models)

        # Tab 3: Visualizations & Graphics
        tab_plots = tk.Frame(notebook, bg="#1e293b", padx=10, pady=10)
        notebook.add(tab_plots, text="🖼️ Tahliliy Grafiklar")
        self.build_plots_tab(tab_plots)

        # Tab 4: Export Clinical Report
        tab_export = tk.Frame(notebook, bg="#1e293b", padx=10, pady=10)
        notebook.add(tab_export, text="📄 Rasmiy Xulosa & Eksport")
        self.build_export_tab(tab_export)

    def build_biomarkers_tab(self, parent):
        tk.Label(parent, text="Saratonni Aniqlashda Asosiy Hal Qiluvchi Genlar (XGBoost Feature Importance):",
                 font=("Segoe UI", 10, "bold"), fg="#38bdf8", bg="#1e293b").pack(anchor="w", pady=(0, 8))

        cols = ("Gen", "XGBoost Ahamiyati", "RF Ahamiyati", "Bemor Darajasi (Z-score)", "Biologik Funksiyasi")
        self.bio_tree = ttk.Treeview(parent, columns=cols, show="headings", height=9)
        
        self.bio_tree.heading("Gen", text="Gen")
        self.bio_tree.heading("XGBoost Ahamiyati", text="XGBoost Hissasi")
        self.bio_tree.heading("RF Ahamiyati", text="Random Forest")
        self.bio_tree.heading("Bemor Darajasi (Z-score)", text="Bemor Qiymati")
        self.bio_tree.heading("Biologik Funksiyasi", text="Biologik Mexanizmi")

        self.bio_tree.column("Gen", width=75, anchor="center")
        self.bio_tree.column("XGBoost Ahamiyati", width=110, anchor="center")
        self.bio_tree.column("RF Ahamiyati", width=100, anchor="center")
        self.bio_tree.column("Bemor Darajasi (Z-score)", width=110, anchor="center")
        self.bio_tree.column("Biologik Funksiyasi", width=220, anchor="w")

        self.bio_tree.pack(fill=tk.BOTH, expand=True)

    def build_models_tab(self, parent):
        tk.Label(parent, text="Mashinali O'qitish Modellari Qiyosiy Sinov Natijalari (114 ta Mustaqil Test Namunasi):",
                 font=("Segoe UI", 10, "bold"), fg="#10b981", bg="#1e293b").pack(anchor="w", pady=(0, 8))

        cols = ("Model", "Aniqlik (Acc)", "Recall", "Specificity", "F1", "ROC-AUC", "5-Fold CV AUC")
        tree = ttk.Treeview(parent, columns=cols, show="headings", height=7)

        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=80 if col != "Model" else 140)

        for _, row in self.metrics_df.iterrows():
            tree.insert("", tk.END, values=(
                row["Model"],
                f"{row['Accuracy']*100:.1f}%",
                f"{row['Recall (Sensitivity)']*100:.1f}%",
                f"{row['Specificity']*100:.1f}%",
                f"{row['F1-Score']:.3f}",
                f"{row['ROC-AUC (Test)']:.3f}",
                row["5-Fold CV ROC-AUC"]
            ))

        tree.pack(fill=tk.BOTH, expand=True)

    def build_plots_tab(self, parent):
        top_bar = tk.Frame(parent, bg="#1e293b")
        top_bar.pack(fill=tk.X, pady=(0, 8))

        tk.Label(top_bar, text="Grafikni tanlang:", font=("Segoe UI", 9, "bold"), fg="#f8fafc", bg="#1e293b").pack(side=tk.LEFT, padx=(0, 8))

        self.plot_combo = ttk.Combobox(top_bar, values=[
            "01_pca_clusters.png (PCA 2D Klasterlash)",
            "02_volcano_plot.png (DEG Volcano Plot)",
            "03_heatmap_top_biomarkers.png (Top Biomarkerlar Heatmap)",
            "04_xgboost_feature_importance.png (Genlar Ahamiyati)",
            "05_gene_expression_boxplots.png (Gen Ifodalanish Boxplotlari)",
            "06_confusion_matrices.png (Xatolik Matritsasi)",
            "07_roc_curves_comparison.png (ROC Egri Chiziqlari)"
        ], state="readonly", width=45)
        self.plot_combo.current(0)
        self.plot_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.plot_combo.bind("<<ComboboxSelected>>", self.display_selected_plot)

        btn_full = tk.Button(top_bar, text="🔍 Kattalashtirib Ko'rish", command=self.open_full_image_external,
                             bg="#0284c7", fg="#ffffff", font=("Segoe UI", 8, "bold"), relief="flat", padx=8)
        btn_full.pack(side=tk.LEFT)

        self.plot_image_lbl = tk.Label(parent, bg="#0f172a", text="Grafik yuklanmoqda...")
        self.plot_image_lbl.pack(fill=tk.BOTH, expand=True)

        self.display_selected_plot()

    def build_export_tab(self, parent):
        tk.Label(parent, text="Klinik Diagnostik Xulosa va Tibbiy Dalolatnoma (Report):",
                 font=("Segoe UI", 10, "bold"), fg="#38bdf8", bg="#1e293b").pack(anchor="w", pady=(0, 6))

        self.txt_report = tk.Text(parent, bg="#0f172a", fg="#f1f5f9", font=("Consolas", 9), relief="solid", bd=1, padx=8, pady=8)
        self.txt_report.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        btn_row = tk.Frame(parent, bg="#1e293b")
        btn_row.pack(fill=tk.X)

        exp_btn = tk.Button(btn_row, text="💾 Hisobotni Faylga Saqlash (.txt)", command=self.save_report_file,
                            bg="#10b981", fg="#ffffff", font=("Segoe UI", 9, "bold"), relief="flat", padx=12, pady=6)
        exp_btn.pack(side=tk.LEFT, padx=(0, 10))

        copy_btn = tk.Button(btn_row, text="📋 Nusxalash (Clipboard)", command=self.copy_report_clipboard,
                             bg="#334155", fg="#f8fafc", font=("Segoe UI", 9), relief="flat", padx=12, pady=6)
        copy_btn.pack(side=tk.LEFT)

    def display_selected_plot(self, event=None):
        try:
            sel_text = self.plot_combo.get()
            filename = sel_text.split(" ")[0]
            img_path = os.path.join(base_dir, "results", "figures", filename)

            if os.path.exists(img_path):
                img = Image.open(img_path)
                # Resize to fit tab
                img.thumbnail((620, 360), Image.Resampling.LANCZOS)
                self.tk_plot_img = ImageTk.PhotoImage(img)
                self.plot_image_lbl.configure(image=self.tk_plot_img, text="")
            else:
                self.plot_image_lbl.configure(image="", text="Grafik fayli topilmadi: " + filename)
        except Exception as e:
            self.plot_image_lbl.configure(image="", text="Xatolik: " + str(e))

    def open_full_image_external(self):
        sel_text = self.plot_combo.get()
        filename = sel_text.split(" ")[0]
        img_path = os.path.join(base_dir, "results", "figures", filename)
        if os.path.exists(img_path):
            os.startfile(img_path)

    def on_slider_move(self, val, lbl):
        lbl.configure(text=f"{float(val):+0.2f}")
        # Run prediction dynamically
        self.run_prediction()

    def select_random_patient(self):
        random_id = random.choice(list(self.X_test.index))
        self.patient_combo.set(random_id)
        self.on_patient_change()

    def on_patient_change(self, event=None):
        self.current_patient_id = self.patient_combo.get()
        self.reset_current_patient_values()

    def reset_current_patient_values(self):
        pat_id = self.current_patient_id
        clin = self.clin_raw.loc[pat_id]
        idx_in_test = list(self.X_test.index).index(pat_id)
        actual_label = "Tumor (Xavfli o'sma)" if self.y_test[idx_in_test] == 1 else "Normal (Sog'lom to'qima)"

        age = clin['Age'] if 'Age' in clin else 55
        gender = clin['Gender'] if 'Gender' in clin else "Ayol"
        cohort = clin['Cohort'] if 'Cohort' in clin else clin.get('Data_Source', "TCGA-BRCA / GEO")
        stage = clin['Stage'] if 'Stage' in clin else "Noma'lum"

        self.lbl_patient_info.configure(
            text=f"Bemor ID: {pat_id} | Yosh: {age} | Jins: {gender} | Kohorta: {cohort}\n"
                 f"Klinik Bosqich: {stage} | Asl Tashxis: {actual_label}"
        )

        patient_vals = self.X_test.loc[pat_id]
        for gene in self.top_genes:
            val = float(patient_vals[gene])
            self.gene_vars[gene].set(round(val, 2))

        self.run_prediction()

    def run_prediction(self):
        try:
            # Construct patient gene vector
            pat_id = self.current_patient_id
            curr_row = self.X_test.loc[[pat_id]].copy()

            # Override with slider values (with security bounding)
            for gene in self.top_genes:
                val = float(self.gene_vars[gene].get())
                curr_row.loc[pat_id, gene] = max(-5.0, min(5.0, val))

            # Selected model
            model_name = self.model_combo.get()
            model = self.models.get(model_name, self.models["XGBoost"])

            # Predict
            prob_tumor = float(model.predict_proba(curr_row)[0, 1])
            is_tumor = prob_tumor >= 0.5
            conf = max(prob_tumor, 1 - prob_tumor) * 100

            idx_in_test = list(self.X_test.index).index(pat_id)
            actual_label = "Tumor (Xavfli)" if self.y_test[idx_in_test] == 1 else "Normal (Sog'lom)"

            # Update UI Badge
            if is_tumor:
                self.lbl_diagnosis_badge.configure(text="⚠️ TASHXIS: TUMOR (XAVFLI O'SMA)", bg="#ef4444")
                self.lbl_prob_text.configure(text=f"Saraton Ehtimolligi: {prob_tumor * 100:.1f}% (Yuqori Xavf)", fg="#ef4444")
            else:
                self.lbl_diagnosis_badge.configure(text="✅ TASHXIS: NORMAL (SOG'LOM / REMISSIYA)", bg="#10b981")
                self.lbl_prob_text.configure(text=f"Saraton Ehtimolligi: {prob_tumor * 100:.1f}% (Xavfsiz)", fg="#10b981")

            self.lbl_conf_text.configure(
                text=f"Model: {model_name} | Ishonchlilik: {conf:.1f}% | Asl Klinik Holati: {actual_label}"
            )

            # Update Progress Bar
            bar_w = int(280 * prob_tumor)
            color = "#ef4444" if prob_tumor > 0.5 else "#10b981"
            self.prob_canvas.coords(self.prob_bar, 0, 0, bar_w, 14)
            self.prob_canvas.itemconfig(self.prob_bar, fill=color)

            # Targeted Therapy recommendation
            vegfa_val = self.gene_vars["VEGFA"].get()
            erbb2_val = self.gene_vars["ERBB2"].get()
            ccnd1_val = self.gene_vars["CCND1"].get()
            brca1_val = self.gene_vars["BRCA1"].get()

            rec_list = []
            if is_tumor:
                if vegfa_val > 0.4:
                    rec_list.append("• VEGFA giper-ekspressiya: Bevacizumab (Avastin) - Angiogenez vaskulyarizatsiyasini to'xtatish;")
                if erbb2_val > 0.3:
                    rec_list.append("• HER2/ERBB2 amplifikatsiyasi: Trastuzumab (Herceptin) monoklonal antitanasi tavsiya etiladi;")
                if ccnd1_val > 0.3:
                    rec_list.append("• Siklin D1 (CCND1) yuqori: Palbociclib (Ibrance) - CDK4/6 ingibitori hujayra bo'linishini to'xtatadi;")
                if brca1_val < -0.3:
                    rec_list.append("• BRCA1 yetishmovchiligi: Olaparib (Lynparza) - PARP-ingibitori bilan DNK reparatsiyasini nishonga olish;")
                if not rec_list:
                    rec_list.append("• Standart onkologik kimyoterapiya va doimiy transkriptomik monitoring tavsiya etiladi.")
            else:
                rec_list.append("• Genlar me'yoriy doirada. Maxsus kimyoterapiyaga ehtiyoj yo'q, 6 oylik profilaktik ko'rik kifoya.")

            self.lbl_therapy_recommendations.configure(text="\n".join(rec_list))

            # Update Biomarker Table
            self.update_biomarker_table()

            # Update Clinical Report Text
            self.generate_clinical_report(model_name, prob_tumor, is_tumor, conf, actual_label, rec_list)

        except Exception as e:
            print(f"Bashoratda xatolik: {e}")

    def update_biomarker_table(self):
        for item in self.bio_tree.get_children():
            self.bio_tree.delete(item)

        bio_mechanisms = {
            "VEGFA": "O'sma angiogenezi va qon tomir o'sishi",
            "MMP9": "Matriks metalloproteinaza, metastaz va invaziya",
            "CCND1": "Siklin D1, G1/S hujayra siklini faollashtirish",
            "ERBB2": "HER2 retseptori, o'sish signallari giperaktivligi",
            "MKI67": "Ki-67 proliferatsiya va o'sma o'sish sur'ati",
            "AURKA": "Mitoz shpindeli va xromosoma barqarorligi",
            "CDKN2A": "p16/p14 o'sma supressori, siklni to'xtatish",
            "MYC": "Onkogen transkripsiya omili, metabolizm",
            "BRCA1": "DNK reparatsiyasi va homolog rekombinatsiya",
            "CDH1": "E-kadherin hujayra yopishishi va metastaz to'sig'i"
        }

        for gene in self.top_genes:
            r = self.imp_df[self.imp_df["Gene"] == gene].iloc[0]
            val = self.gene_vars[gene].get()
            self.bio_tree.insert("", tk.END, values=(
                gene,
                f"{r['XGBoost_Importance']*100:.1f}%",
                f"{r['RandomForest_Importance']*100:.1f}%",
                f"{val:+0.2f}",
                bio_mechanisms.get(gene, "Onkogen regulyatsiya")
            ))

    def generate_clinical_report(self, model_name, prob, is_tumor, conf, actual, therapies):
        clin = self.clin_raw.loc[self.current_patient_id]
        age = clin['Age'] if 'Age' in clin else 55
        gender = clin['Gender'] if 'Gender' in clin else "Ayol"
        cohort = clin['Cohort'] if 'Cohort' in clin else clin.get('Data_Source', "TCGA-BRCA / GEO")
        stage = clin['Stage'] if 'Stage' in clin else "Noma'lum"

        report = f"""================================================================================
          BIOINFORMATIKA VA ONKOLOGIYA: RASMIY DIAGNOSTIK DALOLATNOMA
               TCGA-BRCA / GEO TRANSKRIPTOMIK TAHLIL XULOSASI
================================================================================
Bemor ID        : {self.current_patient_id}
Bemor Yoshi     : {age} yosh | Jinsi: {gender}
Klinik Kohorta  : {cohort}
Klinik Bosqich  : {stage}
Tahlil Qilingan : 200 ta Differensial Gen Ekspressiyasi Profili (Z-score)
Asl Statusi     : {actual}
--------------------------------------------------------------------------------
MASHINALI O'QITISH DIAGNOSTIK XULOSASI:
Algoritm        : {model_name} Classifier (5-Fold Cross-Validated)
Bashorat        : {'TUMOR (XAVFLI OʻSMA TOʻQIMASI)' if is_tumor else 'NORMAL (SOGʻLOM TOʻQIMA)'}
Saraton Ehtimoli: {prob * 100:.2f}%
Model Ishonchi  : {conf:.2f}%
Xavf Darajasi   : {'YUQORI VA KRITIK XAVF' if prob >= 0.5 else 'XAVFSIZ / ME’YORIY'}
--------------------------------------------------------------------------------
ASOSIY BIOMARKERLAR IFODALANISHI:
"""
        for gene in self.top_genes:
            val = self.gene_vars[gene].get()
            imp = self.imp_df[self.imp_df["Gene"] == gene]["XGBoost_Importance"].values[0] * 100
            status = "YUQORI (Overexpressed)" if val > 0.5 else ("PAST (Suppressed)" if val < -0.5 else "ME'YORIY")
            report += f"  • {gene:<8}: Z={val:+0.2f} [{status}] (Ahamiyati: {imp:.1f}%)\n"

        report += "--------------------------------------------------------------------------------\n"
        report += "MOLEKULYAR MAQSADLI TERAPIYA TAVSIYALARI:\n"
        for t in therapies:
            report += f"  {t}\n"

        report += """--------------------------------------------------------------------------------
Mas'ul Tadqiqotchilar: Ramanov Rustam va Sobirov Elmurod
Bioinformatika fani bo'yicha Kurs Loyihasi dasturiy ta'minoti.
================================================================================
"""
        self.txt_report.delete("1.0", tk.END)
        self.txt_report.insert("1.0", report)

    def save_report_file(self):
        content = self.txt_report.get("1.0", tk.END)
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=f"Diagnostik_Xulosa_{self.current_patient_id}.txt",
            filetypes=[("Matnli fayl", "*.txt"), ("Barcha fayllar", "*.*")]
        )
        if filename:
            # Security: Sanitize path
            filename = os.path.abspath(filename)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Saqlandi", f"Klinik xulosa muvaffaqiyatli saqlandi:\n{filename}")

    def copy_report_clipboard(self):
        content = self.txt_report.get("1.0", tk.END)
        self.clipboard_clear()
        self.clipboard_append(content)
        messagebox.showinfo("Nusxalandi", "Xulosa matni xotiraga (clipboard) nusxalandi!")

def launch_app():
    app = BioinfoClinicalApp()
    app.mainloop()

if __name__ == "__main__":
    launch_app()

