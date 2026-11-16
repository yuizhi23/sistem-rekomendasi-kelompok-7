# -*- coding: utf-8 -*-
import json
import numpy as np
from xml.sax.saxutils import escape
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
                                TableStyle, Image as RLImage, PageBreak, KeepTogether)

# ===================== ISI DATA KELOMPOK DI SINI =====================
KELOMPOK = "Kelompok 7"
ANGGOTA = [("Yukie Ramadhani Kiyoshi", "103012300093"),
           ("Sri Dewi Septiani Nur", "103012300360"),
           ("Kayla Ulfiyah Haurani", "103012300490"),
           ("Farha Amirah Hasibuan", "103012330345")]
LINK = "https://github.com/yuizhi23/sistem-rekomendasi-kelompok-7"
OUT = "Laporan_Sistem_Rekomendasi.pdf"
# =====================================================================

import os, matplotlib
font_dirs = [
    "/usr/share/fonts/truetype/dejavu/",
    os.path.join(matplotlib.get_data_path(), "fonts", "ttf") + "/",
    "/Library/Fonts/",
    "/System/Library/Fonts/"
]
FD = next((d for d in font_dirs if os.path.exists(os.path.join(d, "DejaVuSans.ttf"))), None)
if not FD:
    raise FileNotFoundError("DejaVuSans.ttf tidak ditemukan. Pastikan matplotlib atau font DejaVu terpasang.")

pdfmetrics.registerFont(TTFont("DV", FD + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DV-B", FD + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DV-I", FD + "DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("DV-BI", FD + "DejaVuSans-BoldOblique.ttf"))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I", boldItalic="DV-BI")

R = json.load(open("results.json"))
F = R["final"]
NAVY, TEAL = colors.HexColor("#14213d"), colors.HexColor("#00798c")
LIGHT = colors.HexColor("#eef3f6")

body = ParagraphStyle("body", fontName="DV", fontSize=9.3, leading=14, alignment=TA_JUSTIFY, spaceAfter=5)
bodyL = ParagraphStyle("bodyL", parent=body, alignment=TA_LEFT)
h1 = ParagraphStyle("h1", fontName="DV-B", fontSize=14, leading=18, textColor=NAVY, spaceBefore=12, spaceAfter=6, keepWithNext=1)
h2 = ParagraphStyle("h2", fontName="DV-B", fontSize=11, leading=15, textColor=TEAL, spaceBefore=9, spaceAfter=4, keepWithNext=1)
cap = ParagraphStyle("cap", fontName="DV-I", fontSize=8, leading=11, alignment=TA_CENTER, textColor=colors.HexColor("#444444"), spaceAfter=8, spaceBefore=2)
step = ParagraphStyle("step", parent=body, leftIndent=16, firstLineIndent=-12, spaceAfter=3)
cell = ParagraphStyle("cell", fontName="DV", fontSize=8, leading=10.5)
cellB = ParagraphStyle("cellB", parent=cell, fontName="DV-B")
cellC = ParagraphStyle("cellC", parent=cell, alignment=TA_CENTER)
cellH = ParagraphStyle("cellH", parent=cell, fontName="DV-B", textColor=colors.white, alignment=TA_CENTER)
note = ParagraphStyle("note", parent=body, fontSize=8.5, leading=12, textColor=colors.HexColor("#333333"),
                      backColor=colors.HexColor("#fff6dd"), borderPadding=5, spaceBefore=4, spaceAfter=8)

import os
LAB_FILE = "labels.json"
LABELS = json.load(open(LAB_FILE)) if os.path.exists(LAB_FILE) else {}
NEWLAB = {}
story = []
fig_n = [0]
tab_n = [0]


def L(key):
    return LABELS.get(key, "?")


def P(t, s=body): story.append(Paragraph(t, s))
def H1(t): story.append(Paragraph(t, h1))
def H2(t): story.append(Paragraph(t, h2))
def S(h=6): story.append(Spacer(1, h))
def STEP(n, t): story.append(Paragraph(f"<b>{n}.</b>&nbsp;&nbsp;{t}", step))


def img_flow(path, width=None, scale=None, maxw=481):
    w, h = Image.open(path).size
    width = width or (w * scale if scale else maxw)
    width = min(width, maxw)
    return RLImage(path, width=width, height=h * width / w)


def figure(path, caption, label=None, **kw):
    fig_n[0] += 1
    if label: NEWLAB[label] = fig_n[0]
    story.append(KeepTogether([img_flow(path, **kw), Paragraph(f"<b>Gambar {fig_n[0]}.</b> {caption}", cap)]))


def formula(path):
    w, h = Image.open(path).size
    width = min(w / 220 * 72, 470)
    t = Table([[RLImage(path, width=width, height=h * width / w)]], colWidths=[481])
    t.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                           ("BOX", (0, 0), (-1, -1), .4, colors.HexColor("#cccccc")),
                           ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    story.append(t); S(6)


def code(path, caption):
    w, h = Image.open(path).size
    fig_n[0] += 1
    story.append(KeepTogether([img_flow(path, scale=.58), Paragraph(f"<b>Gambar {fig_n[0]}.</b> {caption}", cap)]))


def table(data, widths, caption=None, header=True, align_center_from=1, zebra=True, extra=None, label=None):
    rows = []
    for ri, row in enumerate(data):
        r_ = []
        for ci, c in enumerate(row):
            if isinstance(c, str):
                st = cellH if (header and ri == 0) else (cellC if ci >= align_center_from else cell)
                r_.append(Paragraph(c, st))
            else:
                r_.append(c)
        rows.append(r_)
    t = Table(rows, colWidths=widths, repeatRows=1 if header else 0)
    style = [("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#c8d0d6")),
             ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    if zebra:
        for i in range(1, len(rows)):
            if i % 2 == 0: style.append(("BACKGROUND", (0, i), (-1, i), LIGHT))
    if extra: style += extra
    t.setStyle(TableStyle(style))
    items = [t]
    if caption:
        tab_n[0] += 1
        if label: NEWLAB[label] = tab_n[0]
        items = [Paragraph(f"<b>Tabel {tab_n[0]}.</b> {caption}", ParagraphStyle("tc", parent=cap, alignment=TA_LEFT, spaceAfter=3)), t, Spacer(1, 8)]
    story.append(KeepTogether(items))


def fmt(v, d=4): return f"{v:.{d}f}"


def best_bold(vals, lowest=True, d=4):
    b = min(vals) if lowest else max(vals)
    return [f"<b>{fmt(v, d)}</b>" if v == b else fmt(v, d) for v in vals]


# ------------------------------------------------------------------ halaman sampul
story.append(Spacer(1, 1.2 * cm))
story.append(Paragraph("LAPORAN TUGAS KELOMPOK", ParagraphStyle("c0", fontName="DV-B", fontSize=11, textColor=TEAL, alignment=TA_CENTER, spaceAfter=10)))
story.append(Paragraph("Prediksi Rating dan Rekomendasi Item", ParagraphStyle("c1", fontName="DV-B", fontSize=21, leading=26, textColor=NAVY, alignment=TA_CENTER)))
story.append(Paragraph("User-based Collaborative Filtering, Item-based Collaborative Filtering,<br/>dan Matrix Factorization", ParagraphStyle("c2", fontName="DV", fontSize=13, leading=19, textColor=NAVY, alignment=TA_CENTER, spaceBefore=6)))
story.append(Spacer(1, 6))
story.append(Paragraph("Studi kasus: dataset MovieLens (ml-latest-small) dengan evaluasi MAE, MSE, RMSE, NMSE, dan NDCG", ParagraphStyle("c3", fontName="DV-I", fontSize=9.5, alignment=TA_CENTER, textColor=colors.HexColor("#555555"))))
story.append(Spacer(1, 1.2 * cm))
hl = colors.HexColor("#fff2a8")
info = [[Paragraph("<b>Kelompok</b>", cell), Paragraph(KELOMPOK, cell)]]
t = Table(info, colWidths=[3.5 * cm, 11 * cm]); t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), .5, colors.grey), ("BACKGROUND", (1, 0), (1, 0), hl), ("BACKGROUND", (0, 0), (0, 0), LIGHT), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
story.append(t); S(10)
rows = [[Paragraph("<b>No</b>", cellH), Paragraph("<b>Nama Anggota</b>", cellH), Paragraph("<b>NIM</b>", cellH)]]
for i, (n, m) in enumerate(ANGGOTA, 1):
    rows.append([Paragraph(str(i), cellC), Paragraph(n, cell), Paragraph(m, cell)])
