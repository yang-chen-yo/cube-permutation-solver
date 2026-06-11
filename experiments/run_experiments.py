# analysis/plot.py
import os
import pandas as pd
import matplotlib.pyplot as plt

COLORS = ["#4C72B0", "#DD4444", "#2CA02C", "#FF7F0E", "#9467BD", "#8C564B"]

def plot_all(csv_path, title_prefix, out_prefix):
    """直方圖 + 曲線比較圖，動態讀欄位，新增演算法自動出現。"""
    if not os.path.exists(csv_path):
        print(f"找不到 {csv_path}，請先執行 run_experiments.py")
        return

    df = pd.read_csv(csv_path)
    algo_cols = [c for c in df.columns if c.endswith("_Steps")]
    n = len(algo_cols)
    os.makedirs("analysis", exist_ok=True)

    # ── 圖1：各演算法直方圖並排 ──
    fig1, axes = plt.subplots(1, n, figsize=(6 * n, 5))
    if n == 1:
        axes = [axes]

    for ax, col, color in zip(axes, algo_cols, COLORS):
        label = col.replace("_Steps", "").replace("_", " ")
        counts = df[col].value_counts().sort_index()
        avg = df[col].mean()
        ax.bar(counts.index, counts.values, color=color, edgecolor="black", alpha=0.85)
        ax.axvline(avg, color="black", linestyle="--", linewidth=1.5, label=f"Avg = {avg:.2f}")
        ax.set_title(label, fontsize=13, fontweight="bold")
        ax.set_xlabel("Number of Swaps (Steps)", fontsize=11)
        ax.set_ylabel("Number of Cases", fontsize=11)
        ax.legend(fontsize=10)
        ax.grid(axis="y", linestyle=":", alpha=0.6)

    fig1.suptitle(f"{title_prefix} — Individual Histograms", fontsize=14, fontweight="bold")
    plt.tight_layout()
    out1 = f"analysis/{out_prefix}_histograms.png"
    fig1.savefig(out1, dpi=150)
    print(f"直方圖已儲存至: {out1}")
    plt.show()

    # ── 圖2：所有演算法曲線疊在一起比較 ──
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    for col, color in zip(algo_cols, COLORS):
        label = col.replace("_Steps", "").replace("_", " ")
        counts = df[col].value_counts().sort_index()
        avg = df[col].mean()
        ax2.plot(counts.index, counts.values, marker="o", linestyle="-",
                 label=f"{label} (avg={avg:.2f})", color=color, alpha=0.85)

    ax2.set_title(f"{title_prefix} — Curves Comparison", fontsize=14, fontweight="bold")
    ax2.set_xlabel("Number of Swaps (Steps)", fontsize=12)
    ax2.set_ylabel("Number of Cases", fontsize=12)
    ax2.legend(fontsize=11)
    ax2.grid(linestyle="--", alpha=0.6)
    plt.tight_layout()
    out2 = f"analysis/{out_prefix}_comparison.png"
    fig2.savefig(out2, dpi=150)
    print(f"曲線比較圖已儲存至: {out2}")
    plt.show()


if __name__ == "__main__":
    # 3D 全排列
    plot_all(
        csv_path="data/results_3d.csv",
        title_prefix="3D Hypercube (40,320 Permutations)",
        out_prefix="3d"
    )

    # 自動掃描所有 *_random.csv（4D、5D、...），selected 不畫圖
    if os.path.exists("data"):
        for fname in sorted(os.listdir("data")):
            if fname.startswith("results_") and fname.endswith("_random.csv"):
                dim_key = fname.replace("results_", "").replace("_random.csv", "")
                dim = dim_key[0]
                plot_all(
                    csv_path=f"data/{fname}",
                    title_prefix=f"{dim}D Hypercube (Random 40,000 Permutations)",
                    out_prefix=f"{dim_key}_random"
                )