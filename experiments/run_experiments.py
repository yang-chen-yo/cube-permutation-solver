# experiments/run_experiments.py
import itertools
import random
import sys
import os
import pandas as pd

# 確保可以讀取到根目錄的模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import Cube
from algorithms.bfs import BFSRouter
from algorithms.batcher import BatcherRouter
from algorithms.bitonic import BitonicRouter


# =============================================
# Batcher 比較器計算（僅計算網路中的比較器數量，非路由步數）
# =============================================
def batcher_sort_count(initial_state):
    n = len(initial_state)
    dim = n.bit_length() - 1
    state = list(initial_state)
    swaps = 0
    for i in range(1, dim + 1):
        for j in range(i - 1, -1, -1):
            dist = 1 << j
            for u in range(n):
                if (u & dist) == 0:
                    v = u + dist
                    dir_asc = ((u >> i) & 1) == 0
                    if dir_asc:
                        if state[u] > state[v]:
                            state[u], state[v] = state[v], state[u]
                            swaps += 1
                    else:
                        if state[u] < state[v]:
                            state[u], state[v] = state[v], state[u]
                            swaps += 1
    return swaps


# =============================================
# 額外演算法註冊區
# 在這裡掛載 Batcher 的循序與平行版本
# =============================================
def build_extra_routers(cube):
    # 建立組員的 Odd-Even (基準組)
    odd_even_seq = BatcherRouter(cube, use_parallel=False)
    odd_even_par = BatcherRouter(cube, use_parallel=True)
    
    # 建立你的 Bitonic (優化組)
    bitonic_seq = BitonicRouter(cube, use_parallel=False)
    
    return [
        {"name": "OddEven_Sequential", "fn": lambda state: len(odd_even_seq.route(state))},
        {"name": "OddEven_Parallel", "fn": lambda state: len(odd_even_par.route(state))},
        {"name": "Bitonic_Sequential", "fn": lambda state: len(bitonic_seq.route(state))},
    ]

# =============================================
# 選定測資區
# =============================================
SELECTED_TESTCASES = {
    "4d": [
        [15,0,10,4,3,11,1,7,8,5,6,2,12,9,14,13],
        [0,8,1,12,2,5,9,14,4,6,10,7,3,11,13,15],
        [1,5,0,8,9,11,2,15,3,12,4,6,10,14,13,7],
        [1,9,0,4,10,8,2,11,3,15,5,12,7,14,13,6],
        [3,1,7,13,11,0,8,15,2,5,10,6,9,14,12,4],
        [3,1,11,7,8,0,9,5,2,6,15,13,14,4,10,12],
        [3,5,11,1,8,0,9,7,2,6,14,13,10,4,12,15],
        [0,1,2,3,4,5,6,8,7,9,10,11,12,13,14,15],
        [6,2,14,13,3,11,10,7,0,5,8,1,15,12,4,9],
        [6,4,11,0,9,8,12,2,15,5,3,7,10,13,14,1],
        [13,1,14,0,9,2,15,6,12,8,11,3,4,5,7,10],
        [0,2,3,5,7,11,13,1,4,6,8,9,10,12,14,15],
        [8,14,0,3,2,5,10,7,4,9,12,11,1,13,6,15],
        [7,14,9,6,11,0,13,2,5,15,10,12,1,4,3,8],
        [1,2,4,8,0,3,5,6,7,9,10,11,12,13,14,15],
        [0,1,14,3,4,5,7,8,15,13,10,6,9,12,11,2],
        [2,5,3,15,4,13,6,7,8,9,10,11,12,1,14,0],
        [0,1,2,3,4,5,14,11,8,6,10,9,12,15,13,7],
        [1,2,3,4,5,6,7,8,9,0,10,11,12,13,14,15],
        [1,1,3,9,2,7,13,15,14,8,1,4,10,0,12,6],
        [5,0,12,15,7,1,5,2,4,10,13,3,11,8,14,9],
        [9,0,2,15,11,6,7,8,14,3,4,13,5,1,12,10],
        [6,15,9,5,13,12,3,7,2,10,1,11,0,14,4,8],
        [1,1,3,9,2,7,13,15,14,8,1,4,10,0,12,6,5],
    ],
}

# 各維度隨機抽樣數量設定
RANDOM_SAMPLE_SIZE = {
    "4d": 40000,
}