t = Table(rows, colWidths=[1.2 * cm, 9.3 * cm, 4 * cm])
t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), .5, colors.grey), ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                       ("BACKGROUND", (1, 1), (-1, -1), hl), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
story.append(t); S(10)
rows = [[Paragraph("<b>Source code</b>", cell), Paragraph(LINK, cell)],
        [Paragraph("<b>Akses diberikan ke</b>", cell), Paragraph("bayzal@gmail.com", cell)]]
t = Table(rows, colWidths=[3.5 * cm, 11 * cm])
t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), .5, colors.grey), ("BACKGROUND", (0, 0), (0, -1), LIGHT), ("BACKGROUND", (1, 0), (1, 0), hl), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
story.append(t)
story.append(Spacer(1, 1.3 * cm))
story.append(Paragraph("<b>Ringkasan hasil</b>", ParagraphStyle("rs", fontName="DV-B", fontSize=10, textColor=NAVY, spaceAfter=4)))
story.append(Paragraph(
    f"Tiga metode diuji pada {R['n_ratings']:,} rating dari {R['n_users']} pengguna terhadap {R['n_items']:,} film (data uji: 20% rating tiap pengguna). "
    f"Item-based CF memberikan akurasi prediksi rating terbaik (RMSE {fmt(F['Item-based CF']['RMSE'])}, MAE {fmt(F['Item-based CF']['MAE'])}), "
    f"diikuti Matrix Factorization (RMSE {fmt(F['Matrix Factorization']['RMSE'])}) dan User-based CF (RMSE {fmt(F['User-based CF']['RMSE'])}). "
    f"Untuk pengurutan item, NDCG@10 ketiganya berada pada kisaran {fmt(min(F[m]['NDCG@10'] for m in ['User-based CF','Item-based CF','Matrix Factorization']),3)}–{fmt(max(F[m]['NDCG@10'] for m in ['User-based CF','Item-based CF','Matrix Factorization']),3)} "
    f"(acak: {fmt(F['Acak']['NDCG@10'],3)}).", body))
story.append(Spacer(1, 6))
story.append(Paragraph("Kolom yang disorot kuning pada halaman ini adalah data yang perlu diisi oleh kelompok (nomor kelompok, nama dan NIM anggota, serta tautan repository).", note))
story.append(PageBreak())

# ------------------------------------------------------------------ 1. pendahuluan
H1("1. Pendahuluan")
P("Sistem rekomendasi membantu pengguna menemukan item yang relevan di tengah jumlah pilihan yang sangat besar. Laporan ini membahas dua tugas "
  "yang umum pada sistem rekomendasi: <b>(a) prediksi rating</b>, yaitu memperkirakan nilai yang akan diberikan pengguna <i>u</i> pada item <i>i</i> yang belum pernah ia nilai, "
  "dan <b>(b) rekomendasi item</b> (top-N), yaitu memilih N item dengan prediksi terbaik untuk ditampilkan kepada pengguna.")
P("Tiga metode diimplementasikan dari awal menggunakan Python (NumPy/SciPy/pandas), tanpa pustaka rekomendasi siap pakai, sehingga setiap langkah dapat dijelaskan dan diperiksa: "
  "<b>User-based Collaborative Filtering</b> (UB-CF), <b>Item-based Collaborative Filtering</b> (IB-CF), dan <b>Matrix Factorization</b> (MF) yang dilatih dengan "
  "<i>stochastic gradient descent</i>. Ketiganya diuji dengan lima metrik: MAE, MSE, RMSE, NMSE, dan NDCG. Sebagai pembanding ditambahkan <i>baseline</i> sederhana "
  "(rata-rata global + bias user + bias item), rekomendasi berdasarkan popularitas, dan urutan acak.")

