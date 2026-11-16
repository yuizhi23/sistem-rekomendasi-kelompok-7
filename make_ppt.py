# -*- coding: utf-8 -*-
"""
Generator PPT - Sistem Rekomendasi Kelompok 7
Menggunakan python-pptx
"""
import json
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
from pptx.chart.data import ChartData
from pptx.enum.chart import XL_CHART_TYPE
import copy

# ── Warna tema ──────────────────────────────────────────────
NAVY   = RGBColor(0x14, 0x21, 0x3D)   # #14213D
TEAL   = RGBColor(0x00, 0x79, 0x8C)   # #00798C
GOLD   = RGBColor(0xED, 0xAE, 0x49)   # #EDAE49
RED    = RGBColor(0xD1, 0x49, 0x5B)   # #D1495B
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT  = RGBColor(0xEE, 0xF3, 0xF6)
GRAY   = RGBColor(0x55, 0x55, 0x55)
GREEN  = RGBColor(0x2E, 0x9E, 0x44)

# ── Load data ────────────────────────────────────────────────
with open("results.json") as f:
    R = json.load(f)
F = R["final"]

prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)

BLANK = prs.slide_layouts[6]  # completely blank

W = float(prs.slide_width)
H = float(prs.slide_height)


# ════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════

def add_rect(slide, x, y, w, h, fill=None, line=None, line_w=Pt(0)):
    shape = slide.shapes.add_shape(1, Emu(x), Emu(y), Emu(w), Emu(h))
    shape.line.width = line_w
    if fill:
        shape.fill.solid(); shape.fill.fore_color.rgb = fill
    else:
        shape.fill.background()
    if line:
        shape.line.color.rgb = line
    else:
        shape.line.fill.background()
    return shape


def add_text(slide, text, x, y, w, h,
             size=18, bold=False, color=WHITE,
             align=PP_ALIGN.LEFT, wrap=True, italic=False):
    txb = slide.shapes.add_textbox(Emu(x), Emu(y), Emu(w), Emu(h))
    txb.word_wrap = wrap
    tf = txb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name = "Calibri"
    return txb


def add_multiline(slide, lines, x, y, w, h,
                  size=16, color=WHITE, bold_first=False, bullet=False):
    """lines = list of str or (text, bold, size, color)"""
    txb = slide.shapes.add_textbox(Emu(x), Emu(y), Emu(w), Emu(h))
    txb.word_wrap = True
    tf = txb.text_frame
    tf.word_wrap = True
    for li, line in enumerate(lines):
        if isinstance(line, str):
            txt, b, sz, col = line, (bold_first and li == 0), size, color
        else:
            txt, b, sz, col = line[0], line[1], line[2] if len(line) > 2 else size, line[3] if len(line) > 3 else color
        p = tf.add_paragraph() if li > 0 else tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        if bullet and li > 0:
            p.level = 1
        run = p.add_run()
        run.text = ("• " + txt) if bullet and li > 0 else txt
        run.font.size = Pt(sz)
        run.font.bold = b
        run.font.color.rgb = col
        run.font.name = "Calibri"
    return txb


