# -*- coding: utf-8 -*-
"""
Bioinformatika Loyihasi 13: To'liq Avtomatlashtirilgan Ishchi Zanjir (Master Pipeline)
Ushbu skript talab qilingan 7 bosqichli jarayonni boshidan oxirigacha avtomatik bajaradi:
Dataset -> Ma'lumotlarni yuklash -> Preprocessing -> Bioinformatik algoritm (DEG/PCA) ->
Tahlil/Model (XGBoost/RF/SVM) -> Vizualizatsiya -> Biologik interpretatsiya -> Xulosa
"""

import os
import sys
import time
sys.stdout.reconfigure(encoding='utf-8')

base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from src.data_loader import generate_or_load_tcga_geo_dataset
from src.preprocessing import preprocess_bio_data
from src.bio_analysis import run_differential_expression_analysis
from src.ml_pipeline import train_and_evaluate_models
from src.visualization import generate_all_visualizations
from src.bio_interpretation import run_biological_interpretation

def main():
    t0 = time.time()
    print("=" * 80)
    print("   BIOINFORMATIKA KURS LOYIHASI: 13-MAVZU")
    print("   BIOLOGIK MA'LUMOTLAR ASOSIDA KASALLIKLARNI MASHINALI O'QITISH YORDAMIDA")
    print("   BASHORATLASH (GEO/TCGA, scikit-learn, XGBoost)")
    print("   Mualliflar: Ramanov Rustam va Sobirov Elmurod")
    print("=" * 80)

    print("\n>>> BOSQICH 1: Dataset va biologik ma'lumotlarni yuklash...")
    generate_or_load_tcga_geo_dataset(data_dir=os.path.join(base_dir, "data", "raw"))

    print("\n>>> BOSQICH 2: Preprocessing (QC, Z-score, Dispersiya filtrlash, 80/20 Split)...")
    preprocess_bio_data(
        raw_data_dir=os.path.join(base_dir, "data", "raw"),
        processed_data_dir=os.path.join(base_dir, "data", "processed")
    )

    print("\n>>> BOSQICH 3: Bioinformatik tahlil (DEG - Differensial ekspressiya & PCA)...")
    run_differential_expression_analysis(base_dir=base_dir)

    print("\n>>> BOSQICH 4: Mashinali o'qitish modellari (XGBoost, RF, SVM, LR, KNN)...")
    train_and_evaluate_models(base_dir=base_dir)

    print("\n>>> BOSQICH 5: Vizualizatsiya (7 ta ilmiy 300 DPI grafiklar yaratish)...")
    generate_all_visualizations(target_dir=base_dir)

    print("\n>>> BOSQICH 6: Biologik interpretatsiya va onkologik mexanizmlar...")
    run_biological_interpretation(base_dir=base_dir)

    elapsed = time.time() - t0
    print("\n" + "=" * 80)
    print(f"[✓] TO'LIQ BIOINFORMATIK VA ML PIPELINE MUVAFFAQIYATLI YAKUNLANDI! ({elapsed:.1f} soniya)")
    print(f"    - Barcha natijalar 'results/' va 'data/' jildlarida saqlandi.")
    print("=" * 80)

if __name__ == "__main__":
    main()

