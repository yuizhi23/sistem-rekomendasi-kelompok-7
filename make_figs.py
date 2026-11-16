import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

r = json.load(open("results.json"))
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.grid": True, "grid.alpha": .25,
                     "mathtext.fontset": "dejavusans"})
COL = {"Baseline (bias)": "#8d99ae", "User-based CF": "#d1495b", "Item-based CF": "#00798c",
       "Matrix Factorization": "#edae49", "Popularitas": "#66a182", "Acak": "#bbbbbb"}
SHORT = {"Baseline (bias)": "Baseline", "User-based CF": "User-based\nCF", "Item-based CF": "Item-based\nCF",
         "Matrix Factorization": "Matrix\nFactorization", "Popularitas": "Popularitas", "Acak": "Acak"}

AB = {"Baseline (bias)":"Baseline","User-based CF":"UB-CF","Item-based CF":"IB-CF","Matrix Factorization":"MF","Popularitas":"Popular","Acak":"Acak"}
# ---------- Gambar 1: statistik dataset ----------
fig, ax = plt.subplots(1, 3, figsize=(9.6, 2.9))
d = r["dist_rating"]
ax[0].bar([float(k) for k in d], list(d.values()), width=.4, color="#00798c")
ax[0].set_title("Distribusi nilai rating"); ax[0].set_xlabel("rating"); ax[0].set_ylabel("jumlah")
ax[1].hist(r["per_user"], bins=np.logspace(1, 3.4, 30), color="#d1495b")
ax[1].set_xscale("log"); ax[1].set_title("Rating per user"); ax[1].set_xlabel("jumlah rating (log)")
ax[1].set_ylabel("jumlah user")
ax[2].hist(r["per_item"], bins=np.logspace(0, 2.6, 30), color="#edae49")
ax[2].set_xscale("log"); ax[2].set_yscale("log"); ax[2].set_title("Rating per film (long tail)")
ax[2].set_xlabel("jumlah rating (log)"); ax[2].set_ylabel("jumlah film (log)")
plt.tight_layout(); plt.savefig("figs/f1_dataset.png", dpi=200); plt.close()

# ---------- Gambar 2: tuning hyperparameter ----------
fig, ax = plt.subplots(1, 3, figsize=(9.6, 3.0), gridspec_kw={"width_ratios": [1, 1, 1.05]})
base = r["val_baseline"]["RMSE"]
for a, key, name, c in [(ax[0], "sweep_user", "User-based CF", COL["User-based CF"]),
                        (ax[1], "sweep_item", "Item-based CF", COL["Item-based CF"])]:
    ks = [int(k) for k in r[key]]; v = list(r[key].values())
    a.plot(ks, v, "o-", color=c, lw=2); a.axhline(base, color="#8d99ae", ls="--", lw=1.2, label="Baseline")
    kb = ks[int(np.argmin(v))]; a.scatter([kb], [min(v)], s=110, facecolor="none", edgecolor="k", zorder=5)
    a.annotate(f"k={kb}\nRMSE={min(v):.4f}", (kb, min(v)), textcoords="offset points", xytext=(-20, 22), fontsize=8)
    a.set_xscale("log"); a.set_xlabel("k (jumlah tetangga)"); a.set_ylabel("RMSE validasi")
    a.set_title(name); a.legend(frameon=False, fontsize=8)
nfs = sorted({int(k.split("|")[0]) for k in r["sweep_mf"]}); regs = sorted({float(k.split("|")[1]) for k in r["sweep_mf"]})
H = np.array([[r["sweep_mf"][f"{nf}|{rg}"] for rg in regs] for nf in nfs])
im = ax[2].imshow(H, cmap="YlGnBu_r", aspect="auto")
ax[2].set_xticks(range(len(regs))); ax[2].set_xticklabels(regs); ax[2].set_yticks(range(len(nfs))); ax[2].set_yticklabels(nfs)
ax[2].set_xlabel("regularisasi $\\lambda$"); ax[2].set_ylabel("jumlah faktor"); ax[2].set_title("Matrix Factorization"); ax[2].grid(False)
for i in range(len(nfs)):
    for j in range(len(regs)):
        ax[2].text(j, i, f"{H[i, j]:.4f}", ha="center", va="center", fontsize=8,
                   color="white" if H[i, j] < H.mean() else "black", fontweight="bold" if H[i, j] == H.min() else "normal")