def clean_permutations(raw_data, n):
    cleaned = []
    for p in raw_data:
        truncated = p[:n]
        missing = list(set(range(n)) - set(truncated))
        seen = set()
        final_p = []
        for x in truncated:
            if x not in seen and 0 <= x < n:
                seen.add(x)
                final_p.append(x)
            else:
                if missing:
                    fill = missing.pop(0)
                    seen.add(fill)
                    final_p.append(fill)
        while len(final_p) < n:
            if missing:
                final_p.append(missing.pop(0))
        cleaned.append(tuple(final_p))
    return cleaned


# =============================================
# 3D：全排列實驗
# =============================================
def run_3d():
    print("正在初始化 3D 超立方體...")
    cube = Cube(dim=3)
    
    # 同時建立 BFS 循序與平行版本
    bfs_seq = BFSRouter(cube, use_matchings=False)
    bfs_par = BFSRouter(cube, use_matchings=True)
    extra_routers = build_extra_routers(cube)

    print("正在計算 BFS 全狀態地圖 (Sequential & Parallel Ground Truth)...")
    dist_seq = bfs_seq.all_distances()
    dist_par = bfs_par.all_distances()

    print("開始跑 40320 筆排列實驗...")
    all_perms = list(itertools.permutations(range(cube.N)))
    results = []

    for idx, perm in enumerate(all_perms):
        state = tuple(perm)
        row = {
            "permutation": str(list(state)),
            "BFS_Sequential_Steps": dist_seq[state],
            "BFS_Parallel_Steps": dist_par[state],
            # 將原本純計算的函式改名，避免被 plot.py 當成路由步數畫出來
            "Batcher_Comparators_Only": batcher_sort_count(state),
        }
        for r in extra_routers:
            row[f"{r['name']}_Steps"] = r["fn"](state)
        results.append(row)

        if (idx + 1) % 5000 == 0:
            print(f"  已完成 {idx + 1} / 40320 筆...")

    os.makedirs("data", exist_ok=True)
    pd.DataFrame(results).to_csv("data/results_3d.csv", index=False)
    print("3D 實驗完成！結果已儲存至 data/results_3d.csv")


# =============================================
# 高維度：選定測資 + 隨機抽樣
# =============================================
def run_selected():
    for dim_key, raw_data in SELECTED_TESTCASES.items():
        dim = int(dim_key[0])
        n   = 1 << dim
        print(f"\n正在初始化 {dim}D 超立方體...")
        cube = Cube(dim=dim)
        extra_routers = build_extra_routers(cube)

        # --- 選定測資 ---
        selected = clean_permutations(raw_data, n)
        selected_results = []
        print(f"開始測試 {len(selected)} 筆選定的 {dim}D 排列...")
        for idx, state in enumerate(selected):
            row = {
                "ID": idx + 1,
                "Permutation": str(list(state)),
                "Batcher_Comparators_Only": batcher_sort_count(state),
            }
            for r in extra_routers:
                row[f"{r['name']}_Steps"] = r["fn"](state)
            selected_results.append(row)

        os.makedirs("data", exist_ok=True)
        sel_path = f"data/results_{dim_key}_selected.csv"
        pd.DataFrame(selected_results).to_csv(sel_path, index=False)
        print(f"選定測資完成！結果已儲存至 {sel_path}")

        # --- 隨機抽樣 ---
        sample_size = RANDOM_SAMPLE_SIZE.get(dim_key, 40000)
        print(f"開始隨機抽樣 {sample_size} 筆 {dim}D 排列...")
        random.seed(42)
        sample_results = []
        for idx in range(sample_size):
            state = tuple(random.sample(range(n), n))
            row = {
                "ID": idx + 1,
                "Permutation": str(list(state)),
                "Batcher_Comparators_Only": batcher_sort_count(state),
            }
            for r in extra_routers:
                row[f"{r['name']}_Steps"] = r["fn"](state)
            sample_results.append(row)

            if (idx + 1) % 10000 == 0:
                print(f"  已完成 {idx + 1} / {sample_size} 筆...")

        rnd_path = f"data/results_{dim_key}_random.csv"
        pd.DataFrame(sample_results).to_csv(rnd_path, index=False)
        print(f"隨機抽樣完成！結果已儲存至 {rnd_path}")


def main():
    run_3d()
    run_selected()


if __name__ == "__main__":
    main()