# ------------------------------------------------------------------ 2. dataset
H1("2. Dataset")
pu, pi = np.array(R["per_user"]), np.array(R["per_item"])
dist = {float(k): v for k, v in R["dist_rating"].items()}
mean_r = sum(k * v for k, v in dist.items()) / sum(dist.values())
P("Dataset yang digunakan adalah <b>MovieLens ml-latest-small</b> dari GroupLens Research, Universitas Minnesota (Harper &amp; Konstan, 2015; sumber asli: "
  "grouplens.org/datasets/movielens). Salinan berkas <i>ratings.csv</i> dan <i>movies.csv</i> diunduh dari mirror GitHub (repository smanihwr/ml-latest-small). "
  "Dataset ini memenuhi syarat tugas karena memiliki <b>riwayat penilaian (user history)</b>: setiap baris memuat <i>userId, movieId, rating</i> (0.5 sampai 5.0 dengan kelipatan 0.5), "
  f"dan setiap pengguna menilai minimal {pu.min()} film.")
table([["Statistik", "Nilai"],
       ["Jumlah pengguna", f"{R['n_users']:,}"], ["Jumlah film", f"{R['n_items']:,}"], ["Jumlah rating", f"{R['n_ratings']:,}"],
       ["Sparsity matriks user–item", f"{R['sparsity']*100:.2f}%"], ["Rata-rata rating", f"{mean_r:.3f}"],
       ["Rating per user (min / median / maks)", f"{pu.min()} / {int(np.median(pu))} / {pu.max()}"],
       ["Rating per film (min / median / maks)", f"{pi.min()} / {int(np.median(pi))} / {pi.max()}"]],
      [8 * cm, 5 * cm], "Statistik dataset.")
figure("figs/f1_dataset.png", "Distribusi rating, jumlah rating per pengguna, dan jumlah rating per film. Sebagian besar film hanya dinilai sedikit pengguna (long tail), sehingga matriks sangat jarang (sparse).")
P(f"Matriks user–item sangat jarang ({R['sparsity']*100:.1f}% sel kosong) dan distribusi rating per film sangat miring: median film hanya memiliki {int(np.median(pi))} rating. "
  "Kondisi ini berpengaruh langsung pada hasil, seperti dibahas pada Bagian 7.")

# ------------------------------------------------------------------ 3. skema pengujian
H1("3. Persiapan Data dan Skema Pengujian")
STEP(1, "<b>Memuat data dan membuat indeks.</b> <i>userId</i> dan <i>movieId</i> dipetakan ke indeks 0…n−1 agar dapat disimpan dalam matriks.")
STEP(2, f"<b>Pembagian data per pengguna (hold-out).</b> Untuk setiap pengguna, 20% ratingnya disembunyikan sebagai data uji dan 80% sisanya menjadi data latih. "
        f"Pembagian per pengguna menjamin setiap pengguna masih memiliki riwayat pada data latih. Hasilnya: {R['n_train']:,} rating latih dan {R['n_test']:,} rating uji.")
STEP(3, f"<b>Data validasi untuk tuning.</b> Dari data latih, 12.5% rating tiap pengguna dipisahkan lagi ({R['n_val']:,} rating) untuk memilih hyperparameter "
        "(k tetangga, jumlah faktor, regularisasi). <b>Data uji tidak pernah dipakai untuk memilih parameter.</b> Setelah parameter terpilih, model dilatih ulang pada seluruh data latih dan diuji satu kali pada data uji.")
STEP(4, "<b>Matriks user–item.</b> Data latih diubah menjadi matriks R berukuran 610 × 9.724; sel bernilai 0 berarti belum dinilai.")
code("figs/s_data.png", "Memuat data, membagi data per pengguna, dan membentuk matriks user–item (<i>recsys.py</i>).")
P("Seed acak dibuat tetap (42) sehingga seluruh hasil dapat direproduksi.")

# ------------------------------------------------------------------ 4. metode
H1("4. Metode dan Langkah Implementasi")
H2("4.1 Baseline (bias) – pembanding dan nilai cadangan")
P("Baseline memprediksi rating sebagai rata-rata global μ ditambah bias pengguna b<sub>u</sub> (user yang cenderung memberi nilai tinggi/rendah) dan bias film b<sub>i</sub> (film yang cenderung disukai/tidak). "
  "Bias dihitung dengan <i>damping</i> agar stabil untuk pengguna/film yang jarang dinilai. Baseline juga dipakai sebagai nilai cadangan ketika CF tidak menemukan tetangga.")
formula("figs/m_base.png")
code("figs/s_base.png", "Perhitungan baseline bias.")

H2("4.2 User-based Collaborative Filtering")
P("Gagasan: pengguna yang selera ratingnya mirip di masa lalu akan menilai item baru dengan cara yang mirip. Langkah-langkahnya:")
STEP(1, "<b>Hitung kemiripan antar pengguna</b> dengan korelasi Pearson pada film yang dinilai bersama (I<sub>uv</sub>). Karena dua pengguna bisa hanya berbagi sedikit film, "
        "kemiripan dikalikan <i>significance weighting</i> |I<sub>uv</sub>|/(|I<sub>uv</sub>|+β) dengan β = 10 agar kemiripan yang berdasar sedikit data tidak terlalu dipercaya.")