plt.tight_layout(); plt.savefig("figs/f2_tuning.png", dpi=200); plt.close()

# ---------- Gambar 3: konvergensi MF ----------
cv = r["mf_curve"]
fig, ax = plt.subplots(figsize=(5.2, 3.0))
ax.plot([c["epoch"] for c in cv], [c["train_rmse"] for c in cv], "-", color="#edae49", lw=2, label="RMSE train")
ax.plot([c["epoch"] for c in cv], [c["eval_rmse"] for c in cv], "-", color="#00798c", lw=2, label="RMSE test")
ax.axhline(r["final"]["Baseline (bias)"]["RMSE"], color="#8d99ae", ls="--", label="RMSE baseline (test)")
ax.set_xlabel("epoch"); ax.set_ylabel("RMSE"); ax.set_title("Konvergensi Matrix Factorization (SGD)")
ax.legend(frameon=False); plt.tight_layout(); plt.savefig("figs/f3_mf_curve.png", dpi=200); plt.close()

# ---------- Gambar 4: perbandingan metrik ----------
meth = ["Baseline (bias)", "User-based CF", "Item-based CF", "Matrix Factorization"]
fig, ax = plt.subplots(1, 3, figsize=(9.6, 3.1))
for a, met, ttl in [(ax[0], "MAE", "MAE (lebih kecil lebih baik)"), (ax[1], "RMSE", "RMSE (lebih kecil lebih baik)")]:
    vals = [r["final"][m][met] for m in meth]
    b = a.bar(range(4), vals, color=[COL[m] for m in meth])
    a.set_xticks(range(4)); a.set_xticklabels([SHORT[m] for m in meth], fontsize=7.5)
    a.set_ylim(min(vals) - .04, max(vals) + .02); a.set_title(ttl)
    for x, v in zip(range(4), vals): a.text(x, v + .002, f"{v:.4f}", ha="center", fontsize=8)
meth2 = meth + ["Popularitas", "Acak"]
vals = [r["final"][m]["NDCG@10"] for m in meth2]
ax[2].bar(range(6), vals, color=[COL[m] for m in meth2])
ax[2].set_xticks(range(6)); ax[2].set_xticklabels([AB[m] for m in meth2], fontsize=7.5)
ax[2].set_ylim(.65, .84); ax[2].set_title("NDCG@10 (lebih besar lebih baik)")
for x, v in zip(range(6), vals): ax[2].text(x, v + .003, f"{v:.3f}", ha="center", fontsize=7.5)
plt.tight_layout(); plt.savefig("figs/f4_compare.png", dpi=200); plt.close()

# ---------- Gambar 5: NDCG ranking penuh vs min_support ----------
fig, ax = plt.subplots(1, 2, figsize=(9.2, 3.1))
for m in meth + ["Popularitas"]:
    ms = [int(k) for k in r["support_sens"][m]]
    ax[0].plot(range(len(ms)), list(r["support_sens"][m].values()), "o-", color=COL[m], lw=2, label=SHORT[m].replace("\n", " "))
ax[0].set_xticks(range(len(ms))); ax[0].set_xticklabels(ms)
ax[0].set_xlabel("minimum jumlah rating item kandidat (data train)"); ax[0].set_ylabel("NDCG@10 (ranking penuh)")
ax[0].set_title("Pengaruh filter dukungan item"); ax[0].legend(frameon=False, fontsize=7.5)
m2 = meth + ["Popularitas", "Acak"]
vals = [r["final"][m]["NDCG_rank"] for m in m2]
ax[1].bar(range(6), vals, color=[COL[m] for m in m2])
ax[1].set_xticks(range(6)); ax[1].set_xticklabels([AB[m] for m in m2], fontsize=7.5)
ax[1].set_title("NDCG@10 ranking penuh (filter dukungan = 20)")
for x, v in zip(range(6), vals): ax[1].text(x, v + .002, f"{v:.3f}", ha="center", fontsize=8)
plt.tight_layout(); plt.savefig("figs/f5_topn.png", dpi=200); plt.close()


# ---------- Gambar rumus (mathtext) ----------
def formula(name, lines, fs=13, w=7.2):
    h = 0.52 * len(lines) + .1
    fig = plt.figure(figsize=(w, h))
    for n, ln in enumerate(lines):
        fig.text(0.5, 1 - (n + .55) / len(lines), ln, ha="center", va="center", fontsize=fs)
    plt.savefig(f"figs/{name}.png", dpi=220, transparent=False, bbox_inches="tight", pad_inches=0.05, facecolor="white")
    plt.close()


