"""
Sistem Rekomendasi - Tugas Kelompok
Metode  : User-based CF, Item-based CF, Matrix Factorization (SGD)
Dataset : MovieLens ml-latest-small (610 user, 9.724 film, 100.836 rating)
Metrik  : MAE, MSE, RMSE, NMSE, NDCG@10
"""
import json, time
import numpy as np
import pandas as pd
from scipy import sparse

SEED = 42


# ============================================================
# 1. DATA: load, split per-user, bentuk matriks user-item
# ============================================================
def load_data(path="."):
    ratings = pd.read_csv(f"{path}/ratings.csv")
    movies = pd.read_csv(f"{path}/movies.csv")
    uid = {u: i for i, u in enumerate(sorted(ratings.userId.unique()))}
    iid = {m: i for i, m in enumerate(sorted(ratings.movieId.unique()))}
    ratings["u"] = ratings.userId.map(uid)
    ratings["i"] = ratings.movieId.map(iid)
    return ratings, movies, uid, iid


def split_per_user(df, test_frac, seed=SEED):
    """Setiap user: sebagian ratingnya disembunyikan sebagai data uji."""
    rng = np.random.default_rng(seed)
    train_idx, test_idx = [], []
    for _, g in df.groupby("u"):
        idx = rng.permutation(g.index.values)
        n_test = max(1, int(round(len(idx) * test_frac)))
        test_idx += list(idx[:n_test])
        train_idx += list(idx[n_test:])
    return df.loc[train_idx].copy(), df.loc[test_idx].copy()


def to_matrix(df, n_users, n_items):
    R = np.zeros((n_users, n_items), dtype=np.float32)
    R[df.u.values, df.i.values] = df.rating.values
    return R  # 0 = belum dirating


# ============================================================
# 2. BASELINE (rata-rata global + bias user + bias item)
#    dipakai sebagai cadangan jika CF tidak punya tetangga
# ============================================================
def fit_baseline(R, reg_i=10.0, reg_u=15.0):
    M = R > 0
    mu = R[M].mean()
    n_i = M.sum(0)
    bi = np.where(n_i > 0, ((R - mu) * M).sum(0) / (n_i + reg_i), 0.0)
    n_u = M.sum(1)
    bu = ((R - mu - bi[None, :]) * M).sum(1) / (n_u + reg_u)
    return mu, bu, bi


def baseline_matrix(mu, bu, bi):
    return mu + bu[:, None] + bi[None, :]


# ============================================================
# 3. USER-BASED COLLABORATIVE FILTERING
#    sim = Pearson (item yang di-rating bersama) x significance weighting
#    pred(u,i) = mean_u + sum_v sim(u,v) * (r_vi - mean_v) / sum_v |sim(u,v)|
#    v = k user paling mirip dengan u yang JUGA me-rating item i
# ============================================================
def _run_per_user(n_users, n_items, pairs, fn):
    """pairs=None -> matriks prediksi penuh; pairs=(u_arr,i_arr) -> vektor prediksi."""
    if pairs is None:
        out = np.zeros((n_users, n_items), np.float32)
        for u in range(n_users):
            out[u] = fn(u, slice(None))
        return out
    u_arr, i_arr = pairs
    out = np.zeros(len(u_arr), np.float32)
    order = np.argsort(u_arr, kind="stable")
    bounds = np.flatnonzero(np.diff(u_arr[order])) + 1
    for grp in np.split(order, bounds):
        out[grp] = fn(u_arr[grp[0]], i_arr[grp])
    return out


def user_similarity(R, shrink=10.0):
    M = (R > 0).astype(np.float64)
    R = R.astype(np.float64)
    n = M @ M.T                          # jumlah item yang dirating bersama
    sx = R @ M.T                         # sum r_u pada item bersama (u,v)
    sxx = (R ** 2) @ M.T
    sxy = R @ R.T
    nn = np.maximum(n, 1)
    cov = sxy - sx * sx.T / nn
    var_u = sxx - sx ** 2 / nn
    var_v = sxx.T - sx.T ** 2 / nn
    den = np.sqrt(np.maximum(var_u, 0) * np.maximum(var_v, 0))
    sim = np.where((den > 1e-9) & (n >= 2), cov / np.maximum(den, 1e-9), 0.0)
    sim *= n / (n + shrink)              # significance weighting
    np.fill_diagonal(sim, 0.0)
    return sim.astype(np.float32)


