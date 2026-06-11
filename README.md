# 超立方體排列路由實驗

在超立方體網路上，將封包透過合法邊交換（僅能交換二進位差一位的相鄰節點）路由回正確位置，並比較各演算法的步數表現。

## 快速執行

```bash
pip install pandas matplotlib tabulate
python main.py
```

---

## 新增演算法

**第一步：建立 `algorithms/你的演算法.py`**
```python
from .base import RoutingAlgorithm

class 你的Router(RoutingAlgorithm):
    def route(self, state):
        # 回傳一個 list of matchings（每個 matching 是一組邊交換）
        ...
```

**第二步：在 `experiments/run_experiments.py` 加兩行**
```python
# 頂部加 import
from algorithms.你的演算法 import 你的Router

# 在 build_extra_routers() 裡加一筆
def build_extra_routers(cube):
    return [
        {"name": "你的演算法", "fn": lambda state: sum(len(m) for m in 你的Router(cube).route(state))},
    ]
```

✅ CSV、統計報告、圖表全部自動更新，其他檔案不需要動。

---

## 新增維度（5D、6D、...）

開啟 `experiments/run_experiments.py`，找到以下兩個地方新增：

```python
SELECTED_TESTCASES = {
    "4d": [...],
    "5d": [[31, 0, 1, ...]],  # ← 在這裡加選定測資
}

RANDOM_SAMPLE_SIZE = {
    "4d": 40000,
    "5d": 40000,  # ← 在這裡加隨機抽樣數量
}
```

✅ 新的 CSV 和圖表自動產生，不需要改其他地方。

---

## 專案結構

```
├── main.py                      # 執行入口，依序跑所有步驟
├── utils.py                     # 超立方體定義與工具函式
├── algorithms/
│   ├── base.py                  # 演算法基底類別
│   ├── bfs.py                   # BFS（最短步數 Ground Truth）
│   └── batcher.py               # Batcher Sorting Network
├── experiments/
│   ├── run_experiments.py       # ★ 新增演算法 / 新增維度 → 改這裡
│   └── compare.py               # 統計報告輸出
├── analysis/
│   └── plot.py                  # 圖表生成
└── data/                        # 自動產生的 CSV 結果
```
