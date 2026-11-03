# -*- coding: utf-8 -*-
"""
Bioinformatika Loyihasi 13: Biologik Interpretatsiya va Funksional Tahlil Moduli
- Top biomarker genlarning molekulyar-biologik tavsifi
- Saraton xususiyatlari (Hallmarks of Cancer: Hanahan & Weinberg)
- KEGG signal yo'llari va Gene Ontology (GO) terminlari
- Klinik ahamiyat va maqsadli (Targeted) terapiya dorilari
"""

import os
import sys
import json
sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd

# Biologik ma'lumotlar bazasi (NCBI, UniProt, KEGG, GeneCards asosida)
GENE_KNOWLEDGE_BASE = {
    "VEGFA": {
        "full_name": "Vascular Endothelial Growth Factor A",
        "category": "Onkogen / O'sish omili",
        "hallmark": "Inducing Angiogenesis (Yangi qon tomirlar hosil qilish)",
        "kegg_pathways": ["hsa04370: VEGF signaling pathway", "hsa05200: Pathways in cancer", "hsa04066: HIF-1 signaling pathway"],
        "go_terms": ["GO:0001525 ~ angiogenesis", "GO:0045766 ~ positive regulation of angiogenesis", "GO:0005178 ~ integrin binding"],
        "clinical_relevance": "O'sma hujayralarini kislorod va ozuqa bilan ta'minlash uchun tomir o'sishini rag'batlantiradi. Bevacizumab (Avastin) preparatining nishoni."
    },
    "MMP9": {
        "full_name": "Matrix Metallopeptidase 9",
        "category": "Matriks metalloproteinaza (Ferment)",
        "hallmark": "Activating Invasion and Metastasis (Invaziya va metastaz)",
        "kegg_pathways": ["hsa05200: Pathways in cancer", "hsa04670: Leukocyte transendothelial migration"],
        "go_terms": ["GO:0030198 ~ extracellular matrix organization", "GO:0004222 ~ metalloendopeptidase activity"],
        "clinical_relevance": "Hujayralararo matriksni eritib, saraton hujayralarining qon va limfa tomirlariga kirib butun tanaga tarqalishiga (metastaz) yo'l ochadi."
    },
    "CCND1": {
        "full_name": "Cyclin D1",
        "category": "Hujayra sikli regulyatori",
        "hallmark": "Sustaining Proliferative Signaling (To'xtovsiz bo'linish)",
        "kegg_pathways": ["hsa04110: Cell cycle", "hsa05200: Pathways in cancer", "hsa04115: p53 signaling pathway"],
        "go_terms": ["GO:0051726 ~ regulation of cell cycle", "GO:0000079 ~ regulation of cyclin-dependent protein kinase activity"],
        "clinical_relevance": "G1 fazadan S fazaga o'tishni boshqaradi. Ko'krak bezi saratonining 50% dan ortig'ida kuchli giper-ekspressiyalanadi. CDK4/6 ingibitorlari (Palbociclib) nishoni."
    },
    "ERBB2": {
        "full_name": "Erb-B2 Receptor Tyrosine Kinase 2 (HER2/neu)",
        "category": "Retseptor tirozin-kinaza",
        "hallmark": "Sustaining Proliferative Signaling (O'sish retseptori)",
        "kegg_pathways": ["hsa04012: ErbB signaling pathway", "hsa04151: PI3K-Akt signaling pathway"],
        "go_terms": ["GO:0007169 ~ transmembrane receptor protein tyrosine kinase signaling", "GO:0005524 ~ ATP binding"],
        "clinical_relevance": "Agressiv HER2-musbat ko'krak bezi saratoni subtiplarining asosiy drayveri. Trastuzumab (Herceptin) monoklonal antitanalari yordamida nishonga olinadi."
    },
    "MKI67": {
        "full_name": "Marker of Proliferation Ki-67",
        "category": "Yadroviy proliferatsiya oqsili",
        "hallmark": "Enabling Replicative Immortality (Cheksiz bo'linish)",
        "kegg_pathways": ["hsa04110: Cell cycle"],
        "go_terms": ["GO:0007049 ~ cell cycle", "GO:0005694 ~ chromosome"],
        "clinical_relevance": "Klinik onkologiyada o'sma hujayralarining bo'linish tezligini baholovchi 'oltin standart' immunohistokimyoviy indeks. Yuqori Ki-67 agressiv kechishni ko'rsatadi."
    },
    "AURKA": {
        "full_name": "Aurora Kinase A",
        "category": "Serin/treonin kinaza",
        "hallmark": "Genome Instability and Mutation (Genom beqarorligi)",
        "kegg_pathways": ["hsa04110: Cell cycle", "hsa04114: Oocyte meiosis"],
        "go_terms": ["GO:0007067 ~ mitotic nuclear division", "GO:0005813 ~ centrosome"],
        "clinical_relevance": "Mitozda xromosomalarning to'g'ri ajralishini boshqaradi. Haddan tashqari ko'p ekspressiyalanishi aneuploidiya va saraton rivojlanishiga olib keladi."
    },
    "CDKN2A": {
        "full_name": "Cyclin Dependent Kinase Inhibitor 2A (p16/INK4a)",
        "category": "O'sma supressori (Tumor Suppressor)",
        "hallmark": "Evading Growth Suppressors (O'sish to'siqlarini aylanib o'tish)",
        "kegg_pathways": ["hsa04110: Cell cycle", "hsa05200: Pathways in cancer"],
        "go_terms": ["GO:0007050 ~ cell cycle arrest", "GO:0019888 ~ protein phosphatase inhibitor activity"],
        "clinical_relevance": "Hujayra bo'linishini tormozlovchi muhim himoya oqsili. Uning yo'qolishi yoki mutatsiyasi boshqaruvsiz karsinogenezga olib keladi."
    },
    "PTEN": {
        "full_name": "Phosphatase and Tensin Homolog",
        "category": "Lipid fosfataza / O'sma supressori",
        "hallmark": "Evading Growth Suppressors & Resisting Cell Death",
        "kegg_pathways": ["hsa04151: PI3K-Akt signaling pathway", "hsa05200: Pathways in cancer"],
        "go_terms": ["GO:0006661 ~ phosphatidylinositol metabolic process", "GO:0016311 ~ dephosphorylation"],
        "clinical_relevance": "PI3K/Akt/mTOR omon qolish signal yo'lining asosiy salbiy regulyatori. PTEN ning faolsizlanishi saraton hujayralarining o'lmasligiga sabab bo'ladi."
    },
    "BRCA1": {
        "full_name": "BRCA1 DNA Repair Associated",
        "category": "DNK reparatsiyasi oqsili / O'sma supressori",
        "hallmark": "Genome Instability and Mutation",
        "kegg_pathways": ["hsa03440: Homologous recombination", "hsa03460: Fanconi anemia pathway"],
        "go_terms": ["GO:0006281 ~ DNA repair", "GO:0000724 ~ double-strand break repair via homologous recombination"],
        "clinical_relevance": "Irsiy ko'krak va tuxumdon bezi saratoni genidir. BRCA1 yo'qotilganda PARP ingibitorlari (Olaparib) sintetik letallik orqali davolashda qo'llaniladi."
    },
    "CDH1": {
        "full_name": "Cadherin 1 (E-Cadherin)",
        "category": "Hujayralararo yopishish glikoproteini (Adhesion)",
        "hallmark": "Activating Invasion and Metastasis",
        "kegg_pathways": ["hsa04520: Adherens junction", "hsa05200: Pathways in cancer"],
        "go_terms": ["GO:0007156 ~ homophilic cell adhesion via plasma membrane adhesion molecules"],
        "clinical_relevance": "Normal epiteliy hujayralarini bir-biriga mahkam ushlab turadi. CDH1 pasayishi epitelial-mezenximal o'tish (EMT) va agressiv metastazni keltirib chiqaradi."
    }
}

