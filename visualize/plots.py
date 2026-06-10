from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from analysis.stats import distribution


def plot_3d_distribution(step_map: dict[str, list[int]], out_path: Path) -> None:
    plt.figure(figsize=(9, 5))
    for name, steps in step_map.items():
        dist = distribution(steps)
        plt.plot(list(dist.keys()), list(dist.values()), marker="o", label=name)
    plt.xlabel("Routing steps")
    plt.ylabel("Permutation count")
    plt.title("3D routing step distribution")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_avg_comparison(summary: dict[str, dict[str, float | int]], out_path: Path, title: str) -> None:
    names = list(summary.keys())
    avgs = [summary[name]["avg"] for name in names]
    plt.figure(figsize=(8, 5))
    plt.bar(names, avgs)
    plt.ylabel("Average routing steps")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_final_curves(result_map: dict[str, list[int]], out_path: Path) -> None:
    plt.figure(figsize=(10, 6))
    for name, steps in result_map.items():
        dist = distribution(steps)
        plt.plot(list(dist.keys()), list(dist.values()), marker="o", label=name)
    plt.xlabel("Routing steps")
    plt.ylabel("Count")
    plt.title("Final routing curves (all algorithms)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