formula("figs/m_ub_sim.png")
code("figs/s_ub_sim.png", "Perhitungan matriks kemiripan Pearson antar pengguna secara vektor (matriks 610 × 610).")
STEP(2, "<b>Pilih tetangga.</b> Untuk setiap pasangan (u, i), dipilih <i>k</i> pengguna dengan kemiripan positif terbesar <u>yang sudah menilai item i</u>, yaitu N<sub>k</sub>(u, i).")
STEP(3, "<b>Prediksi rating</b> dengan rata-rata tertimbang selisih rating tetangga terhadap rata-rata dirinya (<i>mean-centering</i>), lalu ditambahkan ke rata-rata pengguna target. "
        "Jika tidak ada tetangga yang menilai item tersebut, dipakai prediksi baseline.")
formula("figs/m_ub_pred.png")
code("figs/s_ub_pred.png", "Prediksi rating UB-CF: pemilihan k tetangga per item dan rata-rata tertimbang.")
STEP(4, f"<b>Pilih k</b> pada data validasi (Bagian 6.1). Nilai terpilih: <b>k = {R['best']['k_user']}</b>.")

H2("4.3 Item-based Collaborative Filtering")
P("Gagasan: rating pengguna terhadap item i dapat diperkirakan dari rating yang ia berikan pada item-item yang mirip dengan i. Kemiripan antar item cenderung lebih stabil daripada kemiripan antar pengguna.")
STEP(1, "<b>Hitung kemiripan antar item</b> dengan <i>adjusted cosine</i>: rating dipusatkan pada rata-rata pengguna (menghilangkan perbedaan kecenderungan memberi nilai), lalu dihitung kosinus antar vektor item. "
        "Significance weighting yang sama (β = 10) diterapkan. Matriks 9.724 × 9.724 dihitung per potongan 1.000 baris agar hemat memori.")
formula("figs/m_ib_sim.png")
code("figs/s_ib_sim.png", "Perhitungan matriks kemiripan adjusted cosine antar film.")
STEP(2, "<b>Pilih tetangga.</b> Untuk pasangan (u, i), dipilih <i>k</i> item termirip dengan i <u>yang sudah dinilai oleh u</u>, yaitu N<sub>k</sub>(i, u).")
STEP(3, "<b>Prediksi rating</b> = rata-rata rating item i ditambah rata-rata tertimbang selisih rating u pada item-item tetangga terhadap rata-rata masing-masing item.")
formula("figs/m_ib_pred.png")
code("figs/s_ib_pred.png", "Prediksi rating IB-CF untuk satu pengguna terhadap semua item (atau item tertentu).")
STEP(4, f"<b>Pilih k</b> pada data validasi. Nilai terpilih: <b>k = {R['best']['k_item']}</b>.")

H2("4.4 Matrix Factorization (Funk-SVD dengan bias)")
P("Matriks rating R didekati oleh hasil kali dua matriks berdimensi rendah. Setiap pengguna dan setiap film diwakili vektor <i>faktor laten</i> "
  "p<sub>u</sub> dan q<sub>i</sub> (dimensi f); rating diprediksi dari hasil kali dalamnya ditambah bias. Parameter dipelajari dari rating yang diketahui saja dengan meminimalkan kuadrat galat berregularisasi.")
formula("figs/m_mf.png")
STEP(1, "<b>Inisialisasi</b> p<sub>u</sub>, q<sub>i</sub> dengan bilangan acak kecil N(0; 0.1); bias bernilai 0, μ = rata-rata rating latih.")
STEP(2, "<b>Untuk setiap epoch</b>, rating latih diacak urutannya. Untuk tiap rating dihitung galat e<sub>ui</sub>, lalu seluruh parameter digeser berlawanan arah gradien (learning rate γ = 0.005):")
formula("figs/m_sgd.png")
code("figs/s_mf_train.png", "Pelatihan Matrix Factorization dengan SGD; galat train dan galat evaluasi dicatat tiap epoch.")
STEP(3, f"<b>Pilih jumlah faktor dan regularisasi λ</b> pada data validasi. Terpilih: <b>f = {R['best']['n_factors']}</b>, <b>λ = {R['best']['reg']}</b>, 30 epoch.")
STEP(4, "<b>Prediksi</b> rating dengan rumus di atas, lalu dipotong ke rentang [0.5; 5.0].")
code("figs/s_mf_pred.png", "Prediksi rating MF untuk pasangan tertentu dan untuk seluruh matriks.")

H2("4.5 Menghasilkan rekomendasi top-N")
P("Rekomendasi dibuat dengan memprediksi rating semua film yang belum dinilai pengguna, membuang film yang sudah pernah dinilai, lalu mengambil 10 film dengan prediksi tertinggi. "
  "Hanya film yang memiliki setidaknya 20 rating pada data latih yang menjadi kandidat, karena prediksi untuk film dengan 1–2 rating sangat tidak andal (lihat Bagian 6.4).")
code("figs/s_recs.png", "Fungsi pembuat daftar rekomendasi top-N.")

# ------------------------------------------------------------------ 5. metrik
H1("5. Metrik Evaluasi")
P("Metrik galat prediksi dihitung pada seluruh pasangan (user, film) di data uji (n = %s), dengan r sebagai rating sebenarnya, r&#770; prediksi, dan r&#772; rata-rata rating uji." % f"{R['n_test']:,}")
formula("figs/m_err.png")
code("figs/s_metrics.png", "Implementasi MAE, MSE, RMSE, dan NMSE.")
P("<b>Catatan NMSE.</b> NMSE didefinisikan di sini sebagai jumlah kuadrat galat dibagi jumlah kuadrat simpangan rating terhadap rata-ratanya (galat dinormalisasi oleh varians data). "
  "Nilai 0 berarti prediksi sempurna dan nilai 1 berarti tidak lebih baik daripada menebak rata-rata rating uji; NMSE sama dengan 1 − R². "
  "Jika buku acuan memakai normalisasi yang berbeda, hanya skala nilainya yang berubah, bukan urutan antar metode.", note)
