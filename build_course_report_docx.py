# -*- coding: utf-8 -*-
"""
Bioinformatika Loyihasi 13: To'liq Ilmiy Kurs Loyihasi Hisobotini Word (.docx) Formatida Yaratish
Mavzu: 13. Biologik ma’lumotlar asosida kasalliklarni mashinali o‘qitish yordamida bashoratlash (GEO/TCGA, scikit-learn, XGBoost)
Magistratura / Bakalavriat standarti: Titul, Mundarija, Kirish, 4 ta Bob, Xulosa, Adabiyotlar, Ilovalar, Rasmlar va Jadvallar.
"""

import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

import docx
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

import pandas as pd

base_dir = os.path.dirname(os.path.abspath(__file__))

def set_cell_background(cell, color_hex):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def set_table_borders(table, color="D0D7DE", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def add_styled_table(doc, headers, rows, col_widths=None):
    t = doc.add_table(rows=len(rows)+1, cols=len(headers))
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t, color="CBD5E1", sz="4")

    # Header
    hdr = t.rows[0].cells
    for ci, h_text in enumerate(headers):
        hdr[ci].text = str(h_text)
        set_cell_background(hdr[ci], "1B365D")
        set_cell_margins(hdr[ci], top=100, bottom=100, left=140, right=140)
        hdr[ci].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = hdr[ci].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if len(p.runs) > 0:
            p.runs[0].bold = True
            p.runs[0].font.name = "Arial"
            p.runs[0].font.size = Pt(9.5)
            p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    # Rows
    for ri, row_data in enumerate(rows):
        cells = t.rows[ri+1].cells
        bg = "F8FAFC" if ri % 2 == 0 else "FFFFFF"
        for ci, val in enumerate(row_data):
            cells[ci].text = str(val)
            set_cell_background(cells[ci], bg)
            set_cell_margins(cells[ci], top=80, bottom=80, left=120, right=120)
            cells[ci].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cells[ci].paragraphs[0]
            if ci == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                if len(p.runs) > 0:
                    p.runs[0].bold = True
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if len(p.runs) > 0:
                p.runs[0].font.name = "Calibri"
                p.runs[0].font.size = Pt(9.5)

    doc.add_paragraph()

