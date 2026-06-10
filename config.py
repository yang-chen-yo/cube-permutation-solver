from __future__ import annotations

ALGORITHMS_ENABLED = {"bfs", "batcher", "custom"}

# BFS on 4D can explode in state-space. Keep a safety limit for selected samples.
BFS_4D_MAX_VISITED = 200_000

OUTPUT_DIR = "output"
RESULTS_3D_CSV = "results_3d.csv"
RESULTS_4D_CSV = "results_4d.csv"
PLOT_3D_DISTRIBUTION = "3d_distribution.png"
PLOT_3D_COMPARISON = "3d_comparison.png"
PLOT_4D_RESULTS = "4d_results.png"
PLOT_FINAL_CURVES = "final_curves.png"