P("<b>NDCG@K</b> menilai kualitas <i>urutan</i>. Item di posisi atas diberi bobot lebih besar (diskon 1/log<sub>2</sub>(p+1)). Dua protokol dilaporkan:")
formula("figs/m_ndcg.png")
STEP("a", "<b>NDCG@10 pada item uji</b> (gain = 2<super>rating</super> − 1). Untuk tiap pengguna, film-film uji miliknya diurutkan berdasarkan prediksi, lalu dibandingkan dengan urutan ideal menurut rating asli. "
          "Protokol ini mengukur apakah model dapat membedakan film yang disukai dan kurang disukai <i>di antara film yang memang ditonton pengguna</i>.")
code("figs/s_ndcg.png", "Implementasi NDCG@10 pada item uji.")
STEP("b", "<b>NDCG@10 ranking penuh</b> (relevansi biner: rating uji ≥ 4). Seluruh film kandidat yang belum dinilai pengguna diurutkan, dan NDCG dihitung terhadap film uji yang relevan. "
          "Protokol ini lebih berat dan lebih mendekati kondisi rekomendasi sesungguhnya; Precision@10 dan Recall@10 dilaporkan sebagai pelengkap.")
code("figs/s_topn.png", "Implementasi evaluasi ranking penuh (NDCG, Precision, Recall @10) dan fungsi evaluate_all.")

# ------------------------------------------------------------------ 6. hasil
H1("6. Hasil Pengujian")
H2("6.1 Pemilihan hyperparameter (data validasi)")
b = R["best"]
P(f"Gambar {L('fig_tuning')} menunjukkan RMSE validasi. Untuk UB-CF dan IB-CF, k yang terlalu kecil membuat prediksi bergantung pada sedikit tetangga (derau tinggi), "
  f"sedangkan k yang terlalu besar mengikutsertakan tetangga yang kurang mirip; hasilnya berbentuk huruf U dengan minimum pada k = {b['k_user']} (UB-CF) dan k = {b['k_item']} (IB-CF). "
  f"Pada MF, kombinasi {b['n_factors']} faktor dengan λ = {b['reg']} memberikan RMSE validasi terendah; regularisasi terlalu kecil (0.02) tampak overfit, terutama pada 50 faktor.")
figure("figs/f2_tuning.png", label="fig_tuning", caption="RMSE pada data validasi untuk berbagai nilai k (UB-CF, IB-CF) dan kombinasi jumlah faktor × regularisasi (MF). Garis putus-putus: baseline.")
table([["Metode", "Hyperparameter terpilih"],
       ["User-based CF", f"Pearson + significance weighting (β = 10), k = {b['k_user']}"],
       ["Item-based CF", f"Adjusted cosine + significance weighting (β = 10), k = {b['k_item']}"],
       ["Matrix Factorization", f"f = {b['n_factors']} faktor, λ = {b['reg']}, γ = 0.005, 30 epoch, inisialisasi N(0; 0.1)"]],
      [4 * cm, 11 * cm], "Konfigurasi akhir tiap metode.", align_center_from=9)

H2("6.2 Akurasi prediksi rating dan NDCG (data uji)")
meths = ["Baseline (bias)", "User-based CF", "Item-based CF", "Matrix Factorization"]
cols = {m_: best_bold([F[m][m_] for m in meths], True) for m_ in ["MAE", "MSE", "RMSE", "NMSE"]}
cols["NDCG@10"] = best_bold([F[m]["NDCG@10"] for m in meths], False)
rows = [["Metode", "MAE", "MSE", "RMSE", "NMSE", "NDCG@10"]]
for i, m in enumerate(meths):
    rows.append([m] + [cols[x][i] for x in ["MAE", "MSE", "RMSE", "NMSE", "NDCG@10"]])
table(rows, [4.6 * cm, 2.1 * cm, 2.1 * cm, 2.1 * cm, 2.1 * cm, 2.3 * cm],
      "Hasil pada data uji (20.164 rating). Cetak tebal = terbaik pada kolom tersebut. Galat: lebih kecil lebih baik; NDCG: lebih besar lebih baik.")
figure("figs/f4_compare.png", "Perbandingan MAE, RMSE, dan NDCG@10 pada data uji. Pada NDCG@10 ditambahkan pembanding popularitas dan urutan acak.")

# bootstrap
d = np.load("test_preds.npz")
y = d["y"]
se = {m: (y - d[m.replace(" ", "_")]) ** 2 for m in meths}
rng = np.random.default_rng(0)
B = 1000
idx = [rng.integers(0, len(y), len(y)) for _ in range(B)]
rm = {m: np.array([np.sqrt(se[m][i].mean()) for i in idx]) for m in meths}
pairs = [("Item-based CF", "Matrix Factorization"), ("Item-based CF", "User-based CF"), ("Item-based CF", "Baseline (bias)"),
         ("Matrix Factorization", "User-based CF"), ("Matrix Factorization", "Baseline (bias)"), ("User-based CF", "Baseline (bias)")]
rows = [["Perbandingan (A vs B)", "RMSE(A) − RMSE(B)", "Selang kepercayaan 95%", "Kesimpulan"]]
sig = {}
for a_, b_ in pairs:
    diff = rm[a_] - rm[b_]
    lo, hi = np.percentile(diff, [2.5, 97.5]); mean_ = np.sqrt(se[a_].mean()) - np.sqrt(se[b_].mean())
    verdict = f"A lebih baik" if hi < 0 else ("B lebih baik" if lo > 0 else "tidak signifikan")
    sig[(a_, b_)] = verdict
    rows.append([f"{a_} vs {b_}", f"{mean_:+.4f}", f"[{lo:+.4f}; {hi:+.4f}]", verdict])
table(rows, [6.2 * cm, 3 * cm, 3.8 * cm, 2.6 * cm],
      f"Uji bootstrap berpasangan ({B} resampling pasangan data uji) untuk selisih RMSE. Selisih negatif berarti A lebih akurat.", align_center_from=1, label="tab_boot")
P("Uji bootstrap ini hanya mengukur ketidakpastian akibat pencuplikan data uji; variasi akibat pembagian data lain atau inisialisasi acak MF tidak tercakup (lihat keterbatasan di Bagian 8).")

