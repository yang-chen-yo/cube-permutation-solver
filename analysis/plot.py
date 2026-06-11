# analysis/plot.py
import os
import pandas as pd
import matplotlib.pyplot as plt

COLORS = ["#4C72B0", "#DD4444", "#2CA02C", "#FF7F0E", "#9467BD", "#8C564B"]

def plot_combined(csv_path, title, out_path):
    """
    一張大圖：每個演算法一格直方圖 + 最後一格曲線比較。
    新增演算法自動多一格，不用改這裡。
    """
    if not os.path.exists(csv_path):
        print(f"找不到 {csv_path}，請先執行 run_experiments.py")
        return

    df = pd.read_csv(csv_path)
    algo_cols = [c for c in df.columns if c.endswith("_Steps")]
    n = len(algo_cols)
    total_cells = n + 1  # 各直方圖 + 1 格曲線比較

    cols = 3
    rows = (total_cells + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 5 * rows))
    axes = axes.flatten()

    # 各演算法直方圖
    for i, (col, color) in enumerate(zip(algo_cols, COLORS)):
        label = col.replace("_Steps", "").replace("_", " ")
        counts = df[col].value_counts().sort_index()
        avg = df[col].mean()
        ax = axes[i]
        ax.bar(counts.index, counts.values, color=color, edgecolor="black", alpha=0.85)
        ax.axvline(avg, color="black", linestyle="--", linewidth=1.5, label=f"Avg = {avg:.2f}")
        ax.set_title(f"{label} Histogram", fontsize=12, fontweight="bold")
        ax.set_xlabel("Number of Swaps (Steps)", fontsize=10)
        ax.set_ylabel("Number of Cases", fontsize=10)
        ax.legend(fontsize=9)
        ax.grid(axis="y", linestyle=":", alpha=0.6)

    # 最後一格：曲線比較
    ax_curve = axes[n]
    for col, color in zip(algo_cols, COLORS):
        label = col.replace("_Steps", "").replace("_", " ")
        counts = df[col].value_counts().sort_index()
        avg = df[col].mean()
        ax_curve.plot(counts.index, counts.values, marker="o", linestyle="-",
                      label=f"{label} (avg={avg:.2f})", color=color, alpha=0.85)
    ax_curve.set_title("Approximation Curves Comparison", fontsize=12, fontweight="bold")
    ax_curve.set_xlabel("Number of Swaps (Steps)", fontsize=10)
    ax_curve.set_ylabel("Number of Cases", fontsize=10)
    ax_curve.legend(fontsize=9)
    ax_curve.grid(linestyle="--", alpha=0.6)

    # 隱藏多餘的格子
    for j in range(n + 1, len(axes)):
        axes[j].set_visible(False)

    fig.suptitle(title, fontsize=15, fontweight="bold")
    plt.tight_layout()
    os.makedirs("analysis", exist_ok=True)
    fig.savefig(out_path, dpi=150)
    print(f"圖已儲存至: {out_path}")
    plt.show()


if __name__ == "__main__":
    # 3D 全排列
    plot_combined(
        csv_path="data/results_3d.csv",
        title="Hypercube Permutation Routing Comparison — 3D (40,320 Permutations)",
        out_path="analysis/chart_3d.png"
    )

    # 自動掃描所有高維度（4D、5D、...），各出一張
    if os.path.exists("data"):
        dim_keys = set()
        for fname in os.listdir("data"):
            if fname.startswith("results_") and fname.endswith(".csv") and "3d" not in fname:
                part = fname.replace("results_", "").replace(".csv", "")
                dim_key = part.split("_")[0]
                dim_keys.add(dim_key)

        for dim_key in sorted(dim_keys):
            dim = dim_key[0]

            # random 圖
            plot_combined(
                csv_path=f"data/results_{dim_key}_random.csv",
                title=f"Hypercube Permutation Routing Comparison — {dim}D (Random 40,000 Permutations)",
                out_path=f"analysis/chart_{dim_key}_random.png"
            )

            # selected 圖
            plot_combined(
                csv_path=f"data/results_{dim_key}_selected.csv",
                title=f"Hypercube Permutation Routing Comparison — {dim}D (Selected 24 Permutations)",
                out_path=f"analysis/chart_{dim_key}_selected.png"
            )