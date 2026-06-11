# experiments/compare.py
import os
import pandas as pd

def get_algo_cols(df):
    return [c for c in df.columns if c.endswith("_Steps")]

def analyze_3d():
    csv_path = "data/results_3d.csv"
    if not os.path.exists(csv_path):
        print("未找到 3D 結果，請先執行 run_experiments.py")
        return

    df = pd.read_csv(csv_path)
    algo_cols = get_algo_cols(df)

    print("\n=================== 3D 統計報告 (40,320 筆全排列) ===================")
    for col in algo_cols:
        label = col.replace("_Steps", "").replace("_", " ")
        print(f"{label:<30}: {df[col].mean():.4f}")
    print("------------------------------------------------------------------")

    print("\n[3D 步數分佈頻率表]")
    dist_df = pd.DataFrame(
        {col.replace("_Steps", ""): df[col].value_counts() for col in algo_cols}
    ).fillna(0).astype(int).sort_index()
    print(dist_df.to_markdown())

def analyze_selected(dim_key):
    csv_path = f"data/results_{dim_key}_selected.csv"
    if not os.path.exists(csv_path):
        print(f"未找到 {dim_key} 選定測資，請先執行 run_experiments.py")
        return

    dim = dim_key[0]
    df = pd.read_csv(csv_path)
    algo_cols = get_algo_cols(df)

    print(f"\n=================== {dim}D 統計報告 (選定測資) ===================")
    show_cols = ["ID"] + algo_cols
    print(df[show_cols].to_markdown(index=False))
    print("------------------------------------------------------------------")
    for col in algo_cols:
        label = col.replace("_Steps", "").replace("_", " ")
        print(f"{label:<30} {dim}D 平均步數: {df[col].mean():.2f}")

def analyze_random(dim_key):
    csv_path = f"data/results_{dim_key}_random.csv"
    if not os.path.exists(csv_path):
        print(f"未找到 {dim_key} 隨機抽樣結果，請先執行 run_experiments.py")
        return

    dim = dim_key[0]
    df = pd.read_csv(csv_path)
    algo_cols = get_algo_cols(df)
    n = len(df)

    print(f"\n=================== {dim}D 統計報告 (隨機抽樣 {n:,} 筆) ===================")
    for col in algo_cols:
        label = col.replace("_Steps", "").replace("_", " ")
        print(f"{label:<30}: mean={df[col].mean():.4f}  min={df[col].min()}  max={df[col].max()}")
    print("------------------------------------------------------------------")

if __name__ == "__main__":
    analyze_3d()

    # 自動掃描所有非 3D 維度
    if os.path.exists("data"):
        dim_keys = set()
        for fname in os.listdir("data"):
            if fname.startswith("results_") and fname.endswith(".csv") and "3d" not in fname:
                # 取出 "4d", "5d" 等
                part = fname.replace("results_", "").replace(".csv", "")
                dim_key = part.split("_")[0]
                dim_keys.add(dim_key)

        for dim_key in sorted(dim_keys):
            analyze_selected(dim_key)
            analyze_random(dim_key)