H2("6.3 Konvergensi Matrix Factorization")
figure("figs/f3_mf_curve.png", "RMSE train dan test pada tiap epoch pelatihan MF.", label="fig_mfcurve", width=330)
last = R["mf_curve"][-1]
P(f"RMSE train terus turun hingga {fmt(last['train_rmse'])} pada epoch ke-30, sedangkan RMSE test turun lebih lambat hingga {fmt(last['eval_rmse'])}. Selisih keduanya menandakan model mulai menghafal data latih; "
  "namun RMSE test belum berbalik naik, sehingga regularisasi λ = 0.05 masih cukup menahan overfitting dalam 30 epoch.")

H2("6.4 Kualitas rekomendasi top-N (ranking penuh)")
rows = [["Metode", "NDCG@10", "Precision@10", "Recall@10"]]
mm = meths + ["Popularitas", "Acak"]
nd = best_bold([F[m]["NDCG_rank"] for m in mm], False); pr = best_bold([F[m]["Precision"] for m in mm], False); rc = best_bold([F[m]["Recall"] for m in mm], False)
for i, m in enumerate(mm):
    rows.append([m, nd[i], pr[i], rc[i]])
table(rows, [5 * cm, 3 * cm, 3 * cm, 3 * cm], "Evaluasi ranking penuh pada data uji (relevan = rating ≥ 4; kandidat = film dengan ≥ 20 rating di data latih).")
figure("figs/f5_topn.png", label="fig_topn", caption="Kiri: pengaruh batas minimum jumlah rating film kandidat terhadap NDCG@10 ranking penuh. Kanan: perbandingan pada batas 20 rating.")
P("Pada ranking penuh, semua metode personal berada di bawah rekomendasi popularitas. Namun Gambar kiri memperlihatkan bahwa kualitas UB-CF dan IB-CF sangat bergantung pada batas "
  "minimum jumlah rating kandidat: tanpa batas, film yang hanya dinilai 1–2 orang dengan rating tinggi membanjiri daftar dan NDCG hampir nol; dengan batas 100 rating, NDCG mereka naik tajam mendekati popularitas.")

H2("6.5 Contoh prediksi rating")
rows = [["User", "Film (data uji)", "Aktual", "UB-CF", "IB-CF", "MF"]]
for s_ in R["samples"]:
    rows.append([str(s_["user"]), Paragraph(escape(s_["movie"]), cell), f"{s_['actual']:.1f}", f"{s_['User-based CF']:.2f}", f"{s_['Item-based CF']:.2f}", f"{s_['Matrix Factorization']:.2f}"])
table(rows, [1.3 * cm, 7.2 * cm, 1.7 * cm, 1.7 * cm, 1.7 * cm, 1.7 * cm], "Sepuluh pasangan (user, film) acak dari data uji beserta prediksi tiap metode.", align_center_from=2)

H2("6.6 Contoh rekomendasi top-10")
hist_txt = "; ".join(f"{escape(h['title'])} ({h['rating']:.0f})" for h in R["demo_history"])
P(f"Contoh untuk pengguna <b>{R['demo_user']}</b>. Film berating tertinggi miliknya pada data latih: {hist_txt}.")
rows = [["#", "User-based CF", "Item-based CF", "Matrix Factorization"]]
for k in range(10):
    rows.append([str(k + 1)] + [Paragraph(f"{escape(R['recs'][m][k]['title'])} <font color='#777777'>({R['recs'][m][k]['pred']:.2f})</font>", cell)
                                for m in ["User-based CF", "Item-based CF", "Matrix Factorization"]])
table(rows, [0.8 * cm, 5.4 * cm, 5.4 * cm, 5.4 * cm], "Rekomendasi top-10 (prediksi rating dalam kurung).", align_center_from=0)
P("Daftar rekomendasi didominasi film klasik berating tinggi dan banyak dikenal. Ketiga metode menghasilkan daftar yang berbeda namun beririsan "
  "(misalnya <i>The Shawshank Redemption</i> dan <i>Wallace &amp; Gromit</i> muncul pada ketiganya). Sebagian rekomendasi tidak serumpun dengan film yang paling disukai pengguna ini (aksi dan komedi), "
  "yang sejalan dengan temuan Bagian 6.4 bahwa prediksi rating tinggi cenderung jatuh pada film yang disukai banyak orang.")

H2("6.7 Waktu komputasi")
T = R["timing"]
table([["Metode", "Waktu (detik)", "Keterangan"],
       ["User-based CF", f"{T['User-based CF']:.0f}", "kemiripan 610 × 610 + prediksi seluruh matriks"],
       ["Item-based CF", f"{T['Item-based CF']:.0f}", "kemiripan 9.724 × 9.724 + prediksi seluruh matriks"],
       ["Matrix Factorization", f"{T['Matrix Factorization']:.0f}", "SGD 30 epoch (loop Python murni) + prediksi seluruh matriks"]],
      [4 * cm, 3 * cm, 8 * cm], "Waktu komputasi pada satu inti CPU. Angka ini bergantung pada implementasi dan hanya indikatif.", align_center_from=1, label="tab_time")

# ------------------------------------------------------------------ 7. analisis
H1("7. Analisis")
ib, mf, ub, bs = F["Item-based CF"], F["Matrix Factorization"], F["User-based CF"], F["Baseline (bias)"]
imp = lambda a, b: (b - a) / b * 100
P(f"<b>Akurasi prediksi rating.</b> IB-CF terbaik pada semua metrik galat (RMSE {fmt(ib['RMSE'])}), disusul MF ({fmt(mf['RMSE'])}); pada RMSE, MSE, dan NMSE baseline ({fmt(bs['RMSE'])}) mengungguli UB-CF ({fmt(ub['RMSE'])}). "
  f"IB-CF menurunkan RMSE {imp(ib['RMSE'], bs['RMSE']):.1f}% dari baseline dan menjelaskan sekitar {(1-ib['NMSE'])*100:.0f}% varians rating uji (NMSE {fmt(ib['NMSE'])}); nilai NMSE seluruh metode berada di bawah 1, "
  f"artinya semuanya lebih baik daripada menebak rata-rata. Pada uji bootstrap (Tabel {L('tab_boot')}), selang kepercayaan 95% untuk selisih RMSE IB-CF terhadap MF, UB-CF, dan baseline seluruhnya berada di bawah nol, "
  "sehingga keunggulan IB-CF konsisten pada data uji ini.")
