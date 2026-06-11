# analysis/plot.py
import os
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 擴充顏色庫，確保多種演算法都有對應顏色
COLORS = ["#4C72B0", "#DD4444", "#2CA02C", "#FF7F0E", "#9467BD", "#8C564B", "#E377C2"]

def plot_all(csv_path, title_prefix, out_prefix):
    """繪製總體分布：直方圖自動折行 (網格排版) + 曲線疊合圖"""
    if not os.path.exists(csv_path):
        return

    df = pd.read_csv(csv_path)
    algo_cols = [c for c in df.columns if c.endswith("_Steps")]
    if not algo_cols:
        return
        
    n = len(algo_cols)
    os.makedirs("analysis", exist_ok=True)

    # ── 圖1：各演算法直方圖 (2欄網格排列) ──
    cols = 2 if n > 1 else 1
    rows = math.ceil(n / cols)
    
    fig1, axes = plt.subplots(rows, cols, figsize=(7 * cols, 5 * rows))
    axes = axes.flatten() if n > 1 else [axes]

    for i, (col, color) in enumerate(zip(algo_cols, COLORS)):
        label = col.replace("_Steps", "").replace("_", " ")
        counts = df[col].value_counts().sort_index()
        avg = df[col].mean()
        
        ax = axes[i]
        ax.bar(counts.index, counts.values, color=color, edgecolor="black", alpha=0.85)
        ax.axvline(avg, color="black", linestyle="--", linewidth=1.5)
        
        # 精簡文字：將平均值整合進標題，不使用 legend
        ax.set_title(f"{label} (Avg: {avg:.1f})", fontsize=14, fontweight="bold")
        ax.set_xlabel("Steps", fontsize=11)
        ax.set_ylabel("Count", fontsize=11)
        ax.grid(axis="y", linestyle=":", alpha=0.6)

    # 隱藏多餘的空白格子
    for j in range(n, len(axes)):
        axes[j].set_visible(False)

    fig1.suptitle(f"{title_prefix} — Histograms", fontsize=16, fontweight="bold")
    plt.tight_layout()
    out1 = f"analysis/{out_prefix}_histograms.png"
    fig1.savefig(out1, dpi=150)
    plt.close(fig1)

    # ── 圖2：比較曲線疊合圖 ──
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    for col, color in zip(algo_cols, COLORS):
        label = col.replace("_Steps", "").replace("_", " ")
        counts = df[col].value_counts().sort_index()
        ax2.plot(counts.index, counts.values, marker="o", linestyle="-",
                 label=f"{label} (Avg: {df[col].mean():.1f})", color=color, alpha=0.85)

    ax2.set_title(f"{title_prefix} — Curves Comparison", fontsize=15, fontweight="bold")
    ax2.set_xlabel("Steps", fontsize=12)
    ax2.set_ylabel("Count", fontsize=12)
    ax2.legend(fontsize=11)
    ax2.grid(linestyle="--", alpha=0.6)
    
    plt.tight_layout()
    out2 = f"analysis/{out_prefix}_comparison.png"
    fig2.savefig(out2, dpi=150)
    plt.close(fig2)
    print(f"[{out_prefix}] 直方圖與曲線圖已生成！")


def plot_selected_cases_bar(csv_path, title_prefix, out_prefix):
    """專為『選定測資』設計：群組長條圖 (Grouped Bar Chart)"""
    if not os.path.exists(csv_path):
        return

    df = pd.read_csv(csv_path)
    if "ID" not in df.columns:
        return

    algo_cols = [c for c in df.columns if c.endswith("_Steps")]
    n_algos = len(algo_cols)

    fig, ax = plt.subplots(figsize=(14, 6))
    x = np.arange(len(df["ID"]))
    width = 0.8 / n_algos

    for i, (col, color) in enumerate(zip(algo_cols, COLORS)):
        label = col.replace("_Steps", "").replace("_", " ")
        offset = x + (i - n_algos / 2 + 0.5) * width
        ax.bar(offset, df[col], width, label=label, color=color, alpha=0.85)

    ax.set_title(f"{title_prefix} — Individual Testcase Comparison (Bar)", fontsize=16, fontweight="bold")
    ax.set_xlabel("Testcase ID", fontsize=12)
    ax.set_ylabel("Routing Steps", fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(df["ID"])
    ax.legend(fontsize=11)
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    
    plt.tight_layout()
    out_path = f"analysis/{out_prefix}_cases_bar.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"[{out_prefix}] 測資專屬並排長條圖已生成！")


def plot_selected_cases_line(csv_path, title_prefix, out_prefix):
    """專為『選定測資』設計：折線圖 (Line Chart)，更容易觀察趨勢"""
    if not os.path.exists(csv_path):
        return

    df = pd.read_csv(csv_path)
    if "ID" not in df.columns:
        return

    algo_cols = [c for c in df.columns if c.endswith("_Steps")]

    fig, ax = plt.subplots(figsize=(14, 6))
    x = np.arange(len(df["ID"]))

    for i, (col, color) in enumerate(zip(algo_cols, COLORS)):
        label = col.replace("_Steps", "").replace("_", " ")
        ax.plot(x, df[col], marker='o', linewidth=2.5, markersize=6, 
                label=label, color=color, alpha=0.85)

    ax.set_title(f"{title_prefix} — Individual Testcase Comparison (Line)", fontsize=16, fontweight="bold")
    ax.set_xlabel("Testcase ID", fontsize=12)
    ax.set_ylabel("Routing Steps", fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(df["ID"])
    ax.legend(fontsize=11)
    ax.grid(axis="both", linestyle="--", alpha=0.5)
    
    plt.tight_layout()
    out_path = f"analysis/{out_prefix}_cases_line.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"[{out_prefix}] 測資專屬折線圖已生成！")


if __name__ == "__main__":
    print("開始繪製分析圖表...")
    
    # 1. 畫 3D 全排列
    plot_all("data/results_3d.csv", "3D Hypercube (40,320 Permutations)", "3d")

    # 2. 自動掃描並畫高維度資料
    if os.path.exists("data"):
        for fname in sorted(os.listdir("data")):
            # 處理隨機抽樣檔案
            if fname.startswith("results_") and fname.endswith("_random.csv"):
                dim_key = fname.replace("results_", "").replace("_random.csv", "")
                dim = dim_key[0]
                plot_all(f"data/{fname}", f"{dim}D Hypercube (Random 40,000)", f"{dim_key}_random")
            
            # 處理選定測資檔案
            elif fname.startswith("results_") and fname.endswith("_selected.csv"):
                dim_key = fname.replace("results_", "").replace("_selected.csv", "")
                dim = dim_key[0]
                # 畫出總體分布 (直方圖 + 比較曲線)
                plot_all(f"data/{fname}", f"{dim}D Hypercube (Selected 24 Cases)", f"{dim_key}_selected")
                
                # 畫出專屬測資的比較圖 (長條圖 + 折線圖)
                plot_selected_cases_bar(f"data/{fname}", f"{dim}D Hypercube", f"{dim_key}_selected")
                plot_selected_cases_line(f"data/{fname}", f"{dim}D Hypercube", f"{dim_key}_selected")
                
    print("\n🎉 所有圖表已繪製完畢，請至 analysis/ 目錄查看！")