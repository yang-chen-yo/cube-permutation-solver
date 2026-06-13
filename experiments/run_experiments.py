# experiments/run_experiments.py
import itertools
import random
import sys
import os
import pandas as pd
import time

# 確保可以讀取到根目錄的模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import Cube
from algorithms.bfs import BFSRouter
from algorithms.batcher import BatcherRouter
from algorithms.bitonic import BitonicRouter
from algorithms.greedy import GreedyMatchingRouter

execution_table = {}

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

    greedy = GreedyMatchingRouter(cube)       
    
    return [
        {"name": "Batcher Merge sort", "fn": lambda state: len(odd_even_seq.route(state))},
        {"name": "Advanced Batcher Merge sort", "fn": lambda state: len(odd_even_par.route(state))},
        {"name": "Bitonic", "fn": lambda state: len(bitonic_seq.route(state))},
        # {"name": "Greedy_Beam_Search", "fn": lambda state: len(greedy.route(state))}, 
    ]

# =============================================
# 選定測資區
# =============================================
from testcases import SELECTED_TESTCASES

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

    algo_time = {
        r["name"]: 0.0
        for r in extra_routers
    }

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
            # row[f"{r['name']}_Steps"] = r["fn"](state)
            
            start = time.perf_counter()

            steps = r["fn"](state)

            elapsed = time.perf_counter() - start
            algo_time[r["name"]] += elapsed

            row[f"{r['name']}_Steps"] = steps
            row[f"{r['name']}_Time_ms"] = elapsed * 1000
        results.append(row)

        
        if (idx + 1) % 5000 == 0:
            print(f"  已完成 {idx + 1} / 40320 筆...")

    os.makedirs("data", exist_ok=True)
    pd.DataFrame(results).to_csv("data/results_3d.csv", index=False)
    print("3D 實驗完成！結果已儲存至 data/results_3d.csv")

    print("\n=== 3D Runtime ===")
    for name, t in algo_time.items():
        print(f"{name}: {t:.4f} sec")

        if name not in execution_table:
            execution_table[name] = {}

        execution_table[name]["Q3"] = round(t, 4)


# =============================================
# 高維度：選定測資 + 隨機抽樣
# =============================================
def run_selected():
    
    for dim_key, raw_data in SELECTED_TESTCASES.items():
        dim = int(dim_key[:-1])
        n   = 1 << dim
        print(f"\n正在初始化 {dim}D 超立方體...")
        cube = Cube(dim=dim)
        extra_routers = build_extra_routers(cube)
        algo_time = {
            r["name"]: 0.0
            for r in extra_routers
        }
        
        # --- 選定測資 ---
        selected = clean_permutations(raw_data, n)
        selected_results = []
        print(f"開始測試 {len(selected)} 筆選定的 {dim}D 排列...")
        for idx, state in enumerate(selected):
            row = {
                "ID": idx + 1,
                #"Permutation": str(list(state)),
                "Batcher_Comparators_Only": batcher_sort_count(state),
            }
            if dim < 13:
                row["Permutation"] =  str(list(state[:20]))
            for r in extra_routers:
                # row[f"{r['name']}_Steps"] = r["fn"](state)
                
                start = time.perf_counter()
                steps = r["fn"](state)
                elapsed = time.perf_counter() - start

                algo_time[r["name"]] += elapsed


                row[f"{r['name']}_Steps"] = steps
                row[f"{r['name']}_Time_ms"] = elapsed * 1000
            selected_results.append(row)

        os.makedirs("data", exist_ok=True)
        sel_path = f"data/results_{dim_key}_selected.csv"
        pd.DataFrame(selected_results).to_csv(sel_path, index=False)
        print(f"選定測資完成！結果已儲存至 {sel_path}")

        # --- 隨機抽樣 ---
        sample_size = RANDOM_SAMPLE_SIZE.get(dim_key, 0)
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
                #row[f"{r['name']}_Steps"] = r["fn"](state)
                start = time.perf_counter()

                steps = r["fn"](state)

                elapsed = time.perf_counter() - start

                algo_time[r["name"]] += elapsed

                row[f"{r['name']}_Steps"] = steps
                row[f"{r['name']}_Time_ms"] = elapsed * 1000
            sample_results.append(row)

            if (idx + 1) % 10000 == 0:
                print(f"  已完成 {idx + 1} / {sample_size} 筆...")

        rnd_path = f"data/results_{dim_key}_random.csv"
        pd.DataFrame(sample_results).to_csv(rnd_path, index=False)
        print(f"隨機抽樣完成！結果已儲存至 {rnd_path}")

        print(f"\n=== {dim_key.upper()} Runtime ===")

        for name, t in algo_time.items():

            if name not in execution_table:
                execution_table[name] = {}

            dimension_name = f"{dim}D"
            execution_table[name][dimension_name] = round(t, 4)

def main():
    run_3d()
    run_selected()

if __name__ == "__main__":
    main()