P(f"<b>Mengapa UB-CF paling lemah?</b> UB-CF memerlukan <i>pengguna lain yang sudah menilai film target</i>. Karena sebagian besar film hanya dinilai segelintir orang (median {int(np.median(pi))} rating per film), "
  "prediksi untuk film jarang bergantung pada satu-dua tetangga atau jatuh ke nilai cadangan. Selain itu, kemiripan antar pengguna dihitung dari film yang dinilai bersama yang sering sedikit. "
  f"Hasilnya, RMSE UB-CF ({fmt(ub['RMSE'])}) bahkan lebih buruk daripada baseline ({fmt(bs['RMSE'])}) meskipun MAE-nya sedikit lebih baik ({fmt(ub['MAE'])} vs {fmt(bs['MAE'])}); "
  "kombinasi ini mengindikasikan UB-CF cukup tepat pada sebagian besar prediksi tetapi sesekali membuat galat besar (RMSE lebih sensitif terhadap galat besar). "
  f"Perlu dicatat bahwa penjelasan ini merupakan interpretasi kami berdasarkan karakteristik data; kami tidak menguji penyebabnya secara terpisah. Selisih UB-CF terhadap baseline pun perlu dibaca sesuai selang kepercayaan pada Tabel {L('tab_boot')}.")
P("<b>Mengapa IB-CF unggul?</b> Pengguna rata-rata telah menilai puluhan hingga ratusan film, jadi untuk memprediksi (u, i) tersedia banyak item bertetangga yang <i>sudah dinilai u</i>. "
  "Kemiripan antar film juga lebih stabil karena tidak berubah mengikuti perubahan selera satu pengguna. Pemusatan rating pada rata-rata pengguna (adjusted cosine) dan significance weighting membantu menekan derau.")
P(f"<b>Matrix Factorization</b> memperbaiki baseline (RMSE {fmt(mf['RMSE'])} vs {fmt(bs['RMSE'])}) tetapi tidak sebaik IB-CF pada konfigurasi ini. Dengan data hanya 80 ribu rating latih, faktor laten yang banyak mudah overfit "
  f"(terlihat dari selisih RMSE train–test pada Gambar {L('fig_mfcurve')} dan dari tuning: 50 faktor dengan λ kecil paling buruk). Kurva test pun belum benar-benar mendatar pada epoch 30, "
  "sehingga pelatihan lebih panjang, tuning learning rate, atau variasi seperti SVD++ mungkin memperbaikinya; ini tidak kami uji. Keunggulan MF yang lebih jelas biasanya muncul pada data yang jauh lebih besar dan pada waktu prediksi (cukup satu hasil kali vektor per pasangan).")
P(f"<b>NDCG@10 pada item uji.</b> Nilai ketiga metode berkisar {fmt(min(ub['NDCG@10'],mf['NDCG@10'],ib['NDCG@10']),3)}–{fmt(max(ub['NDCG@10'],mf['NDCG@10'],ib['NDCG@10']),3)}, jauh di atas urutan acak ({fmt(F['Acak']['NDCG@10'],3)}) dan popularitas ({fmt(F['Popularitas']['NDCG@10'],3)}), "
  "sehingga model memang mampu membedakan film yang lebih disukai dari yang kurang disukai oleh pengguna yang sama. Akan tetapi selisih antar metode kecil (kurang dari 0.01), dan baseline bias pun mencapai "
  f"{fmt(bs['NDCG@10'],3)}. Artinya sebagian besar kemampuan mengurutkan berasal dari bias film (kualitas umum film); kontribusi tambahan CF/MF terhadap urutan di dalam daftar film yang sudah ditonton relatif kecil. "
  "Selisih sekecil ini sebaiknya tidak dijadikan dasar menyatakan satu metode lebih baik, karena kami tidak melakukan uji signifikansi untuk NDCG.")
P(f"<b>Akurasi prediksi rating tidak sama dengan kualitas rekomendasi.</b> Pada ranking penuh, IB-CF, UB-CF, dan MF hanya mencapai NDCG@10 sekitar {fmt(min(ub['NDCG_rank'],mf['NDCG_rank'],ib['NDCG_rank']),3)}–{fmt(max(ub['NDCG_rank'],mf['NDCG_rank'],ib['NDCG_rank']),3)}, "
  f"di bawah baseline ({fmt(bs['NDCG_rank'],3)}) dan popularitas ({fmt(F['Popularitas']['NDCG_rank'],3)}), walaupun di atas acak ({fmt(F['Acak']['NDCG_rank'],3)}). Ada dua alasan yang masuk akal. "
  f"(1) Model yang dilatih untuk meminimalkan galat rating cenderung memberi prediksi tertinggi kepada film langka yang kebetulan dinilai tinggi oleh sedikit orang. Gambar {L('fig_topn')} (kiri) mendukung hal ini: menaikkan batas minimum jumlah rating kandidat "
  "meningkatkan NDCG UB-CF dan IB-CF dari mendekati nol menjadi sekitar 0.14. (2) Film pada data uji adalah film yang <i>dipilih sendiri</i> oleh pengguna untuk ditonton, sehingga data amat condong ke film populer; "
  "protokol ini menguntungkan rekomendasi popularitas. Karena itu, kami tidak menyimpulkan bahwa metode personal 'tidak berguna', melainkan bahwa model rating murni perlu dipadukan dengan filter dukungan, atau dilatih dengan tujuan ranking, untuk top-N.")