def user_cf_predict(R, sim, k, fallback, pairs=None):
    M = (R > 0).astype(np.float32)
    mean_u = R.sum(1) / np.maximum(M.sum(1), 1)
    C = (R - mean_u[:, None]) * M        # rating yang sudah dipusatkan

    def predict_user(u, cols):
        Mc, Cc = M[:, cols], C[:, cols]
        w = np.maximum(sim[u][:, None], 0) * Mc          # bobot: hanya penilai item, sim > 0
        if k < w.shape[0]:                               # pertahankan k tetangga terbaik per item
            thr = np.partition(w, -k, axis=0)[-k]
            w = np.where(w >= thr[None, :], w, 0)
        num, den = (w * Cc).sum(0), w.sum(0)
        return np.where(den > 1e-6, mean_u[u] + num / np.maximum(den, 1e-6), fallback[u, cols])

    return _run_per_user(R.shape[0], R.shape[1], pairs, predict_user)


# ============================================================
# 4. ITEM-BASED COLLABORATIVE FILTERING
#    sim = Adjusted Cosine (dipusatkan rata-rata user) x significance weighting
#    pred(u,i) = mean_i + sum_j sim(i,j) * (r_uj - mean_j) / sum_j |sim(i,j)|
#    j = k item paling mirip dengan i yang SUDAH di-rating user u
# ============================================================
def item_similarity(R, shrink=10.0, chunk=1000):
    """Matriks similaritas item x item (dihitung per potongan agar hemat memori)."""
    M = (R > 0).astype(np.float32)
    mean_u = R.sum(1) / np.maximum(M.sum(1), 1)
    C = (R - mean_u[:, None]) * M
    norm = np.sqrt((C ** 2).sum(0)) + 1e-9
    n_items = R.shape[1]
    S = np.zeros((n_items, n_items), dtype=np.float32)
    for a in range(0, n_items, chunk):
        b = min(a + chunk, n_items)
        sim = (C[:, a:b].T @ C) / (norm[a:b, None] * norm[None, :])
        N = M[:, a:b].T @ M              # jumlah user yang me-rating kedua item
        S[a:b] = sim * N / (N + shrink)  # significance weighting
    np.fill_diagonal(S, 0.0)
    return S


def item_cf_predict(R, S, k, fallback, pairs=None):
    M = R > 0
    mu = R[M].mean()
    mean_i = np.where(M.sum(0) > 0, R.sum(0) / np.maximum(M.sum(0), 1), mu)

    def predict_user(u, cols):
        J = np.flatnonzero(M[u])                         # item yang sudah dirating user u
        resid = R[u, J] - mean_i[J]
        w = np.maximum(S[cols][:, J], 0)                 # bobot sim(i, j), hanya sim > 0
        if k < len(J):                                   # k item termirip per target
            thr = np.partition(w, -k, axis=1)[:, -k]
            w = np.where(w >= thr[:, None], w, 0)
        num, den = w @ resid, w.sum(1)
        return np.where(den > 1e-6, mean_i[cols] + num / np.maximum(den, 1e-6), fallback[u, cols])

    return _run_per_user(R.shape[0], R.shape[1], pairs, predict_user)


