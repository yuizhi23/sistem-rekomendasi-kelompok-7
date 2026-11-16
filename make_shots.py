import ast
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import ImageFormatter

src = open("recsys.py").read()
lines = src.split("\n")
tree = ast.parse(src)
fn = {n.name: (n.lineno, n.end_lineno) for n in tree.body if isinstance(n, ast.FunctionDef)}

def shot(name, funcs, out):
    # gabungkan beberapa fungsi, nomor baris asli dipertahankan lewat line_number_start
    start = min(fn[f][0] for f in funcs)
    chunks = []
    for f in funcs:
        a, b = fn[f]
        chunks.append("\n".join(lines[a-1:b]))
    code = "\n\n".join(chunks)
    try:
        fmt = ImageFormatter(font_name="DejaVu Sans Mono", font_size=15, style="friendly",
                             line_numbers=True, line_number_start=start,
                             image_pad=14, line_pad=3, line_number_bg="#eeeeee", line_number_fg="#888888")
    except Exception:
        fmt = ImageFormatter(font_name="Menlo", font_size=15, style="friendly",
                             line_numbers=True, line_number_start=start,
                             image_pad=14, line_pad=3, line_number_bg="#eeeeee", line_number_fg="#888888")
    with open(out, "wb") as f:
        f.write(highlight(code, PythonLexer(), fmt))

shots = {
 "s_data":   ["load_data", "split_per_user", "to_matrix"],
 "s_base":   ["fit_baseline", "baseline_matrix"],
 "s_ub_sim": ["user_similarity"],
 "s_ub_pred":["user_cf_predict"],
 "s_ib_sim": ["item_similarity"],
 "s_ib_pred":["item_cf_predict"],
 "s_mf_train":["mf_sgd"],
 "s_mf_pred":["mf_predict_pairs", "mf_full_matrix"],
 "s_metrics":["mae", "mse", "rmse", "nmse", "vec_metrics", "rating_metrics"],
 "s_ndcg":   ["ndcg_test_items"],
 "s_topn":   ["topn_metrics", "evaluate_all"],
 "s_recs":   ["recommend"],
}
for k, v in shots.items():
    shot(k, v, f"figs/{k}.png")
print("ok")