P(f"<b>Biaya komputasi.</b> UB-CF dan IB-CF tidak memerlukan fase pelatihan iteratif tetapi menuntut perhitungan kemiripan (610² untuk pengguna dan 9.724² untuk film; IB-CF memakan memori terbesar). "
  f"MF memerlukan pelatihan iteratif namun menghasilkan model kecil dan prediksi yang cepat. Waktu pada Tabel {L('tab_time')} hanya indikatif karena bergantung pada implementasi (UB/IB divektorkan dengan NumPy, MF memakai loop Python).")

# ------------------------------------------------------------------ 8. kesimpulan
H1("8. Kesimpulan")
P(f"1. Ketiga metode berhasil diimplementasikan dan diuji pada MovieLens dengan skema hold-out per pengguna, tuning pada data validasi, dan lima metrik (MAE, MSE, RMSE, NMSE, NDCG).", bodyL)
P(f"2. Untuk <b>prediksi rating</b>, Item-based CF paling akurat (MAE {fmt(ib['MAE'])}, RMSE {fmt(ib['RMSE'])}), diikuti Matrix Factorization (RMSE {fmt(mf['RMSE'])}); User-based CF paling lemah (RMSE {fmt(ub['RMSE'])}), "
  "terutama karena sebagian besar film hanya memiliki sedikit penilai.", bodyL)
P("3. Untuk <b>pengurutan</b> pada item yang telah dinilai pengguna, ketiga metode jauh lebih baik daripada acak dengan selisih antar metode yang kecil. Pada ranking penuh, tidak satu pun metode personal mengalahkan popularitas pada protokol ini; "
  "filter jumlah rating minimum pada kandidat sangat berpengaruh.", bodyL)
P("4. Pemilihan hyperparameter (k, jumlah faktor, λ) berpengaruh nyata dan harus dilakukan pada data validasi terpisah dari data uji.", bodyL)
P("<b>Keterbatasan dan saran.</b> (a) Hasil berasal dari satu kali pembagian data; validasi silang akan memberi estimasi variasi yang lebih baik. (b) Dataset relatif kecil; dataset yang lebih besar (misalnya MovieLens 1M atau 25M) "
  "dapat mengubah urutan metode, khususnya untuk MF. (c) β = 10, learning rate, dan jumlah epoch tidak di-tuning. (d) Model hybrid (CF + popularitas/konten) dan fungsi tujuan berbasis ranking (BPR, ALS implisit) layak dicoba untuk top-N.", body)

# ------------------------------------------------------------------ lampiran
H1("Lampiran A. Cara Menjalankan Source Code")
P("Source code (<i>recsys.py</i>, <i>make_figs.py</i>, <i>make_shots.py</i>, <i>make_report.py</i>) dan berkas data berada pada repository berikut: " + escape(LINK) + ". Akses repository telah diberikan kepada bayzal@gmail.com.")
code_txt = Paragraph("pip install numpy scipy pandas matplotlib pygments reportlab pillow<br/>"
                     "# letakkan ratings.csv dan movies.csv (MovieLens ml-latest-small) di folder yang sama<br/>"
                     "python recsys.py        # tuning + evaluasi tiga metode -&gt; results.json, test_preds.npz<br/>"
                     "python make_figs.py     # grafik dan gambar rumus<br/>"
                     "python make_shots.py    # cuplikan kode (gambar)<br/>"
                     "python make_report.py   # menyusun laporan PDF",
                     ParagraphStyle("mono", fontName="DV", fontSize=8, leading=11.5, backColor=colors.HexColor("#f2f2f2"), borderPadding=6, spaceAfter=10))
story.append(code_txt)
P("Seluruh eksperimen memakai seed 42 sehingga hasil dapat direproduksi. Waktu total sekitar 6 menit pada satu inti CPU.")

H1("Referensi")
for ref in ["Harper, F. M., &amp; Konstan, J. A. (2015). The MovieLens Datasets: History and Context. <i>ACM Transactions on Interactive Intelligent Systems</i>, 5(4).",
            "Resnick, P., Iacovou, N., Suchak, M., Bergstrom, P., &amp; Riedl, J. (1994). GroupLens: An Open Architecture for Collaborative Filtering of Netnews. <i>CSCW '94</i>.",
            "Sarwar, B., Karypis, G., Konstan, J., &amp; Riedl, J. (2001). Item-based Collaborative Filtering Recommendation Algorithms. <i>WWW '01</i>.",
            "Koren, Y., Bell, R., &amp; Volinsky, C. (2009). Matrix Factorization Techniques for Recommender Systems. <i>Computer</i>, 42(8).",
            "Järvelin, K., &amp; Kekäläinen, J. (2002). Cumulated Gain-based Evaluation of IR Techniques. <i>ACM TOIS</i>, 20(4).",
            "Baizal, Z. K. A., &amp; Agung Toto W. <i>Sistem Rekomendasi</i> (buku acuan mata kuliah)."]:
    story.append(Paragraph("• " + ref, ParagraphStyle("ref", parent=body, leftIndent=12, firstLineIndent=-8, fontSize=8.5, leading=12, alignment=TA_LEFT, spaceAfter=2)))


# ------------------------------------------------------------------ build
def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("DV", 7.5); canvas.setFillColor(colors.HexColor("#777777"))
    canvas.drawString(2 * cm, 1.2 * cm, "Laporan Tugas Kelompok – Sistem Rekomendasi")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Halaman {doc.page}")
    canvas.setStrokeColor(colors.HexColor("#cccccc")); canvas.line(2 * cm, 1.55 * cm, A4[0] - 2 * cm, 1.55 * cm)
    canvas.restoreState()


doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=2.1 * cm,
                      title="Laporan Tugas Kelompok - Sistem Rekomendasi", author="Kelompok")
doc.addPageTemplates([PageTemplate(id="p", frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")], onPage=footer)])
doc.build(story)
json.dump(NEWLAB, open(LAB_FILE, "w"))
print("PDF dibuat:", OUT, "| gambar:", fig_n[0], "| tabel:", tab_n[0])
