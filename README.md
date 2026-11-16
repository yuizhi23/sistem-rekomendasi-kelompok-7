# Sistem Rekomendasi: UB-CF, IB-CF, Matrix Factorization

Dataset: MovieLens ml-latest-small (610 user, 9.724 film, 100.836 rating).
Metrik: MAE, MSE, RMSE, NMSE, NDCG@10.

## Menjalankan
    pip install numpy scipy pandas matplotlib pygments reportlab pillow
    python recsys.py        # tuning + evaluasi -> results.json (±6 menit, 1 CPU)
    python save_preds.py    # simpan prediksi uji (untuk bootstrap di laporan)
    python make_figs.py     # grafik & rumus
    python make_shots.py    # cuplikan kode
    python make_report.py   # laporan PDF (jalankan 2x agar nomor rujukan benar)

Seed tetap (42), hasil dapat direproduksi. Isi nomor kelompok, anggota, dan link repo di bagian atas make_report.py.