# ============================================================
# 5. MATRIX FACTORIZATION (Funk-SVD dengan bias, dilatih dengan SGD)
#    r_hat(u,i) = mu + b_u + b_i + p_u . q_i
#    min  sum (r - r_hat)^2 + lambda (b_u^2 + b_i^2 + |p_u|^2 + |q_i|^2)
# ============================================================
def mf_sgd(train, n_users, n_items, n_factors=20, lr=0.005, reg=0.02,
           epochs=25, seed=SEED, eval_df=None):
    rng = np.random.default_rng(seed)
    u_arr, i_arr = train.u.values, train.i.values
    r_arr = train.rating.values.astype(np.float64)
    mu = r_arr.mean()
    bu, bi = np.zeros(n_users), np.zeros(n_items)
    P = rng.normal(0, 0.1, (n_users, n_factors))
    Q = rng.normal(0, 0.1, (n_items, n_factors))
    curve = []
    for ep in range(epochs):
        for t in rng.permutation(len(r_arr)):
            u, i, r = u_arr[t], i_arr[t], r_arr[t]
            pu, qi = P[u], Q[i]
            err = r - (mu + bu[u] + bi[i] + pu @ qi)
            bu[u] += lr * (err - reg * bu[u])
            bi[i] += lr * (err - reg * bi[i])
            pu_old = pu.copy()
            P[u] += lr * (err * qi - reg * pu)
            Q[i] += lr * (err * pu_old - reg * qi)
        rec = {"epoch": ep + 1}
        rec["train_rmse"] = rmse(r_arr, mf_predict_pairs(mu, bu, bi, P, Q, u_arr, i_arr))
        if eval_df is not None:
            p = mf_predict_pairs(mu, bu, bi, P, Q, eval_df.u.values, eval_df.i.values)
            rec["eval_rmse"] = rmse(eval_df.rating.values, p)
        curve.append(rec)
    return (mu, bu, bi, P, Q), curve


def mf_predict_pairs(mu, bu, bi, P, Q, u, i):
    return np.clip(mu + bu[u] + bi[i] + (P[u] * Q[i]).sum(1), 0.5, 5.0)


def mf_full_matrix(model):
    mu, bu, bi, P, Q = model
    return (mu + bu[:, None] + bi[None, :] + P @ Q.T).astype(np.float32)


# ============================================================
# 6. METRIK EVALUASI
# ============================================================
def mae(y, p):  return float(np.mean(np.abs(y - p)))
def mse(y, p):  return float(np.mean((y - p) ** 2))
def rmse(y, p): return float(np.sqrt(mse(y, p)))
def nmse(y, p):  # MSE dinormalisasi dengan varians data aktual (= 1 - R^2)
    return float(np.sum((y - p) ** 2) / np.sum((y - np.mean(y)) ** 2))


def vec_metrics(y, p):
    y = np.asarray(y, dtype=np.float64)
    p = np.clip(p, 0.5, 5.0).astype(np.float64)
    return {"MAE": mae(y, p), "MSE": mse(y, p), "RMSE": rmse(y, p), "NMSE": nmse(y, p)}


def rating_metrics(P, test):
    return vec_metrics(test.rating.values, P[test.u.values, test.i.values])


def ndcg_test_items(P, test, k=10):
    """NDCG@k: urutkan item uji milik tiap user berdasar prediksi,
    bandingkan dengan urutan ideal (rating asli). gain = 2^rating - 1."""
    scores = []
    disc = 1.0 / np.log2(np.arange(2, k + 2))
    for _, g in test.groupby("u"):
        if len(g) < 2:
            continue
        y = g.rating.values
        p = P[g.u.values, g.i.values]
        top = np.argsort(-p, kind="stable")[:k]
        ideal = np.sort(y)[::-1][:k]
        dcg = ((2.0 ** y[top] - 1) * disc[:len(top)]).sum()
        idcg = ((2.0 ** ideal - 1) * disc[:len(ideal)]).sum()
        scores.append(dcg / idcg)
    return float(np.mean(scores))


def topn_metrics(P, R_train, test, min_support=20, k=10, thr=4.0):
    """Evaluasi ranking penuh: kandidat = semua item yg belum dirating user
    (dan punya >= min_support rating di train). Relevan = rating uji >= 4.
    Mengembalikan NDCG@k, Precision@k, Recall@k."""
    n_users, n_items = R_train.shape
    S = P.astype(np.float64).copy()
    S[R_train > 0] = -np.inf
    S[:, (R_train > 0).sum(0) < min_support] = -np.inf
    rel = np.zeros((n_users, n_items), dtype=bool)
    t = test[test.rating >= thr]
    rel[t.u.values, t.i.values] = True
    top = np.argpartition(-S, k, axis=1)[:, :k]
    ordr = np.argsort(-np.take_along_axis(S, top, axis=1), axis=1)
    top = np.take_along_axis(top, ordr, axis=1)
    hits = np.take_along_axis(rel, top, axis=1)
    disc = 1.0 / np.log2(np.arange(2, k + 2))
    dcg = (hits * disc).sum(1)
    n_rel = rel.sum(1)
    idcg = np.array([disc[:min(k, n)].sum() for n in n_rel])
    ok = n_rel > 0
    return {"NDCG_rank": float(np.mean(dcg[ok] / idcg[ok])),
            "Precision": float(np.mean(hits.sum(1)[ok] / k)),
            "Recall": float(np.mean(hits.sum(1)[ok] / n_rel[ok]))}