formula("m_base", [r"$\hat{r}_{ui}=\mu+b_u+b_i$"])
formula("m_ub_sim", [
    r"$\mathrm{sim}(u,v)=\frac{\sum_{i\in I_{uv}}(r_{ui}-\mu_u^{uv})(r_{vi}-\mu_v^{uv})}"
    r"{\sqrt{\sum_{i\in I_{uv}}(r_{ui}-\mu_u^{uv})^2}\;\sqrt{\sum_{i\in I_{uv}}(r_{vi}-\mu_v^{uv})^2}}$",
    r"$\mathrm{sim}'(u,v)=\frac{|I_{uv}|}{|I_{uv}|+\beta}\;\mathrm{sim}(u,v),\quad \beta=10$"], fs=12.5)
formula("m_ub_pred", [
    r"$\hat{r}_{ui}=\bar{r}_u+\frac{\sum_{v\in N_k(u,i)}\mathrm{sim}'(u,v)\,(r_{vi}-\bar{r}_v)}"
    r"{\sum_{v\in N_k(u,i)}|\mathrm{sim}'(u,v)|}$"], fs=13)
formula("m_ib_sim", [
    r"$\mathrm{sim}(i,j)=\frac{\sum_{u\in U_{ij}}(r_{ui}-\bar{r}_u)(r_{uj}-\bar{r}_u)}"
    r"{\sqrt{\sum_{u\in U_i}(r_{ui}-\bar{r}_u)^2}\;\sqrt{\sum_{u\in U_j}(r_{uj}-\bar{r}_u)^2}}$",
    r"$\mathrm{sim}'(i,j)=\frac{|U_{ij}|}{|U_{ij}|+\beta}\;\mathrm{sim}(i,j),\quad \beta=10$"], fs=12.5)
formula("m_ib_pred", [
    r"$\hat{r}_{ui}=\bar{r}_i+\frac{\sum_{j\in N_k(i,u)}\mathrm{sim}'(i,j)\,(r_{uj}-\bar{r}_j)}"
    r"{\sum_{j\in N_k(i,u)}|\mathrm{sim}'(i,j)|}$"], fs=13)
formula("m_mf", [
    r"$\hat{r}_{ui}=\mu+b_u+b_i+\mathbf{p}_u^{\top}\mathbf{q}_i$",
    r"$\min\;\sum_{(u,i)\in\mathcal{K}}\left(r_{ui}-\hat{r}_{ui}\right)^2+\lambda\left(b_u^2+b_i^2+\|\mathbf{p}_u\|^2+\|\mathbf{q}_i\|^2\right)$"], fs=12.5)
formula("m_sgd", [
    r"$e_{ui}=r_{ui}-\hat{r}_{ui}$",
    r"$b_u\leftarrow b_u+\gamma\,(e_{ui}-\lambda b_u)\qquad b_i\leftarrow b_i+\gamma\,(e_{ui}-\lambda b_i)$",
    r"$\mathbf{p}_u\leftarrow \mathbf{p}_u+\gamma\,(e_{ui}\,\mathbf{q}_i-\lambda\,\mathbf{p}_u)\qquad "
    r"\mathbf{q}_i\leftarrow \mathbf{q}_i+\gamma\,(e_{ui}\,\mathbf{p}_u-\lambda\,\mathbf{q}_i)$"], fs=12.5)
formula("m_err", [
    r"$\mathrm{MAE}=\frac{1}{n}\sum_{k=1}^{n}|r_k-\hat{r}_k|\qquad\qquad "
    r"\mathrm{MSE}=\frac{1}{n}\sum_{k=1}^{n}(r_k-\hat{r}_k)^2$",
    r"$\mathrm{RMSE}=\sqrt{\mathrm{MSE}}\qquad\qquad "
    r"\mathrm{NMSE}=\frac{\sum_{k=1}^{n}(r_k-\hat{r}_k)^2}{\sum_{k=1}^{n}(r_k-\bar{r})^2}$"], fs=13)
formula("m_ndcg", [
    r"$\mathrm{DCG@}K=\sum_{p=1}^{K}\frac{2^{rel_p}-1}{\log_2(p+1)}\qquad\qquad "
    r"\mathrm{NDCG@}K=\frac{\mathrm{DCG@}K}{\mathrm{IDCG@}K}$"], fs=13)
print("figures ok")
