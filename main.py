from __future__ import annotations

from pathlib import Path

import config
from analysis.runner_3d import run_3d
from analysis.runner_4d import run_4d
from src.core import Cube
from src.utils import ensure_output_dir, load_algorithms
from visualize.plots import plot_3d_distribution, plot_avg_comparison, plot_final_curves


def build_instances(cube: Cube):
    classes = load_algorithms(config.ALGORITHMS_ENABLED)
    instances = {}
    for name, cls in classes.items():
        if name == "bfs" and cube.dimension == 4:
            instances[name] = cls(cube, max_visited=config.BFS_4D_MAX_VISITED)
        else:
            instances[name] = cls(cube)
    return instances


def main() -> None:
    out_dir = Path(config.OUTPUT_DIR)
    ensure_output_dir(out_dir)

    algorithms_3d = build_instances(Cube(3))
    _, steps_3d, summary_3d = run_3d(
        algorithms_3d,
        out_dir / config.RESULTS_3D_CSV,
    )

    algorithms_4d = build_instances(Cube(4))
    _, steps_4d, summary_4d = run_4d(
        algorithms_4d,
        out_dir / config.RESULTS_4D_CSV,
    )

    plot_3d_distribution(steps_3d, out_dir / config.PLOT_3D_DISTRIBUTION)
    plot_avg_comparison(summary_3d, out_dir / config.PLOT_3D_COMPARISON, "3D average steps")
    plot_avg_comparison(summary_4d, out_dir / config.PLOT_4D_RESULTS, "4D selected average steps")

    final_step_map = {f"3d_{k}": v for k, v in steps_3d.items()}
    final_step_map.update({f"4d_{k}": v for k, v in steps_4d.items()})
    plot_final_curves(final_step_map, out_dir / config.PLOT_FINAL_CURVES)

    print("Done. Output files written to", out_dir.resolve())


if __name__ == "__main__":
    main()
