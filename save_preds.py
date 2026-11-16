# Menyimpan prediksi per-pasangan data uji memakai hyperparameter terbaik dari results.json
import json, numpy as np
from recsys import *
r = json.load(open("results.json")); b = r["best"]
ratings, movies, uid, iid = load_data()
nu, ni = len(uid), len(iid)
train, test = split_per_user(ratings, 0.20)
R = to_matrix(train, nu, ni)
mu, bu, bi = fit_baseline(R); fb = baseline_matrix(mu, bu, bi)
P = {"Baseline (bias)": fb,
     "User-based CF": user_cf_predict(R, user_similarity(R), int(b["k_user"]), fb),
     "Item-based CF": item_cf_predict(R, item_similarity(R), int(b["k_item"]), fb)}
model, _ = mf_sgd(train, nu, ni, n_factors=b["n_factors"], reg=b["reg"], epochs=30)
P["Matrix Factorization"] = mf_full_matrix(model)
np.savez("test_preds.npz", y=test.rating.values,
         **{n.replace(" ", "_"): np.clip(M[test.u.values, test.i.values], .5, 5) for n, M in P.items()})
for n, M in P.items():
    print(n, {k: round(v, 4) for k, v in rating_metrics(M, test).items()}, "| tersimpan:", r["final"][n]["RMSE"])