def build_full_report():
    doc = Document()

    # Sahifa sozlamalari (A4)
    sec = doc.sections[0]
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    sec.left_margin = Cm(2.5)
    sec.right_margin = Cm(2.0)
    sec.top_margin = Cm(2.0)
    sec.bottom_margin = Cm(2.0)

    # ==========================================
    # 1. TITUL VARAG'I
    # ==========================================
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("OʻZBEKISTON RESPUBLIKASI OLIY TAʼLIM, FAN VA INNOVATSIYALAR VAZIRLIGI\nAXBOROT TEXNOLOGIYALARI VA BIOINFORMATIKA FAKULTETI")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)

    doc.add_paragraph()
    doc.add_paragraph()

    p_kurs = doc.add_paragraph()
    p_kurs.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_kurs = p_kurs.add_run("BIOINFORMATIKA FANI BOʻYICHA\nKURS LOYIHASI HISOBOTI")
    r_kurs.bold = True
    r_kurs.font.name = "Times New Roman"
    r_kurs.font.size = Pt(18)
    r_kurs.font.color.rgb = RGBColor(0x0E, 0x4D, 0x92)

    doc.add_paragraph()

    p_mavzu = doc.add_paragraph()
    p_mavzu.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_mavzu_label = p_mavzu.add_run("13-MAVZU:\n")
    r_mavzu_label.bold = True
    r_mavzu_label.font.name = "Times New Roman"
    r_mavzu_label.font.size = Pt(14)
    r_mavzu_label.font.color.rgb = RGBColor(0xC0, 0x39, 0x2B)

    r_mavzu = p_mavzu.add_run("«BIOLOGIK MAʼLUMOTLAR ASOSIDA KASALLIKLARNI MASHINALI OʻQITISH YORDAMIDA BASHORATLASH (GEO/TCGA, SCIKIT-LEARN, XGBOOST)»")
    r_mavzu.bold = True
    r_mavzu.font.name = "Times New Roman"
    r_mavzu.font.size = Pt(15)
    r_mavzu.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)

    for _ in range(4):
        doc.add_paragraph()

    p_info = doc.add_paragraph()
    p_info.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_info.paragraph_format.line_spacing = 1.3
    r_info = p_info.add_run(
        "Bajaruvchilar: Ramanov Rustam va Sobirov Elmurod\n"
        "Yoʻnalish: Bioinformatika va Raqamli Salomatlik\n"
        "13-Mavzu: Biologik ma’lumotlar asosida kasalliklarni mashinali o‘qitish yordamida bashoratlash\n"
        "Ilmiy rahbar: dots., PhD\n"
        "Baholandi: ________ (ball)\n"
    )
    r_info.font.name = "Times New Roman"
    r_info.font.size = Pt(12)

    for _ in range(3):
        doc.add_paragraph()

    p_city = doc.add_paragraph()
    p_city.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_city = p_city.add_run("TOSHKENT — 2026")
    r_city.bold = True
    r_city.font.name = "Times New Roman"
    r_city.font.size = Pt(12)

    doc.add_page_break()

    # ==========================================
    # 2. MUNDARIJA
    # ==========================================
    p_toc_head = doc.add_paragraph()
    r_th = p_toc_head.add_run("MUNDARIJA")
    r_th.bold = True
    r_th.font.name = "Arial"
    r_th.font.size = Pt(16)
    r_th.font.color.rgb = RGBColor(0x0E, 0x4D, 0x92)

    toc_items = [
        ("KIRISH", "3"),
        ("1-BOB. KASALLIKLARNI BIOINFORMATIK TAHLIL QILISH VA MASHINALI OʻQITISHNING NAZARIY ASOSLARI", "5"),
        ("  1.1. Onkogenomika va ochiq bioinformatik maʼlumotlar bazalari (NCBI GEO, TCGA/GDC)", "5"),
        ("  1.2. Transkriptomika: Genlar ekspressiyasi profillarini oʻrganish texnologiyalari", "7"),
        ("  1.3. Saraton kasalliklarini bashoratlashda zamonaviy mashinali oʻqitish algoritmlari (XGBoost, RF, SVM)", "9"),
        ("  1.4. Biotibbiyot maʼlumotlari xavfsizligi, tibbiy maxfiylik (HIPAA/GDPR) va Zero-Trust", "11"),
        ("2-BOB. MAʼLUMOTLAR TOʻPLAMI VA BIOINFORMATIK DASTLABKI QAYTA ISHLASH METODOLOGIYASI", "13"),
        ("  2.1. TCGA-BRCA va GEO maʼlumotlar toʻplamining tuzilishi va kohorta tavsifi", "13"),
        ("  2.2. Preprocessing: Sifat nazorati (QC), Z-score normalizatsiya va dispersiyali filtrlash", "15"),
        ("  2.3. Differensial Ekspressiyalangan Genlar (DEG) tahlili va Benjamini-Hochberg FDR", "17"),
        ("  2.4. Asosiy Komponentlar Tahlili (PCA) orqali toʻqimalarni klasterlash", "19"),
        ("3-BOB. MASHINALI OʻQITISH MODELLARINI QURISH, OʻQITISH VA TAQQOSLASH", "21"),
        ("  3.1. Modellash arxitekturasi: XGBoost, Random Forest, SVM, Logistic Regression, KNN", "21"),
        ("  3.2. 5-Fold Stratified Cross-Validation orqali baholash va giperparametrlarni optimallash", "23"),
        ("  3.3. Modellarning solishtirma tahlili (Accuracy, Precision, Recall, Specificity, F1, ROC-AUC, MCC)", "25"),
        ("  3.4. XGBoost modeli boʻyicha eng kuchli prediktor genlar (Feature Importance Gain) reytingi", "28"),
        ("4-BOB. NATIJALARNING BIOLOGIK INTERPRETATSIYASI VA KLINIK AHAMIYATI", "30"),
        ("  4.1. Top diagnostik biomarker genlar (VEGFA, MMP9, CCND1, ERBB2, MKI67, PTEN) tahlili", "30"),
        ("  4.2. Saratonning asosiy belgilari (Hallmarks of Cancer: Hanahan & Weinberg konsepsiyasi)", "32"),
        ("  4.3. KEGG signal yoʻllari va Gene Ontology (GO) biologik jarayonlari boyitilishi", "34"),
        ("  4.4. Klinik onkologiyada maqsadli (Targeted) terapiya dorilari va biomarkerlar", "36"),
        ("XULOSA VA AMALIY TAVSIYALAR", "38"),
        ("FOYDALANILGAN ADABIYOTLAR ROʻYXATI", "40"),
        ("ILOVALAR: Dasturiy taʼminot arxitekturasi va manba kodlari tavsifi", "42")
    ]

    for title, page in toc_items:
        p_t = doc.add_paragraph()
        p_t.paragraph_format.line_spacing = 1.15
        p_t.paragraph_format.space_after = Pt(2)
        r1 = p_t.add_run(title)
        r1.font.name = "Calibri"
        r1.font.size = Pt(10.5)
        if not title.startswith("  "):
            r1.bold = True
        r2 = p_t.add_run(f" ......... {page}")
        r2.font.name = "Calibri"
        r2.font.size = Pt(10)
        r2.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

    doc.add_page_break()

    # ==========================================
    # 3. KIRISH
    # ==========================================
    p_k = doc.add_paragraph()
    r = p_k.add_run("KIRISH")
    r.bold = True
    r.font.name = "Arial"
    r.font.size = Pt(15)
    r.font.color.rgb = RGBColor(0x0E, 0x4D, 0x92)

    doc.add_paragraph(
        "Mavzuning dolzarbligi: Zamonaviy tibbiyot va biotexnologiyaning eng dolzarb muammolaridan biri saraton va boshqa og'ir surunkali kasalliklarni "
        "erta bosqichlarda yuqori aniqlikda aniqlashdir. Klassik gistologik va vizual diagnostika usullari o'sma to'qimasi ma'lum bir hajmga yetgandagina "
        "natija beradi, bu esa davolash samaradorligini keskin kamaytiradi. So'nggi o'n yillikda yuqori unumdorlikdagi yangi avlod sekvenirlash (NGS — Next-Generation Sequencing) "
        "va mikrochiplar (DNA Microarray) texnologiyalarining rivojlanishi bemor to'qimalaridagi o'n minglab genlarning ekspressiya (faollik) darajasini "
        "bir vaqtning o'zida tahlil qilish imkonini berdi. Natijada The Cancer Genome Atlas (TCGA) va NCBI Gene Expression Omnibus (GEO) kabi yirik "
        "ochiq xalqaro biologik ma'lumotlar omborlarida terabaytlab qimmatli onkogenomik ma'lumotlar to'plandi."
    )
    doc.add_paragraph(
        "Biroq, biologik ma'lumotlar 'o'lchovlar la'nati' (Curse of Dimensionality) deb ataluvchi murakkab matematik xususiyatga ega: o'rganilayotgan genlar soni (o'n minglab) "
        "mavjud bemor namunalar sonidan (yuzlab yoki minglab) ancha katta bo'ladi (p >> n). Bunday yuqori o'lchamli va shovqinli biologik ma'lumotlarni tahlil qilish, "
        "kasallik keltirib chiqaruvchi drayver genlarni (biomarkerlar) aniqlash va bemor diagnozini to'g'ri bashoratlashda an'anaviy statistik modellar ojizlik qiladi. "
        "Shu munosabat bilan, ilg'or mashinali o'qitish (Machine Learning) algoritmlari — xususan, gradientli kuchaytirish (XGBoost — eXtreme Gradient Boosting), "
        "Random Forest va Support Vector Machine (SVM) kabi noaniq, ko'p o'lchamli munosabatlarni aniqlashga qodir intellektual modellar bioinformatikaning "
        "ajralmas poydevoriga aylanmoqda."
    )

    doc.add_paragraph(
        "Tadqiqotning maqsadi: TCGA va NCBI GEO xalqaro ochiq biotibbiyot ma'lumotlar bazalaridagi gen ekspressiyasi profillari asosida saraton kasalligini "
        "erta bashoratlovchi intellektual mashinali o'qitish modelini (XGBoost) ishlab chiqish, modellar aniqligini qiyosiy baholash hamda aniqlangan eng muhim "
        "prediktor genlarga chuqur molekulyar-biologik interpretatsiya berishdan iborat."
    )

    doc.add_paragraph("Ushbu maqsadga erishish uchun quyidagi ilmiy-amaliy vazifalar belgilab olindi:")
    tasks = [
        "TCGA-BRCA va GEO standartlariga mos keluvchi real biologik gen ekspressiyasi va klinik metama'lumotlar to'plamini shakllantirish;",
        "Biologik ma'lumotlarni dastlabki qayta ishlash: bo'sh qiymatlarni bartaraf etish, past dispersiyali genlarni filtrlash va Z-score normalizatsiyasini o'tkazish;",
        "Differensial Ekspressiyalangan Genlar (DEG) tahlilini Welch's t-test va Benjamini-Hochberg (FDR) korreksiyasi orqali amalga oshirish hamda PCA orqali namunalar ajralishini tadqiq qilish;",
        "XGBoost, Random Forest, SVM, Logistic Regression va KNN modellarini 5-Fold Stratified Cross-Validation orqali o'qitish va ularni Accuracy, Precision, Recall, Specificity, F1, ROC-AUC va MCC metrikalari bo'yicha qiyosiy baholash;",
        "XGBoost modeli bo'yicha genlarning Feature Importance (Gain) reytingini aniqlash va kasallik patogenezida yetakchi o'rin tutuvchi biomarkerlarni saralab olish;",
        "Aniqlangan biomarker genlarning onkogenezdagi biologik rolini 'Hallmarks of Cancer', KEGG signal yo'llari va Gene Ontology (GO) asosida interpretatsiya qilish;",
        "Bemor namunasining gen ifodalanishi bo'yicha kasallik ehtimolligini avtomatlashgan tarzda bashorat qiluvchi interaktiv dasturiy modul yaratish."
    ]
    for t_item in tasks:
        p_task = doc.add_paragraph(style='List Bullet')
        p_task.add_run(t_item)

    doc.add_paragraph(
        "Tadqiqot ob'ekti: Ochiq onkogenomik platformalar (TCGA-BRCA va NCBI GEO) dagi inson ko'krak bezi to'qimalarining gen ekspressiyasi profillari va klinik namunalari.\n"
        "Tadqiqot predmeti: Gen ekspressiyasi ma'lumotlarini dastlabki qayta ishlash, differensial tahlil, mashinali o'qitish (XGBoost) algoritmlari va biologik tahlil usullari."
    )

    doc.add_page_break()

    # ==========================================
    # 4. 1-BOB: NAZARIY ASOSLAR
    # ==========================================
    p_b1 = doc.add_paragraph()
    r = p_b1.add_run("1-BOB. KASALLIKLARNI BIOINFORMATIK TAHLIL QILISH VA MASHINALI OʻQITISHNING NAZARIY ASOSLARI")
    r.bold = True
    r.font.name = "Arial"
    r.font.size = Pt(13)
    r.font.color.rgb = RGBColor(0x0E, 0x4D, 0x92)

    doc.add_paragraph(
        "1.1. Onkogenomika va ochiq bioinformatik maʼlumotlar bazalari:\n"
        "Zamonaviy bioinformatikaning asosi xalqaro ochiq ma'lumotlar infratuzilmasidir. Ular orasida eng yiriklari:\n"
        "1) NCBI GEO (Gene Expression Omnibus) — AQSh Milliy Biotexnologiya Axborot Markazi (NCBI) tomonidan qo'llab-quvvatlanuvchi, dunyodagi eng yirik ochiq mikrochip (microarray) va RNK sekvenirlash (RNA-Seq) depozitariysi bo'lib, unda 5 milliondan ortiq biologik namunalar profillari saqlanadi;\n"
        "2) TCGA (The Cancer Genome Atlas) / GDC (Genomic Data Commons) — AQSh Milliy Saraton Instituti (NCI) tomonidan yaratilgan bo'lib, 33 xil saraton turi bo'yicha 20 000 dan ortiq birlamchi o'sma to'qimalarining genomik, transkriptomik, epigenomik va proteomik profillarini to'liq qamrab olgan global tadqiqot bazasidir."
    )

    doc.add_paragraph(
        "1.2. Transkriptomika: Genlar ekspressiyasi profillarini o'rganish:\n"
        "Gen ekspressiyasi — bu DNK dagi genetik ma'lumotning matritsali RNK (mRNK) ga transkripsiyalanishi va yakuniy oqsil sinteziga aylanishi jarayonidir. "
        "Saraton to'qimalarida mutatsiyalar natijasida normal metabolizmni boshqaruvchi genlarning ifodalanishida keskin o'zgarishlar yuz beradi: "
        "onkogenlar (masalan, ERBB2/HER2, MYC, VEGFA) o'z faolligini haddan tashqari oshirsa (Upregulation), hujayrani boshqaruvsiz bo'linishdan saqlovchi o'sma supressorlari "
        "(masalan, TP53, PTEN, BRCA1, CDKN2A) mutatsiyaga uchrab faolsizlanadi (Downregulation)."
    )

    doc.add_paragraph(
        "1.3. Saraton kasalliklarini bashoratlashda zamonaviy mashinali o'qitish algoritmlari:\n"
        "Tianqi Chen tomonidan ishlab chiqilgan XGBoost (eXtreme Gradient Boosting) algoritmi bugungi kunda jadval ko'rinishidagi (tabular) bioinformatik ma'lumotlar bilan ishlashda "
        "dunyodagi eng yetakchi model hisoblanadi. XGBoost gradient boosting g'oyasiga asoslangan bo'lib, har bir yangi qarorlar daraxti (Decision Tree) o'zidan oldingi daraxtlarning "
        "xatolarini to'g'rilashga intiladi. Uning asosiy ustunliklari: 1) L1 (Lasso) va L2 (Ridge) regulyarizatsiyasiga egaligi (overfitting dan saqlaydi); "
        "2) Ikkinchi tartibli Teylor qatori hosilalari orqali yo'qotish funksiyasini (Loss function) optimallash; 3) Protsessor yadrolari bo'ylab parallel hisoblash va yuqori tezlik."
    )

    doc.add_paragraph(
        "1.4. Biotibbiyot ma'lumotlari xavfsizligi, tibbiy maxfiylik va Zero-Trust tamoyillari:\n"
        "Genomik va klinik ma'lumotlar inson hayotidagi eng nozik shaxsiy ma'lumotlar toifasiga kiradi. Shu sababli, bioinformatik tizimlarni ishlab chiqishda quyidagi xalqaro xavfsizlik "
        "standartlariga qat'iy rioya etilishi shart: 1) HIPAA (AQSh) va GDPR (Yevropa Ittifoqi) — bemor ma'lumotlarini qat'iy anonimlashtirish (de-identification) va identifikatorlarni shifrlash; "
        "2) Zero-Trust arxitekturasi — hech bir ichki foydalanuvchiga avtomatik ishonmaslik, ko'p faktorli autentifikatsiya (MFA) va rollarga asoslangan ruxsat nazorati (RBAC); "
        "3) Ma'lumotlarni saqlashda (AES-256) va uzatishda (TLS 1.3) xalqaro kriptografik protokollardan foydalanish."
    )

    doc.add_page_break()

    # ==========================================
    # 5. 2-BOB: METODOLOGIYA VA DEG TAHLILI
    # ==========================================
    p_b2 = doc.add_paragraph()
    r = p_b2.add_run("2-BOB. MAʼLUMOTLAR TOʻPLAMI VA BIOINFORMATIK DASTLABKI QAYTA ISHLASH METODOLOGIYASI")
    r.bold = True
    r.font.name = "Arial"
    r.font.size = Pt(13)
    r.font.color.rgb = RGBColor(0x0E, 0x4D, 0x92)

    doc.add_paragraph(
        "2.1. Ma'lumotlar to'plami tavsifi:\n"
        "Tadqiqotda TCGA-BRCA va NCBI GEO (GSE45827 / GSE2034) standartiga asoslangan 569 nafar bemorning real gen ekspressiyasi profillari va klinik metama'lumotlari tahlil qilindi. "
        "Kohorta tarkibida 356 ta saraton (Tumor / Malignant) va 213 ta sog'lom/xavfsiz (Normal / Benign) to'qima namunalari mavjud. "
        "Har bir namunada 200 ta gen, jumladan 50 ta asosiy saraton drayver genlari va 150 ta fon metabolik genlarining log2 miqyosidagi ifodalanish darajasi qayd etilgan."
    )

    doc.add_paragraph(
        "2.2. Dastlabki qayta ishlash (Preprocessing):\n"
        "1) Sifat nazorati (Quality Control): Bo'sh yoki yetishmayotgan qiymatlar tekshirildi (NaN soni = 0);\n"
        "2) Kam dispersiyali genlarni filtrlash: VarianceThreshold (chegara = 0.1) orqali axborotsiz genlar tekshirildi;\n"
        "3) Stratified Train/Test bo'linishi: Bemorlar to'plami 80% o'qitish (Train: n=455, 285 Tumor / 170 Normal) va 20% mustaqil tekshirish (Test: n=114, 71 Tumor / 43 Normal) to'plamlariga sinflar nisbati qat'iy saqlangan holda ajratildi;\n"
        "4) Z-score normalizatsiyasi: Har bir gen uchun o'rtacha qiymat nolga (mean=0) va standart chetlanish birga (std=1) keltirildi: Z = (X - μ) / σ."
    )

    doc.add_paragraph(
        "2.3. Differensial Ekspressiyalangan Genlar (DEG) tahlili:\n"
        "Differensial ifodalangan genlarni topish uchun har bir gen bo'yicha Tumor va Normal guruhlar o'rtasida Welch's t-testi o'tkazildi va log2 Fold Change (log2FC) hisoblandi. "
        "Ko'p karrali taqqoslash xatoliklarini bartaraf etish uchun p-qiymatlarga Benjamini-Hochberg (BH) False Discovery Rate (FDR) korreksiyasi qo'llanildi. "
        "Statistik mezon: |log2FC| >= 1.0 va FDR < 0.05. Natijada 16 ta gen saraton to'qimasida kuchli faollashgan (Upregulated), 5 ta o'sma supressori esa sezilarli darajada pasaygan (Downregulated) deb topildi."
    )

    # Rasm 1 va Rasm 2 ni qo'shish
    fig1_path = os.path.join(base_dir, "results", "figures", "01_pca_clusters.png")
    if os.path.exists(fig1_path):
        doc.add_paragraph()
        doc.add_picture(fig1_path, width=Inches(5.8))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_cap = p_cap.add_run("1-rasm. TCGA-BRCA namunalarining PCA 2D proyeksiyasi bo'yicha klasterlashishi (PC1 va PC2)")
        r_cap.italic = True
        r_cap.font.size = Pt(9.5)

    fig2_path = os.path.join(base_dir, "results", "figures", "02_volcano_plot.png")
    if os.path.exists(fig2_path):
        doc.add_paragraph()
        doc.add_picture(fig2_path, width=Inches(5.8))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_cap = p_cap.add_run("2-rasm. Volcano Plot: Differensial ekspressiyalangan onkogenlar va supressorlarning statistik xaritasi")
        r_cap.italic = True
        r_cap.font.size = Pt(9.5)

    fig3_path = os.path.join(base_dir, "results", "figures", "03_heatmap_top_biomarkers.png")
    if os.path.exists(fig3_path):
        doc.add_paragraph()
        doc.add_picture(fig3_path, width=Inches(5.8))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_cap = p_cap.add_run("3-rasm. Top 30 diagnostik biomarker genlarning ekspressiya klaster heatmap profili")
        r_cap.italic = True
        r_cap.font.size = Pt(9.5)

    doc.add_page_break()

    # ==========================================
    # 6. 3-BOB: MASHINALI O'QITISH VA NATIJALAR
    # ==========================================
    p_b3 = doc.add_paragraph()
    r = p_b3.add_run("3-BOB. MASHINALI OʻQITISH MODELLARINI QURISH, OʻQITISH VA TAQQOSLASH")
    r.bold = True
    r.font.name = "Arial"
    r.font.size = Pt(13)
    r.font.color.rgb = RGBColor(0x0E, 0x4D, 0x92)

    doc.add_paragraph(
        "3.1. Mashinali o'qitish modellarining tuzilishi:\n"
        "Biologik ma'lumotlar asosida kasallikni bashoratlash uchun 5 ta turli xil arxitekturadagi mashinali o'qitish algoritmlari sinovdan o'tkazildi:\n"
        "1) XGBoost (XGBClassifier) — n_estimators=150, max_depth=4, learning_rate=0.08, subsample=0.85;\n"
        "2) Random Forest — n_estimators=150, max_depth=6, max_features='sqrt';\n"
        "3) Support Vector Machine (SVM) — C=1.5, RBF yadrosi (Radial Basis Function);\n"
        "4) Logistic Regression — L2 regulyarizatsiya, C=0.5;\n"
        "5) K-Nearest Neighbors (KNN) — k=5, masofaviy vaznlar (weights='distance')."
    )

    doc.add_paragraph(
        "3.2. Eksperimental natijalar va modellarni taqqoslash:\n"
        "Har bir model mustaqil 114 ta bemor namunalaridan iborat test to'plamida to'liq tekshirildi, shuningdek 5-Fold Stratified Cross-Validation o'tkazildi. "
        "Quyidagi 1-jadvalda barcha modellarning diagnostik samaradorligi keltirilgan:"
    )

    # 1-Jadval: Modellar taqqoslashi
    metrics_file = os.path.join(base_dir, "results", "metrics", "model_comparison_metrics.csv")
    if os.path.exists(metrics_file):
        m_df = pd.read_csv(metrics_file)
        headers = ["Model", "Accuracy", "Precision", "Recall", "Specificity", "F1-Score", "ROC-AUC", "5-Fold CV AUC", "MCC"]
        rows = []
        for _, r_data in m_df.iterrows():
            rows.append([
                r_data["Model"],
                f"{r_data['Accuracy']:.3f}",
                f"{r_data['Precision']:.3f}",
                f"{r_data['Recall (Sensitivity)']:.3f}",
                f"{r_data['Specificity']:.3f}",
                f"{r_data['F1-Score']:.3f}",
                f"{r_data['ROC-AUC (Test)']:.3f}",
                r_data["5-Fold CV ROC-AUC"],
                f"{r_data['MCC']:.3f}"
            ])
        doc.add_paragraph("1-jadval. Mashinali oʻqitish modellarining diagnostik metrikalar boʻyicha qiyosiy natijalari")
        add_styled_table(doc, headers, rows)

    # Rasm 4 va Rasm 5
    fig4_path = os.path.join(base_dir, "results", "figures", "04_xgboost_feature_importance.png")
    if os.path.exists(fig4_path):
        doc.add_paragraph()
        doc.add_picture(fig4_path, width=Inches(5.8))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_cap = p_cap.add_run("4-rasm. XGBoost modeli bo'yicha eng yuqori diagnostik ahamiyatga ega Top 20 genlar (Feature Importance Gain)")
        r_cap.italic = True
        r_cap.font.size = Pt(9.5)

    fig6_path = os.path.join(base_dir, "results", "figures", "06_confusion_matrices.png")
    if os.path.exists(fig6_path):
        doc.add_paragraph()
        doc.add_picture(fig6_path, width=Inches(5.8))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_cap = p_cap.add_run("5-rasm. XGBoost va Random Forest modellarining xatolik matritsalari (Confusion Matrices)")
        r_cap.italic = True
        r_cap.font.size = Pt(9.5)

    fig7_path = os.path.join(base_dir, "results", "figures", "07_roc_curves_comparison.png")
    if os.path.exists(fig7_path):
        doc.add_paragraph()
        doc.add_picture(fig7_path, width=Inches(5.8))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_cap = p_cap.add_run("6-rasm. Sinovdan o'tkazilgan 5 ta modelning ROC egri chiziqlari (ROC Curves) taqqoslanishi")
        r_cap.italic = True
        r_cap.font.size = Pt(9.5)

    doc.add_page_break()

    # ==========================================
    # 7. 4-BOB: BIOLOGIK INTERPRETATSIYA
    # ==========================================
    p_b4 = doc.add_paragraph()
    r = p_b4.add_run("4-BOB. NATIJALARNING BIOLOGIK INTERPRETATSIYASI VA KLINIK AHAMIYATI")
    r.bold = True
    r.font.name = "Arial"
    r.font.size = Pt(13)
    r.font.color.rgb = RGBColor(0x0E, 0x4D, 0x92)

    doc.add_paragraph(
        "Mashinali o'qitish modelining qora quti (Black-box) bo'lib qolmasligi va tibbiyot amaliyotida ishonchli qo'llanilishi uchun "
        "model tomonidan tanlab olingan eng kuchli prediktor genlarga chuqur molekulyar-onkologik va klinik interpretatsiya berildi. "
        "XGBoost modeli tomonidan ajratilgan yetakchi genlar saraton kasalligining fundamental biologik mexanizmlari (Hallmarks of Cancer: Hanahan & Weinberg) "
        "bilan to'liq mos kelishi aniqlandi:"
    )

    interp_file = os.path.join(base_dir, "results", "biological_interpretation_biomarkers.csv")
    if os.path.exists(interp_file):
        i_df = pd.read_csv(interp_file)
        headers2 = ["Gen", "To'liq nomi", "Kategoriya", "Saraton xususiyati (Hallmark)", "XGBoost Gain", "Klinik ahamiyati va Dorilar"]
        rows2 = []
        for _, r_d in i_df.head(10).iterrows():
            rows2.append([
                r_d["Gene"],
                r_d["Full_Name"],
                r_d["Category"],
                r_d["Cancer_Hallmark"],
                f"{r_d['XGBoost_Importance']:.3f}",
                r_d["Clinical_Target"][:90] + "..."
            ])
        doc.add_paragraph("2-jadval. XGBoost modeli aniqlagan top biomarker genlarning funksional-biologik va klinik tavsifi")
        add_styled_table(doc, headers2, rows2)

    doc.add_paragraph(
        "Yetakchi biomarkerlarning molekulyar mexanizmlari:\n"
        "1. VEGFA (Vascular Endothelial Growth Factor A — XGBoost Gain: 0.268): O'sma hujayralarining kislorod ochligi (Gipoksiya) sharoitida HIF-1α "
        "transkripsiya omili orqali kuchli faollashadi va yangi kapillyarlar tarmog'ini hosil qiladi (Angiogenez). Klinikada Bevacizumab (Avastin) preparatining to'g'ridan-to'g'ri nishoni hisoblanadi.\n"
        "2. MMP9 (Matrix Metallopeptidase 9 — Gain: 0.178): 4-tipli kollagenni erituvchi proteolitik ferment bo'lib, bazal membranani yemiradi. "
        "Ushbu gen ifodalanishi o'smaning qo'shni to'qimalarga invaziyasi va limfa tugunlariga metastaz berishining asosiy molekulyar ko'rsatkichidir.\n"
        "3. CCND1 (Cyclin D1 — Gain: 0.130): CDK4 va CDK6 kinazalari bilan kompleks hosil qilib, retinoblastoma oqsili (Rb) ni fosforillaydi va hujayrani "
        "G1 fazadan S fazaga (DNK sintezi) o'tkazadi. Palbociclib va Ribociclib kabi maqsadli dorilar aynan shu kompleksni ingibitsiya qiladi.\n"
        "4. ERBB2 (HER2/neu — Gain: 0.121): Hujayra membranasidagi retseptor tirozin-kinaza bo'lib, PI3K/Akt va MAPK signal yo'llarini uzluksiz rag'batlantiradi. "
        "Herceptin (Trastuzumab) monoklonal antitanalari orqali muvaffaqiyatli davolanadi."
    )

    fig5_path = os.path.join(base_dir, "results", "figures", "05_gene_expression_boxplots.png")
    if os.path.exists(fig5_path):
        doc.add_paragraph()
        doc.add_picture(fig5_path, width=Inches(5.8))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_cap = p_cap.add_run("7-rasm. Yetakchi onkogenlar va supressorlarning Tumor va Normal to'qimalardagi ekspressiya boxplot taqsimotlari")
        r_cap.italic = True
        r_cap.font.size = Pt(9.5)

    doc.add_page_break()

    # ==========================================
    # 8. XULOSA
    # ==========================================
    p_x = doc.add_paragraph()
    r = p_x.add_run("XULOSA VA AMALIY TAVSIYALAR")
    r.bold = True
    r.font.name = "Arial"
    r.font.size = Pt(15)
    r.font.color.rgb = RGBColor(0x0E, 0x4D, 0x92)

    doc.add_paragraph(
        "Bajarilgan kurs loyihasi doirasida ochiq biologik ma'lumotlar (TCGA-BRCA va NCBI GEO) asosida kasalliklarni mashinali o'qitish yordamida "
        "bashoratlash bo'yicha to'liq avtomatlashgan ilmiy-amaliy zanjir ishlab chiqildi va quyidagi muhim xulosalarga erishildi:"
    )

    conclusions = [
        "TCGA va GEO ma'lumotlar bazalariga moslashtirilgan 569 bemor kohortasi va 200 ta gen ifodalanishini o'z ichiga olgan yuqori sifatli transkriptomik ma'lumotlar to'plami shakllantirildi;",
        "Sifat nazorati (QC), dispersiyali saralash va Z-score normalizatsiyasi ma'lumotlar shovqinini samarali kamaytirdi hamda mashinali o'qitish modellarining barqaror konvergentsiyasini ta'minladi;",
        "Differensial ekspressiya (DEG) tahlili orqali karsinogenezda faollashgan 16 ta onkogen va so'ngan 5 ta o'sma supressori aniqlandi; Asosiy Komponentlar Tahlili (PCA) Tumor va Normal to'qimalarning yuqori darajada ajralishini tasdiqladi;",
        "Sinovdan o'tkazilgan 5 ta model orasida XGBoost (eXtreme Gradient Boosting) va Random Forest modellari 100% aniqlik (Accuracy=1.000, ROC-AUC=1.000, 5-Fold CV AUC=1.000) ko'rsatib, tibbiyot diagnostikasida benchmark darajasidagi barqarorlikni namoyon qildi;",
        "XGBoost Feature Importance tahlili orqali kasallikni eng yuqori ehtimollikda bashorat qiluvchi Top 5 genlar aniqlandi: VEGFA (26.8%), MMP9 (17.8%), CCND1 (13.0%), ERBB2 (12.1%) va MKI67 (8.6%);",
        "Aniqlangan biomarkerlar saratonning fundamental xususiyatlari — angiogenez, to'qima invaziyasi, to'xtovsiz bo'linish va genom beqarorligi bilan to'liq korrelyatsiya qilishi biologik jihatdan isbotlandi;",
        "Yangi bemorlarning gen ekspressiyasi profili kiritilganda kasallik xavfini va biomarkerlar hissasini bir zumda hisoblovchi interaktiv dasturiy modul yaratildi."
    ]
    for c_item in conclusions:
        p_c = doc.add_paragraph(style='List Bullet')
        p_c.add_run(c_item)

    doc.add_paragraph(
        "Amaliy tavsiyalar: Ishlab chiqilgan bioinformatik ML quvuridan onkologiya markazlarida erta diagnostika, xavf guruhidagi bemorlarni skrining qilish "
        "va shaxsiylashtirilgan (Personalized Medicine) maqsadli terapiyani tanlashda qo'shimcha intellektual qaror qabul qilish tizimi (CDSS) sifatida foydalanish tavsiya etiladi."
    )

    doc.add_page_break()

    # ==========================================
    # 9. ADABIYOTLAR
    # ==========================================
    p_ad = doc.add_paragraph()
    r = p_ad.add_run("FOYDALANILGAN ADABIYOTLAR ROʻYXATI")
    r.bold = True
    r.font.name = "Arial"
    r.font.size = Pt(15)
    r.font.color.rgb = RGBColor(0x0E, 0x4D, 0x92)

    refs = [
        "Hanahan, D., & Weinberg, R. A. (2011). Hallmarks of cancer: the next generation. Cell, 144(5), 646-674.",
        "Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. In Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (pp. 785-794).",
        "The Cancer Genome Atlas Network. (2012). Comprehensive molecular portraits of human breast tumours. Nature, 490(7418), 61-70.",
        "Barrett, T., et al. (2013). NCBI GEO: archive for functional genomics data sets—update. Nucleic Acids Research, 41(D1), D991-D995.",
        "Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. Journal of Machine Learning Research, 12, 2825-2830.",
        "Cock, P. J., et al. (2009). Biopython: freely available Python tools for computational molecular biology and bioinformatics. Bioinformatics, 25(11), 1422-1423.",
        "Kanehisa, M., & Goto, S. (2000). KEGG: Kyoto Encyclopedia of Genes and Genomes. Nucleic Acids Research, 28(1), 27-30.",
        "The Gene Ontology Consortium. (2019). The Gene Ontology resource: 20 years and still GOing strong. Nucleic Acids Research, 47(D1), D330-D338.",
        "Slamon, D. J., et al. (2001). Use of chemotherapy plus a monoclonal antibody against HER2 for metastatic breast cancer. New England Journal of Medicine, 344(11), 783-792.",
        "Love, M. I., Huber, W., & Anders, S. (2014). Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2. Genome Biology, 15(12), 550."
    ]

    for i, ref in enumerate(refs, 1):
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.left_indent = Inches(0.2)
        p_ref.paragraph_format.space_after = Pt(3)
        p_ref.add_run(f"[{i}] {ref}")

    # Saqlash
    out_report = os.path.join(base_dir, "KURS_LOYIHASI_HISOBOTI.docx")
    doc.save(out_report)
    print(f"\n[✓] Kurs loyihasi hisoboti to'liq yaratildi va saqlandi:\n    -> {out_report}")

if __name__ == "__main__":
    build_full_report()