def header_bar(slide, title, subtitle=None):
    """Top navy bar with title."""
    add_rect(slide, 0, 0, W, Inches(1.15), fill=NAVY)
    add_text(slide, title, Inches(0.4), Inches(0.12), W - Inches(0.8), Inches(0.6),
             size=24, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
    if subtitle:
        add_text(slide, subtitle, Inches(0.4), Inches(0.72), W - Inches(0.8), Inches(0.4),
                 size=13, bold=False, color=RGBColor(0xAA, 0xCC, 0xDD), align=PP_ALIGN.LEFT)
    # teal accent line
    add_rect(slide, 0, Inches(1.15), W, Inches(0.055), fill=TEAL)


def slide_number(slide, n, total):
    add_text(slide, f"{n} / {total}", W - Inches(1.3), H - Inches(0.38),
             Inches(1.2), Inches(0.3), size=10, color=GRAY, align=PP_ALIGN.RIGHT)


def footer_bar(slide):
    add_rect(slide, 0, H - Inches(0.32), W, Inches(0.32), fill=NAVY)
    add_text(slide, "Kelompok 7  ·  Sistem Rekomendasi  ·  Dataset MovieLens",
             Inches(0.3), H - Inches(0.30), W - Inches(0.6), Inches(0.28),
             size=9, color=RGBColor(0xAA, 0xCC, 0xDD), align=PP_ALIGN.CENTER)


TOTAL = 12  # slide count


# ════════════════════════════════════════════════════════════
# SLIDE 1 — COVER
# ════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)

# Full navy background
add_rect(sl, 0, 0, W, H, fill=NAVY)

# Decorative teal accent top
add_rect(sl, 0, 0, W, Inches(0.18), fill=TEAL)

# Left teal vertical stripe
add_rect(sl, 0, Inches(0.18), Inches(0.18), H - Inches(0.18), fill=TEAL)

# Gold accent bottom
add_rect(sl, 0, H - Inches(0.18), W, Inches(0.18), fill=GOLD)

# Title box (white background card)
add_rect(sl, Inches(0.5), Inches(0.9), W - Inches(1.0), Inches(2.6),
         fill=RGBColor(0x1C, 0x2E, 0x50), line=TEAL, line_w=Pt(2))

# Title text
add_text(sl, "Sistem Rekomendasi", Inches(0.7), Inches(1.0), W - Inches(1.4), Inches(0.75),
         size=38, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
add_text(sl, "Prediksi Rating & Rekomendasi Item", Inches(0.7), Inches(1.75), W - Inches(1.4), Inches(0.55),
         size=22, bold=False, color=TEAL, align=PP_ALIGN.CENTER)
add_text(sl, "User-based CF  ·  Item-based CF  ·  Matrix Factorization",
         Inches(0.7), Inches(2.3), W - Inches(1.4), Inches(0.45),
         size=14, bold=False, color=RGBColor(0xAA, 0xCC, 0xDD), align=PP_ALIGN.CENTER)

# Dataset badge
add_rect(sl, Inches(4.5), Inches(3.65), Inches(4.3), Inches(0.42),
         fill=TEAL)
add_text(sl, "📊  Dataset: MovieLens ml-latest-small",
         Inches(4.5), Inches(3.65), Inches(4.3), Inches(0.42),
         size=13, bold=False, color=WHITE, align=PP_ALIGN.CENTER)

# Member list
members = [
    ("Yukie Ramadhani Kiyoshi", "103012300093"),
    ("Sri Dewi Septiani Nur",   "103012300360"),
    ("Kayla Ulfiyah Haurani",   "103012300490"),
    ("Farha Amirah Hasibuan",   "103012330345"),
]
# Member card background
add_rect(sl, Inches(0.5), Inches(4.25), W - Inches(1.0), Inches(2.6),
         fill=RGBColor(0x1C, 0x2E, 0x50))

add_text(sl, "KELOMPOK 7", Inches(0.6), Inches(4.3), W - Inches(1.2), Inches(0.4),
         size=13, bold=True, color=GOLD, align=PP_ALIGN.LEFT)

for i, (name, nim) in enumerate(members):
    yy = Inches(4.72) + i * Inches(0.52)
    add_text(sl, f"  {i+1}.  {name}", Inches(0.6), yy, Inches(7.0), Inches(0.45),
             size=14, bold=False, color=WHITE, align=PP_ALIGN.LEFT)
    add_text(sl, nim, Inches(8.0), yy, Inches(4.0), Inches(0.45),
             size=14, bold=False, color=RGBColor(0xAA, 0xCC, 0xDD), align=PP_ALIGN.LEFT)

slide_number(sl, 1, TOTAL)


# ════════════════════════════════════════════════════════════
# SLIDE 2 — AGENDA / OUTLINE
# ════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
add_rect(sl, 0, 0, W, H, fill=LIGHT)
header_bar(sl, "Agenda", "Alur presentasi")
footer_bar(sl)

items = [
    ("1", "Latar Belakang & Tujuan",    "Mengapa sistem rekomendasi penting?"),
    ("2", "Dataset MovieLens",           "610 user · 9.724 film · 100.836 rating"),
    ("3", "Metode: User-based CF",       "Kemiripan antar pengguna (Pearson)"),
    ("4", "Metode: Item-based CF",       "Kemiripan antar item (Adjusted Cosine)"),
    ("5", "Metode: Matrix Factorization","Funk-SVD + bias, latih dengan SGD"),
    ("6", "Metrik Evaluasi",             "MAE, MSE, RMSE, NMSE, NDCG@10"),
    ("7", "Hasil & Perbandingan",        "Item-based CF terbaik pada prediksi rating"),
    ("8", "Kesimpulan & Analisis",       "Temuan utama dan keterbatasan"),
]

cols = 2
per_col = 4
for idx, (num, title, desc) in enumerate(items):
    col = idx // per_col
    row = idx % per_col
    x = Inches(0.5) + col * Inches(6.4)
    y = Inches(1.4) + row * Inches(1.35)
    # card
    add_rect(sl, x, y, Inches(5.9), Inches(1.18),
             fill=NAVY if idx % 2 == 0 else RGBColor(0x1C, 0x2E, 0x50))
    # number circle
    add_rect(sl, x + Inches(0.12), y + Inches(0.22), Inches(0.55), Inches(0.55), fill=TEAL)
    add_text(sl, num, x + Inches(0.12), y + Inches(0.22), Inches(0.55), Inches(0.55),
             size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    # title
    add_text(sl, title, x + Inches(0.78), y + Inches(0.1), Inches(5.0), Inches(0.45),
             size=14, bold=True, color=WHITE)
    add_text(sl, desc,  x + Inches(0.78), y + Inches(0.55), Inches(5.0), Inches(0.5),
             size=11, bold=False, color=RGBColor(0xAA, 0xCC, 0xDD))

slide_number(sl, 2, TOTAL)


# ════════════════════════════════════════════════════════════
# SLIDE 3 — LATAR BELAKANG
# ════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
add_rect(sl, 0, 0, W, H, fill=LIGHT)
header_bar(sl, "Latar Belakang", "Mengapa Sistem Rekomendasi?")
footer_bar(sl)

# Left box — problem
add_rect(sl, Inches(0.4), Inches(1.4), Inches(5.5), Inches(5.6), fill=NAVY)
add_text(sl, "😩  Masalah", Inches(0.6), Inches(1.5), Inches(5.0), Inches(0.5),
         size=16, bold=True, color=GOLD)
problems = [
    "Pengguna kewalahan memilih dari jutaan item",
    "Sulit menemukan konten yang benar-benar relevan",
    "Waktu dan energi terbuang untuk eksplorasi manual",
    "Platform kehilangan engagement pengguna",
]
for i, p in enumerate(problems):
    add_text(sl, f"• {p}", Inches(0.6), Inches(2.1) + i * Inches(0.65),
             Inches(5.1), Inches(0.6), size=13, color=WHITE)

# Right box — solution
add_rect(sl, Inches(6.4), Inches(1.4), Inches(6.5), Inches(5.6),
         fill=RGBColor(0x00, 0x55, 0x66))
add_text(sl, "✅  Solusi: Sistem Rekomendasi", Inches(6.6), Inches(1.5),
         Inches(6.1), Inches(0.5), size=16, bold=True, color=GOLD)
solutions = [
    ("Collaborative Filtering", "Memanfaatkan riwayat rating pengguna lain"),
    ("Item-based CF",           "Kemiripan antar item untuk prediksi"),
    ("Matrix Factorization",    "Faktor laten tersembunyi dalam data rating"),
]
for i, (ttl, desc) in enumerate(solutions):
    add_text(sl, ttl, Inches(6.6), Inches(2.15) + i * Inches(1.5),
             Inches(5.8), Inches(0.42), size=14, bold=True, color=WHITE)
    add_text(sl, desc, Inches(6.6), Inches(2.57) + i * Inches(1.5),
             Inches(5.8), Inches(0.4), size=12, color=RGBColor(0xAA, 0xDD, 0xEE))

slide_number(sl, 3, TOTAL)


# ════════════════════════════════════════════════════════════
# SLIDE 4 — DATASET
# ════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
add_rect(sl, 0, 0, W, H, fill=LIGHT)
header_bar(sl, "Dataset: MovieLens (ml-latest-small)",
           "Sumber: GroupLens Research, Universitas Minnesota")
footer_bar(sl)

# Stats cards row
stats = [
    ("👤", "610", "Pengguna"),
    ("🎬", "9.724", "Film"),
    ("⭐", "100.836", "Rating"),
    ("📉", "98.3%", "Sparsity"),
    ("📊", "0.5–5.0", "Skala Rating"),
]
card_w = Inches(2.3)
card_h = Inches(1.5)
for i, (icon, val, lbl) in enumerate(stats):
    x = Inches(0.4) + i * Inches(2.5)
    y = Inches(1.5)
    add_rect(sl, x, y, card_w, card_h, fill=NAVY)
    add_rect(sl, x, y, card_w, Inches(0.07), fill=TEAL)
    add_text(sl, icon, x, y + Inches(0.1), card_w, Inches(0.55),
             size=22, color=WHITE, align=PP_ALIGN.CENTER)
    add_text(sl, val, x, y + Inches(0.6), card_w, Inches(0.55),
             size=20, bold=True, color=GOLD, align=PP_ALIGN.CENTER)
    add_text(sl, lbl, x, y + Inches(1.1), card_w, Inches(0.35),
             size=11, color=RGBColor(0xAA, 0xCC, 0xDD), align=PP_ALIGN.CENTER)

# Data structure info
add_rect(sl, Inches(0.4), Inches(3.3), Inches(5.5), Inches(3.6), fill=NAVY)
add_text(sl, "📋  Struktur Data", Inches(0.6), Inches(3.4), Inches(5.0), Inches(0.42),
         size=14, bold=True, color=GOLD)
cols_info = [
    ("userId",    "ID pengguna (1 – 610)"),
    ("movieId",   "ID film"),
    ("rating",    "Nilai 0.5 – 5.0 (kelipatan 0.5)"),
    ("timestamp", "Waktu pemberian rating"),
]
for i, (col, desc) in enumerate(cols_info):
    y = Inches(3.9) + i * Inches(0.65)
    add_rect(sl, Inches(0.6), y, Inches(1.5), Inches(0.4),
             fill=TEAL)
    add_text(sl, col, Inches(0.6), y, Inches(1.5), Inches(0.4),
             size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text(sl, desc, Inches(2.3), y, Inches(3.4), Inches(0.4),
             size=12, color=WHITE)

# Pembagian data
add_rect(sl, Inches(6.3), Inches(3.3), Inches(6.6), Inches(3.6),
         fill=RGBColor(0x1C, 0x2E, 0x50))
add_text(sl, "📐  Skema Pembagian Data", Inches(6.5), Inches(3.4),
         Inches(6.1), Inches(0.42), size=14, bold=True, color=GOLD)

splits = [
    (TEAL,  "Data Latih",   f"80% = {R['n_train']:,} rating"),
    (RED,   "Data Uji",     f"20% = {R['n_test']:,} rating"),
    (GOLD,  "Data Validasi",f"12.5% dari train = {R['n_val']:,} rating  (untuk tuning)"),
]
for i, (col, lbl, val) in enumerate(splits):
    y = Inches(3.9) + i * Inches(0.9)
    add_rect(sl, Inches(6.5), y + Inches(0.08), Inches(0.3), Inches(0.3), fill=col)
    add_text(sl, lbl, Inches(6.9), y, Inches(2.5), Inches(0.45),
             size=13, bold=True, color=WHITE)
    add_text(sl, val, Inches(6.9), y + Inches(0.38), Inches(5.7), Inches(0.42),
             size=12, color=RGBColor(0xAA, 0xCC, 0xDD))

slide_number(sl, 4, TOTAL)


# ════════════════════════════════════════════════════════════
# SLIDE 5 — USER-BASED CF
# ════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
add_rect(sl, 0, 0, W, H, fill=LIGHT)
header_bar(sl, "Metode 1: User-Based Collaborative Filtering",
           "Gagasan: pengguna dengan selera mirip akan menyukai item yang sama")
footer_bar(sl)

# Left: steps
add_rect(sl, Inches(0.4), Inches(1.4), Inches(5.9), Inches(5.6), fill=NAVY)
add_text(sl, "🔢  Langkah-langkah", Inches(0.6), Inches(1.5),
         Inches(5.5), Inches(0.45), size=15, bold=True, color=GOLD)

steps_ub = [
    ("1", "Hitung Kemiripan Pengguna",
     "Gunakan korelasi Pearson pada film yang sama-sama dinilai. "
     "Significance weighting β=10 untuk menstabilkan nilai."),
    ("2", "Pilih k Tetangga Terdekat",
     f"Pilih k={R['best']['k_user']} pengguna paling mirip yang sudah menilai item target."),
    ("3", "Prediksi Rating",
     "Rata-rata tertimbang selisih rating tetangga dari rata-rata mereka."),
    ("4", "Fallback ke Baseline",
     "Jika tidak ada tetangga, gunakan prediksi bias (μ + bᵤ + bᵢ)."),
]
for i, (n, title, desc) in enumerate(steps_ub):
    y = Inches(2.05) + i * Inches(1.2)
    add_rect(sl, Inches(0.6), y, Inches(0.5), Inches(0.5), fill=TEAL)
    add_text(sl, n, Inches(0.6), y, Inches(0.5), Inches(0.5),
             size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text(sl, title, Inches(1.2), y - Inches(0.02), Inches(4.8), Inches(0.42),
             size=13, bold=True, color=WHITE)
    add_text(sl, desc, Inches(1.2), y + Inches(0.4), Inches(4.8), Inches(0.6),
             size=11, color=RGBColor(0xAA, 0xCC, 0xDD))

# Right: formula + config
add_rect(sl, Inches(6.5), Inches(1.4), Inches(6.4), Inches(2.6),
         fill=RGBColor(0x1C, 0x2E, 0x50))
add_text(sl, "📐  Formula Prediksi", Inches(6.7), Inches(1.5),
         Inches(5.8), Inches(0.42), size=14, bold=True, color=GOLD)
add_text(sl, "r̂ᵤᵢ = r̄ᵤ + Σ sim'(u,v)·(rᵥᵢ − r̄ᵥ) / Σ|sim'(u,v)|",
         Inches(6.7), Inches(2.0), Inches(5.9), Inches(0.6),
         size=12, bold=False, color=WHITE)
add_text(sl, "sim'(u,v) = |Iᵤᵥ| / (|Iᵤᵥ| + β) · sim(u,v)",
         Inches(6.7), Inches(2.65), Inches(5.9), Inches(0.5),
         size=12, bold=False, color=RGBColor(0xAA, 0xCC, 0xDD))
add_text(sl, "di mana Iᵤᵥ = film yang dinilai kedua pengguna bersama",
         Inches(6.7), Inches(3.1), Inches(5.9), Inches(0.42),
         size=10, bold=False, color=GRAY)

# Config card
add_rect(sl, Inches(6.5), Inches(4.2), Inches(6.4), Inches(2.6),
         fill=TEAL)
add_text(sl, "⚙️  Konfigurasi Terpilih", Inches(6.7), Inches(4.3),
         Inches(5.8), Inches(0.42), size=14, bold=True, color=NAVY)
configs = [
    ("Similarity", "Pearson + significance weighting"),
    ("β (shrink)", "10"),
    (f"k tetangga (terpilih)", f"{R['best']['k_user']} (dari validasi data)"),
    ("Fallback",  "Baseline bias"),
]
for i, (k, v) in enumerate(configs):
    add_text(sl, f"• {k}:  {v}", Inches(6.7), Inches(4.8) + i * Inches(0.46),
             Inches(5.8), Inches(0.42), size=12, color=NAVY)

slide_number(sl, 5, TOTAL)


# ════════════════════════════════════════════════════════════
# SLIDE 6 — ITEM-BASED CF
# ════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
add_rect(sl, 0, 0, W, H, fill=LIGHT)
header_bar(sl, "Metode 2: Item-Based Collaborative Filtering",
           "Gagasan: prediksi dari rating user pada film-film yang mirip")
footer_bar(sl)

add_rect(sl, Inches(0.4), Inches(1.4), Inches(5.9), Inches(5.6), fill=NAVY)
add_text(sl, "🔢  Langkah-langkah", Inches(0.6), Inches(1.5),
         Inches(5.5), Inches(0.45), size=15, bold=True, color=GOLD)

steps_ib = [
    ("1", "Hitung Kemiripan Antar Film",
     "Adjusted Cosine: rating dipusatkan ke rata-rata user masing-masing. "
     "Dihitung per blok 1.000 baris agar hemat memori."),
    ("2", "Pilih k Item Tetangga",
     f"Pilih k={R['best']['k_item']} film paling mirip yang sudah dinilai user target."),
    ("3", "Prediksi Rating",
     "Rata-rata rating item + rata-rata tertimbang selisih rating user pada item tetangga."),
    ("4", "Significance Weighting",
     "Bobot dikali |Uᵢⱼ|/(|Uᵢⱼ|+β) agar kemiripan berdasar banyak user lebih dipercaya."),
]
for i, (n, title, desc) in enumerate(steps_ib):
    y = Inches(2.05) + i * Inches(1.2)
    add_rect(sl, Inches(0.6), y, Inches(0.5), Inches(0.5), fill=RED)
    add_text(sl, n, Inches(0.6), y, Inches(0.5), Inches(0.5),
             size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text(sl, title, Inches(1.2), y - Inches(0.02), Inches(4.8), Inches(0.42),
             size=13, bold=True, color=WHITE)
    add_text(sl, desc, Inches(1.2), y + Inches(0.4), Inches(4.8), Inches(0.6),
             size=11, color=RGBColor(0xAA, 0xCC, 0xDD))

add_rect(sl, Inches(6.5), Inches(1.4), Inches(6.4), Inches(2.6),
         fill=RGBColor(0x1C, 0x2E, 0x50))
add_text(sl, "📐  Formula Prediksi", Inches(6.7), Inches(1.5),
         Inches(5.8), Inches(0.42), size=14, bold=True, color=GOLD)
add_text(sl, "r̂ᵤᵢ = r̄ᵢ + Σ sim'(i,j)·(rᵤⱼ − r̄ⱼ) / Σ|sim'(i,j)|",
         Inches(6.7), Inches(2.0), Inches(5.9), Inches(0.6),
         size=12, color=WHITE)
add_text(sl, "sim(i,j) = Adjusted Cosine Similarity",
         Inches(6.7), Inches(2.65), Inches(5.9), Inches(0.42),
         size=12, color=RGBColor(0xAA, 0xCC, 0xDD))
add_text(sl, "j ∈ Nₖ(i,u) = k item termirip yang sudah dinilai user u",
         Inches(6.7), Inches(3.1), Inches(5.9), Inches(0.42),
         size=10, color=GRAY)

add_rect(sl, Inches(6.5), Inches(4.2), Inches(6.4), Inches(2.6), fill=RED)
add_text(sl, "⚙️  Konfigurasi Terpilih", Inches(6.7), Inches(4.3),
         Inches(5.8), Inches(0.42), size=14, bold=True, color=WHITE)
configs_ib = [
    ("Similarity", "Adjusted Cosine + significance weighting"),
    ("β (shrink)", "10"),
    (f"k tetangga (terpilih)", f"{R['best']['k_item']} (dari validasi data)"),
    ("Keunggulan",  "Stabil, banyak film-tetangga tersedia per user"),
]
for i, (k, v) in enumerate(configs_ib):
    add_text(sl, f"• {k}:  {v}", Inches(6.7), Inches(4.8) + i * Inches(0.46),
             Inches(5.8), Inches(0.42), size=12, color=WHITE)

slide_number(sl, 6, TOTAL)


# ════════════════════════════════════════════════════════════
# SLIDE 7 — MATRIX FACTORIZATION
# ════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
add_rect(sl, 0, 0, W, H, fill=LIGHT)
header_bar(sl, "Metode 3: Matrix Factorization (Funk-SVD + Bias)",
           "Latih faktor laten dengan Stochastic Gradient Descent")
footer_bar(sl)

add_rect(sl, Inches(0.4), Inches(1.4), Inches(5.9), Inches(5.6), fill=NAVY)
add_text(sl, "🔢  Langkah-langkah SGD", Inches(0.6), Inches(1.5),
         Inches(5.5), Inches(0.45), size=15, bold=True, color=GOLD)

steps_mf = [
    ("1", "Inisialisasi Parameter",
     "Vektor faktor P (user) dan Q (item) ~ N(0, 0.1). Bias user/item = 0."),
    ("2", "Hitung Error per Rating",
     "eᵤᵢ = rᵤᵢ − (μ + bᵤ + bᵢ + pᵤ · qᵢ)"),
    ("3", "Update Gradien (per epoch)",
     "bᵤ, bᵢ, pᵤ, qᵢ diupdate berlawanan arah gradien dengan learning rate γ=0.005."),
    ("4", "Regularisasi",
     f"λ={R['best']['reg']} diterapkan pada semua parameter untuk mencegah overfitting."),
]
for i, (n, title, desc) in enumerate(steps_mf):
    y = Inches(2.05) + i * Inches(1.2)
    add_rect(sl, Inches(0.6), y, Inches(0.5), Inches(0.5), fill=GOLD)
    add_text(sl, n, Inches(0.6), y, Inches(0.5), Inches(0.5),
             size=16, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
    add_text(sl, title, Inches(1.2), y - Inches(0.02), Inches(4.8), Inches(0.42),
             size=13, bold=True, color=WHITE)
    add_text(sl, desc, Inches(1.2), y + Inches(0.4), Inches(4.8), Inches(0.6),
             size=11, color=RGBColor(0xAA, 0xCC, 0xDD))

# Right: formula + config
add_rect(sl, Inches(6.5), Inches(1.4), Inches(6.4), Inches(2.6),
         fill=RGBColor(0x1C, 0x2E, 0x50))
add_text(sl, "📐  Model & Loss", Inches(6.7), Inches(1.5),
         Inches(5.8), Inches(0.42), size=14, bold=True, color=GOLD)
add_text(sl, "r̂ᵤᵢ = μ + bᵤ + bᵢ + pᵤᵀ qᵢ",
         Inches(6.7), Inches(2.0), Inches(5.9), Inches(0.45), size=14, bold=True, color=WHITE)
add_text(sl, "Loss = Σ(rᵤᵢ − r̂ᵤᵢ)² + λ(bᵤ² + bᵢ² + ‖pᵤ‖² + ‖qᵢ‖²)",
         Inches(6.7), Inches(2.5), Inches(5.9), Inches(0.6), size=11, color=RGBColor(0xAA, 0xCC, 0xDD))

add_rect(sl, Inches(6.5), Inches(4.2), Inches(6.4), Inches(2.6), fill=GOLD)
add_text(sl, "⚙️  Konfigurasi Terpilih", Inches(6.7), Inches(4.3),
         Inches(5.8), Inches(0.42), size=14, bold=True, color=NAVY)
configs_mf = [
    ("Faktor laten (f)", f"{R['best']['n_factors']}"),
    ("Regularisasi (λ)", f"{R['best']['reg']}"),
    ("Learning rate (γ)", "0.005"),
    ("Jumlah epoch",    "30"),
    ("Inisialisasi",    "P, Q ~ N(0, 0.1)"),
]
for i, (k, v) in enumerate(configs_mf):
    add_text(sl, f"• {k}:  {v}", Inches(6.7), Inches(4.8) + i * Inches(0.38),
             Inches(5.8), Inches(0.38), size=12, color=NAVY)

slide_number(sl, 7, TOTAL)


# ════════════════════════════════════════════════════════════
# SLIDE 8 — METRIK EVALUASI
# ════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
add_rect(sl, 0, 0, W, H, fill=LIGHT)
header_bar(sl, "Metrik Evaluasi",
           "Lima metrik digunakan untuk mengukur kualitas prediksi dan rekomendasi")
footer_bar(sl)

metrics = [
    ("MAE", "Mean Absolute Error",
     "Rata-rata |galat| prediksi. Mudah diinterpretasi dalam skala rating.",
     "MAE = (1/n) Σ |rₖ − r̂ₖ|", TEAL),
    ("MSE", "Mean Squared Error",
     "Rata-rata galat kuadrat. Lebih sensitif terhadap galat besar.",
     "MSE = (1/n) Σ (rₖ − r̂ₖ)²", RED),
    ("RMSE", "Root MSE",
     "Akar MSE. Satuan sama dengan rating, paling umum dipakai.",
     "RMSE = √MSE", GOLD),
    ("NMSE", "Normalized MSE",
     "MSE dinormalisasi varians data. NMSE = 1 berarti sama buruknya dengan menebak rata-rata.",
     "NMSE = Σ(rₖ−r̂ₖ)² / Σ(rₖ−r̄)²", RGBColor(0x2E, 0x9E, 0x44)),
    ("NDCG@10", "Normalized Discounted Cumulative Gain",
     "Kualitas urutan rekomendasi. Item relevan di posisi atas diberi bobot lebih besar.",
     "NDCG = DCG / IDCG", RGBColor(0x88, 0x44, 0xCC)),
]

cols_m = 3
for idx, (abbr, name, desc, formula, col) in enumerate(metrics):
    r_m = idx // cols_m
    c_m = idx % cols_m
    offset_x = Inches(0.4) + c_m * Inches(4.2)
    offset_y = Inches(1.4) + r_m * Inches(2.6)
    if idx >= 3:  # bottom row: center 2 cards
        offset_x = Inches(2.5) + (idx - 3) * Inches(4.2)
    card_w_ = Inches(3.9)
    card_h_ = Inches(2.3)
    add_rect(sl, offset_x, offset_y, card_w_, card_h_, fill=NAVY)
    add_rect(sl, offset_x, offset_y, card_w_, Inches(0.08), fill=col)
    add_text(sl, abbr, offset_x + Inches(0.15), offset_y + Inches(0.12),
             Inches(1.2), Inches(0.42), size=18, bold=True, color=col)
    add_text(sl, name, offset_x + Inches(0.15), offset_y + Inches(0.55),
             card_w_ - Inches(0.3), Inches(0.42), size=11, bold=False, color=WHITE)
    add_text(sl, formula, offset_x + Inches(0.15), offset_y + Inches(0.98),
             card_w_ - Inches(0.3), Inches(0.42), size=11, bold=True,
             color=RGBColor(0xAA, 0xDD, 0xFF))
    add_text(sl, desc, offset_x + Inches(0.15), offset_y + Inches(1.42),
             card_w_ - Inches(0.3), Inches(0.72), size=10,
             color=RGBColor(0xAA, 0xCC, 0xDD))

slide_number(sl, 8, TOTAL)


# ════════════════════════════════════════════════════════════
# SLIDE 9 — HASIL EVALUASI (TABLE)
# ════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
add_rect(sl, 0, 0, W, H, fill=LIGHT)
header_bar(sl, "Hasil Evaluasi — Prediksi Rating",
           "Data uji: 20.164 rating  |  ↓ lebih kecil lebih baik  |  ↑ lebih besar lebih baik")
footer_bar(sl)

methods = ["Baseline (bias)", "User-based CF", "Item-based CF", "Matrix Factorization"]
metric_cols = ["MAE", "MSE", "RMSE", "NMSE", "NDCG@10"]

# Table header
col_widths = [Inches(3.0), Inches(1.6), Inches(1.6), Inches(1.6), Inches(1.6), Inches(1.7)]
starts_x = Inches(0.5)
row_h = Inches(0.72)
start_y = Inches(1.4)

# Header row
add_rect(sl, starts_x, start_y, sum(col_widths), row_h, fill=NAVY)
headers = ["Metode"] + metric_cols
for ci, (hdr, cw) in enumerate(zip(headers, col_widths)):
    x_ = starts_x + sum(col_widths[:ci])
    add_text(sl, hdr, x_ + Inches(0.05), start_y + Inches(0.12), cw - Inches(0.1), row_h - Inches(0.1),
             size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

# Find best values per metric
best_vals = {}
for m in metric_cols:
    vals = [F[mth][m] for mth in methods]
    best_vals[m] = min(vals) if m != "NDCG@10" else max(vals)

row_colors = [RGBColor(0xE8, 0xF0, 0xF5), RGBColor(0xD5, 0xE6, 0xED),
              RGBColor(0xE8, 0xF0, 0xF5), RGBColor(0xD5, 0xE6, 0xED)]
method_colors = [GRAY, TEAL, RED, GOLD]

for ri, mth in enumerate(methods):
    y_ = start_y + (ri + 1) * row_h
    add_rect(sl, starts_x, y_, sum(col_widths), row_h, fill=row_colors[ri])
    # method name
    add_rect(sl, starts_x, y_, col_widths[0], row_h, fill=method_colors[ri])
    add_text(sl, mth, starts_x + Inches(0.1), y_ + Inches(0.12),
             col_widths[0] - Inches(0.15), row_h - Inches(0.15),
             size=12, bold=True, color=WHITE)
    # metric values
    for ci, m in enumerate(metric_cols):
        val = F[mth][m]
        is_best = abs(val - best_vals[m]) < 1e-6
        x_ = starts_x + col_widths[0] + sum(col_widths[1:ci+1])
        cell_col = RGBColor(0xFF, 0xF0, 0x80) if is_best else row_colors[ri]
        add_rect(sl, x_, y_, col_widths[ci+1], row_h, fill=cell_col)
        add_text(sl, f"{val:.4f}", x_ + Inches(0.05), y_ + Inches(0.12),
                 col_widths[ci+1] - Inches(0.1), row_h - Inches(0.15),
                 size=13, bold=is_best, color=NAVY if is_best else NAVY,
                 align=PP_ALIGN.CENTER)

# Legend
add_text(sl, "🏆 Kuning = nilai terbaik pada kolom tersebut",
         starts_x, start_y + 5 * row_h + Inches(0.15),
         Inches(10), Inches(0.42), size=11, color=GRAY)

slide_number(sl, 9, TOTAL)


# ════════════════════════════════════════════════════════════
# SLIDE 10 — HASIL VISUALISASI (bar chart manual)
# ════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
add_rect(sl, 0, 0, W, H, fill=LIGHT)
header_bar(sl, "Perbandingan Visual Metrik",
           "RMSE & MAE: semakin kecil semakin baik  |  NDCG@10: semakin besar semakin baik")
footer_bar(sl)

methods_short = ["Baseline", "UB-CF", "IB-CF ✅", "MF"]
method_cols_v = [GRAY, TEAL, RED, GOLD]

# --- RMSE bar ---
add_text(sl, "RMSE (↓ lebih baik)", Inches(0.5), Inches(1.35), Inches(5.0), Inches(0.4),
         size=13, bold=True, color=NAVY)
rmse_vals = [F[m]["RMSE"] for m in methods]
rmse_min, rmse_max = 0.84, 0.90
bar_max_w = Inches(4.5)
for i, (val, col) in enumerate(zip(rmse_vals, method_cols_v)):
    y_ = Inches(1.9) + i * Inches(0.9)
    bw = bar_max_w * (val - rmse_min) / (rmse_max - rmse_min)
    add_text(sl, methods_short[i], Inches(0.5), y_, Inches(1.5), Inches(0.6),
             size=12, bold=False, color=NAVY)
    add_rect(sl, Inches(2.1), y_ + Inches(0.1), max(bw, Inches(0.3)), Inches(0.5), fill=col)
    add_text(sl, f"{val:.4f}", Inches(2.1) + max(bw, Inches(0.3)) + Inches(0.08), y_ + Inches(0.08),
             Inches(1.5), Inches(0.5), size=12, bold=True, color=NAVY)

# --- MAE bar ---
add_text(sl, "MAE (↓ lebih baik)", Inches(0.5), Inches(5.65), Inches(5.0), Inches(0.4),
         size=13, bold=True, color=NAVY)
mae_vals = [F[m]["MAE"] for m in methods]
mae_min, mae_max = 0.63, 0.69
for i, (val, col) in enumerate(zip(mae_vals, method_cols_v)):
    y_ = Inches(6.1) - (len(methods) - i - 1) * Inches(0.0)
    # horizontal small below
add_text(sl, f"Baseline: {mae_vals[0]:.4f} | UB-CF: {mae_vals[1]:.4f} | IB-CF: {mae_vals[2]:.4f} | MF: {mae_vals[3]:.4f}",
         Inches(0.5), Inches(6.0), Inches(10), Inches(0.4), size=12, bold=False, color=NAVY)

# --- NDCG@10 (right panel) ---
add_text(sl, "NDCG@10 (↑ lebih baik)", Inches(7.1), Inches(1.35), Inches(5.0), Inches(0.4),
         size=13, bold=True, color=NAVY)
ndcg_vals = [F[m]["NDCG@10"] for m in methods]
ndcg_min, ndcg_max = 0.795, 0.815
bar_max_w2 = Inches(4.0)
for i, (val, col) in enumerate(zip(ndcg_vals, method_cols_v)):
    y_ = Inches(1.9) + i * Inches(0.9)
    bw = bar_max_w2 * (val - ndcg_min) / (ndcg_max - ndcg_min)
    add_text(sl, methods_short[i], Inches(7.1), y_, Inches(1.5), Inches(0.6),
             size=12, bold=False, color=NAVY)
    add_rect(sl, Inches(8.7), y_ + Inches(0.1), max(bw, Inches(0.1)), Inches(0.5), fill=col)
    add_text(sl, f"{val:.4f}", Inches(8.7) + max(bw, Inches(0.1)) + Inches(0.08), y_ + Inches(0.08),
             Inches(1.5), Inches(0.5), size=12, bold=True, color=NAVY)

# Key finding box
add_rect(sl, Inches(0.4), Inches(5.5), W - Inches(0.8), Inches(1.4), fill=NAVY)
add_text(sl,
         "🏆  Item-based CF terbaik: RMSE 0.8568, MAE 0.6506  |  "
         "Matrix Factorization runner-up: RMSE 0.8664  |  "
         "UB-CF: RMSE 0.8840 (lebih lemah akibat sparsity data)",
         Inches(0.6), Inches(5.6), W - Inches(1.2), Inches(1.2),
         size=12, bold=False, color=WHITE)

slide_number(sl, 10, TOTAL)


# ════════════════════════════════════════════════════════════
# SLIDE 11 — ANALISIS & PEMBAHASAN
# ════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
add_rect(sl, 0, 0, W, H, fill=LIGHT)
header_bar(sl, "Analisis & Pembahasan", "Mengapa hasilnya seperti itu?")
footer_bar(sl)

analyses = [
    (RED,   "Mengapa UB-CF paling lemah?",
     [
         "Sebagian besar film hanya dinilai sedikit user (median hanya beberapa rating per film)",
         "Sulit menemukan tetangga yang sama-sama menilai film target",
         "Prediksi sering jatuh ke nilai cadangan (baseline)",
         "Sesekali membuat galat besar → RMSE lebih sensitif daripada MAE",
     ]),
    (TEAL,  "Mengapa IB-CF paling unggul?",
     [
         "Setiap user sudah menilai banyak film → banyak film-tetangga tersedia",
         "Kemiripan antar film lebih stabil daripada kemiripan antar user",
         "Adjusted Cosine menghilangkan bias skala pemberian nilai per user",
         "Significance weighting menekan derau dari pasangan item yang jarang bersama",
     ]),
    (GOLD,  "Bagaimana Matrix Factorization?",
     [
         "Memperbaiki baseline (RMSE 0.8664 vs 0.8752) tetapi belum melampaui IB-CF",
         "Dengan hanya ~80 ribu rating latih, banyak faktor laten rentan overfitting",
         "Kurva RMSE test belum mendatar pada epoch 30 → masih bisa ditingkatkan",
         "Keunggulan MF umumnya terlihat pada dataset jauh lebih besar",
     ]),
]

for idx, (col, title, points) in enumerate(analyses):
    x_ = Inches(0.4) + idx * Inches(4.3)
    add_rect(sl, x_, Inches(1.4), Inches(4.1), Inches(5.6), fill=NAVY)
    add_rect(sl, x_, Inches(1.4), Inches(4.1), Inches(0.07), fill=col)
    add_text(sl, title, x_ + Inches(0.15), Inches(1.5), Inches(3.8), Inches(0.6),
             size=13, bold=True, color=col)
    for pi, pt in enumerate(points):
        add_text(sl, f"• {pt}", x_ + Inches(0.15), Inches(2.2) + pi * Inches(0.85),
                 Inches(3.85), Inches(0.78), size=11, color=WHITE)

slide_number(sl, 11, TOTAL)


# ════════════════════════════════════════════════════════════
# SLIDE 12 — KESIMPULAN
# ════════════════════════════════════════════════════════════
sl = prs.slides.add_slide(BLANK)
add_rect(sl, 0, 0, W, H, fill=NAVY)
add_rect(sl, 0, 0, W, Inches(0.18), fill=TEAL)
add_rect(sl, 0, H - Inches(0.18), W, Inches(0.18), fill=GOLD)

add_text(sl, "Kesimpulan", Inches(0.5), Inches(0.4), W - Inches(1.0), Inches(0.7),
         size=30, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

conclusions = [
    (TEAL, "1", "Ketiga metode berhasil diimplementasikan dari scratch (Python, NumPy, SciPy) "
                "dan dievaluasi dengan 5 metrik: MAE, MSE, RMSE, NMSE, NDCG@10."),
    (RED,  "2", "Item-based CF terbaik untuk prediksi rating (RMSE 0.8568, MAE 0.6506), "
                "karena lebih banyak item-tetangga tersedia dan kemiripan antar film lebih stabil."),
    (GOLD, "3", "Matrix Factorization runner-up (RMSE 0.8664); performanya dapat ditingkatkan "
                "dengan data lebih besar, lebih banyak epoch, atau model SVD++."),
    (RGBColor(0x2E, 0x9E, 0x44), "4",
     "Hyperparameter (k, f, λ) berpengaruh nyata dan wajib dipilih dari data validasi, "
     "bukan data uji."),
]

for i, (col, num, text) in enumerate(conclusions):
    y_ = Inches(1.35) + i * Inches(1.4)
    add_rect(sl, Inches(0.6), y_, Inches(0.6), Inches(0.6), fill=col)
    add_text(sl, num, Inches(0.6), y_, Inches(0.6), Inches(0.6),
             size=20, bold=True, color=NAVY if col == GOLD else WHITE, align=PP_ALIGN.CENTER)
    add_text(sl, text, Inches(1.4), y_ - Inches(0.05), W - Inches(2.0), Inches(1.3),
             size=14, bold=False, color=WHITE)

# Bottom note
add_rect(sl, Inches(0.5), Inches(7.0), W - Inches(1.0), Inches(0.35),
         fill=RGBColor(0x1C, 0x2E, 0x50))
add_text(sl, f"🔗  github.com/yuizhi23/sistem-rekomendasi-kelompok-7  ·  Akses: bayzal@gmail.com",
         Inches(0.6), Inches(7.02), W - Inches(1.2), Inches(0.33),
         size=11, color=TEAL, align=PP_ALIGN.CENTER)

slide_number(sl, 12, TOTAL)


# ════════════════════════════════════════════════════════════
# SAVE
# ════════════════════════════════════════════════════════════
out = "Presentasi_Sistem_Rekomendasi_Kelompok7.pptx"
prs.save(out)
print(f"PPT selesai: {out}  ({TOTAL} slide)")
