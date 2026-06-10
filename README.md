# cube-permutation-solver

可擴展的超立方體排列路由專案（3D + 4D）。

## 專案結構

- `main.py`：唯一入口
- `config.py`：算法與輸出配置
- `src/`：核心與算法
  - `core.py`：`Cube`、型別定義
  - `base.py`：`RouterAlgorithm` 抽象基類
  - `algorithms/`：BFS / Batcher / Custom
  - `utils.py`：狀態、匹配、算法自動發現
- `analysis/`：3D/4D 分析與統計
- `visualize/`：圖表輸出
- `output/`：CSV 與 PNG 結果

## 使用方式

```bash
python main.py
```

執行後會輸出：
- `output/results_3d.csv`
- `output/results_4d.csv`
- `output/3d_distribution.png`
- `output/3d_comparison.png`
- `output/4d_results.png`
- `output/final_curves.png`

## 新增演算法

1. 在 `src/algorithms/` 新增 `new_algorithm.py`
2. 建立繼承 `RouterAlgorithm` 的類別，實作 `route()`
3. 設定唯一 `NAME`（例如 `"new_algo"`）
4. 在 `config.py` 的 `ALGORITHMS_ENABLED` 加入名稱
5. 執行 `python main.py`，分析與圖表會自動納入