def evaluate_all(P, R_train, test):
    out = rating_metrics(P, test)
    out["NDCG@10"] = ndcg_test_items(P, test)
    out.update(topn_metrics(P, R_train, test))
    return out


# ============================================================
# 7. EKSPERIMEN UTAMA
# ============================================================
def recommend(P, R_train, user, movies, inv_iid, n=10, min_support=20):
    s = P[user].astype(np.float64).copy()
    s[R_train[user] > 0] = -np.inf
    s[(R_train > 0).sum(0) < min_support] = -np.inf
    top = np.argsort(-s)[:n]
    return [{"title": movies.set_index("movieId").loc[inv_iid[j], "title"],
             "pred": float(np.clip(P[user, j], 0.5, 5))} for j in top]


def main():
    t0 = time.time()
    ratings, movies, uid, iid = load_data()
    inv_iid = {v: k for k, v in iid.items()}
    n_users, n_items = len(uid), len(iid)
    res = {"n_users": n_users, "n_items": n_items, "n_ratings": len(ratings),
           "sparsity": 1 - len(ratings) / (n_users * n_items)}

    # --- split: 80% train / 20% test (per user); validasi 12.5% dari train
    train, test = split_per_user(ratings, 0.20)
    sub, val = split_per_user(train, 0.125, seed=SEED + 1)
    res.update(n_train=len(train), n_test=len(test), n_sub=len(sub), n_val=len(val))
    R_train = to_matrix(train, n_users, n_items)
    R_sub = to_matrix(sub, n_users, n_items)
    vpairs = (val.u.values, val.i.values)
    print(f"train={len(train)} test={len(test)} sub={len(sub)} val={len(val)}", flush=True)

    # --- 1) tuning hyperparameter pada data validasi (BUKAN pada test)
    mu, bu, bi = fit_baseline(R_sub)
    fb_sub = baseline_matrix(mu, bu, bi)
    res["val_baseline"] = rating_metrics(fb_sub, val)

    sim_sub = user_similarity(R_sub)
    ks_u = [5, 10, 20, 30, 50, 80, 120, 200, 400]
    res["sweep_user"] = {k: vec_metrics(val.rating.values, user_cf_predict(R_sub, sim_sub, k, fb_sub, vpairs))["RMSE"] for k in ks_u}
    print("sweep user", res["sweep_user"], flush=True)

    S_sub = item_similarity(R_sub)
    ks_i = [5, 10, 20, 30, 50, 80, 120, 200]
    res["sweep_item"] = {k: vec_metrics(val.rating.values, item_cf_predict(R_sub, S_sub, k, fb_sub, vpairs))["RMSE"] for k in ks_i}
    print("sweep item", res["sweep_item"], flush=True)
    del S_sub

    res["sweep_mf"] = {}
    for nf in [10, 20, 50]:
        for reg in [0.02, 0.05, 0.1]:
            model, _ = mf_sgd(sub, n_users, n_items, n_factors=nf, reg=reg, epochs=30)
            res["sweep_mf"][f"{nf}|{reg}"] = rating_metrics(mf_full_matrix(model), val)["RMSE"]
            print("sweep mf", nf, reg, res["sweep_mf"][f"{nf}|{reg}"], flush=True)

    best_ku = min(res["sweep_user"], key=res["sweep_user"].get)
    best_ki = min(res["sweep_item"], key=res["sweep_item"].get)
    best_mf = min(res["sweep_mf"], key=res["sweep_mf"].get)
    best_nf, best_reg = int(best_mf.split("|")[0]), float(best_mf.split("|")[1])
    res["best"] = {"k_user": best_ku, "k_item": best_ki, "n_factors": best_nf, "reg": best_reg}
    print("best", res["best"], flush=True)

    # --- 2) latih ulang pada seluruh data train, uji pada test
    mu, bu, bi = fit_baseline(R_train)
    fb = baseline_matrix(mu, bu, bi)
    preds, timing = {"Baseline (bias)": fb}, {}
    t = time.time()
    preds["User-based CF"] = user_cf_predict(R_train, user_similarity(R_train), best_ku, fb)
    timing["User-based CF"] = time.time() - t
    t = time.time()
    preds["Item-based CF"] = item_cf_predict(R_train, item_similarity(R_train), best_ki, fb)
    timing["Item-based CF"] = time.time() - t
    t = time.time()
    model, curve = mf_sgd(train, n_users, n_items, n_factors=best_nf, reg=best_reg,
                          epochs=30, eval_df=test)
    preds["Matrix Factorization"] = mf_full_matrix(model)
    timing["Matrix Factorization"] = time.time() - t
    res["mf_curve"], res["timing"] = curve, timing

    res["final"] = {name: evaluate_all(P, R_train, test) for name, P in preds.items()}
    # pembanding: populer & acak (tanpa prediksi rating)
    rng = np.random.default_rng(SEED)
    refs = {"Popularitas": np.tile((R_train > 0).sum(0).astype(np.float32), (n_users, 1)),
            "Acak": rng.uniform(0.5, 5, (n_users, n_items)).astype(np.float32)}
    for name, P in refs.items():
        res["final"][name] = {"NDCG@10": ndcg_test_items(P, test), **topn_metrics(P, R_train, test)}
    for name, m in res["final"].items():
        print(name, {k: round(v, 4) for k, v in m.items()}, flush=True)
    # simpan prediksi per-pasangan (untuk uji signifikansi / bootstrap di laporan)
    np.savez("test_preds.npz", y=test.rating.values,
             **{n.replace(" ", "_"): np.clip(P[test.u.values, test.i.values], .5, 5)
                for n, P in preds.items()})

    # sensitivitas NDCG ranking terhadap batas minimum jumlah rating item kandidat
    res["support_sens"] = {name: {ms: topn_metrics(P, R_train, test, min_support=ms)["NDCG_rank"]
                                  for ms in [1, 10, 20, 50, 100]}
                           for name, P in {**preds, "Popularitas": refs["Popularitas"]}.items()}
    print("support sensitivity", res["support_sens"], flush=True)

    # --- 3) contoh prediksi rating & rekomendasi top-10
    rng = np.random.default_rng(7)
    samp = test.iloc[rng.choice(len(test), 10, replace=False)]
    res["samples"] = [{"user": int(r.userId), "movie": movies.set_index("movieId").loc[r.movieId, "title"],
                       "actual": float(r.rating),
                       **{n: float(np.clip(preds[n][r.u, r.i], .5, 5)) for n in
                          ["User-based CF", "Item-based CF", "Matrix Factorization"]}}
                      for r in samp.itertuples()]
    demo_user = uid[1]
    hist = train[train.u == demo_user].sort_values("rating", ascending=False).head(8)
    res["demo_user"] = 1
    res["demo_history"] = [{"title": movies.set_index("movieId").loc[inv_iid[r.i], "title"], "rating": float(r.rating)}
                           for r in hist.itertuples()]
    res["recs"] = {n: recommend(preds[n], R_train, demo_user, movies, inv_iid)
                   for n in ["User-based CF", "Item-based CF", "Matrix Factorization"]}

    # --- 4) statistik dataset untuk grafik
    res["dist_rating"] = ratings.rating.value_counts().sort_index().to_dict()
    res["per_user"] = ratings.groupby("u").size().tolist()
    res["per_item"] = ratings.groupby("i").size().tolist()
    res["elapsed_sec"] = time.time() - t0
    json.dump(res, open("results.json", "w"), indent=1, default=float)
    print("selesai", round(res["elapsed_sec"]), "detik")


if __name__ == "__main__":
    main()