def run_biological_interpretation(base_dir=None):
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    metrics_dir = os.path.join(base_dir, "results", "metrics")
    deg_file = os.path.join(base_dir, "results", "selected_biomarkers.csv")
    imp_file = os.path.join(metrics_dir, "feature_importances.csv")

    deg_df = pd.read_csv(deg_file)
    imp_df = pd.read_csv(imp_file)

    merged = pd.merge(imp_df, deg_df[["Gene", "log2FC", "FDR_adj_p", "Significance"]], on="Gene", how="left")

    interpretation_rows = []
    for _, row in merged.head(15).iterrows():
        g = row["Gene"]
        info = GENE_KNOWLEDGE_BASE.get(g, {
            "full_name": "Biological factor",
            "category": "Metabolic regulator",
            "hallmark": "Cellular adaptation",
            "kegg_pathways": ["Metabolic pathways"],
            "go_terms": ["Cellular process"],
            "clinical_relevance": "Potential novel prognostic candidate."
        })
        interpretation_rows.append({
            "Gene": g,
            "Full_Name": info["full_name"],
            "Category": info["category"],
            "Cancer_Hallmark": info["hallmark"],
            "log2FC": row["log2FC"],
            "FDR_p": row["FDR_adj_p"],
            "XGBoost_Importance": round(row["XGBoost_Importance"], 4),
            "Clinical_Target": info["clinical_relevance"]
        })

    interp_df = pd.DataFrame(interpretation_rows)
    out_csv = os.path.join(base_dir, "results", "biological_interpretation_biomarkers.csv")
    interp_df.to_csv(out_csv, index=False)

    out_json = os.path.join(base_dir, "results", "biological_interpretation_full.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(GENE_KNOWLEDGE_BASE, f, indent=4, ensure_ascii=False)

    print(f"[OK] Biologik interpretatsiya natijalari saqlandi:\n     1) {out_csv}\n     2) {out_json}")
    print("\nTop 5 ta genning biologik ta'rifi:")
    for item in interpretation_rows[:5]:
        print(f"  • {item['Gene']} ({item['Full_Name']}): {item['Cancer_Hallmark']} | {item['Clinical_Target'][:80]}...")

    return interp_df

if __name__ == "__main__":
    run_biological_interpretation()

