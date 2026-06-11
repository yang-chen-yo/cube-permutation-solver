from flask import Flask, request, jsonify, send_from_directory
import sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import Cube
from algorithms.bfs import BFSRouter
from algorithms.batcher import BatcherRouter
from algorithms.bitonic import BitonicRouter
from algorithms.greedy_matching import GreedyMatchingRouter

app = Flask(__name__, static_folder="web")

def matchings_to_steps(route_path, start_state):
    state = list(start_state)
    steps = []
    for matching in route_path:
        for u, v in matching:
            state[u], state[v] = state[v], state[u]
        steps.append({
            "swaps": [[u, v] for u, v in matching],
            "state": list(state)
        })
    return steps

def batcher_to_steps(initial_state):
    n = len(initial_state)
    dim = n.bit_length() - 1
    state = list(initial_state)
    steps = []
    for i in range(1, dim + 1):
        for j in range(i - 1, -1, -1):
            dist = 1 << j
            swaps = []
            for u in range(n):
                if (u & dist) == 0:
                    v = u + dist
                    dir_asc = ((u >> i) & 1) == 0
                    if (dir_asc and state[u] > state[v]) or (not dir_asc and state[u] < state[v]):
                        swaps.append([u, v])
                        state[u], state[v] = state[v], state[u]
            if swaps:
                steps.append({"swaps": swaps, "state": list(state)})
    return steps

@app.route("/api/route", methods=["POST"])
def route():
    data = request.json
    dim = int(data.get("dim", 3))
    perm = list(map(int, data.get("perm", [])))
    algo = data.get("algo", "bfs")
    n = 1 << dim

    if len(perm) != n:
        return jsonify({"error": f"排列長度應為 {n}"}), 400
    if sorted(perm) != list(range(n)):
        return jsonify({"error": "不是合法排列"}), 400

    state = tuple(perm)
    cube = Cube(dim=dim)

    try:
        if algo == "bfs_serial":
            router = BFSRouter(cube, use_matchings=False)
            path = router.route(state)
            steps = matchings_to_steps(path, state)

        elif algo == "bfs_parallel":
            router = BFSRouter(cube, use_matchings=True)
            path = router.route(state)
            steps = matchings_to_steps(path, state)

        elif algo == "batcher_serial":
            steps = batcher_to_steps(perm)

        elif algo == "batcher_parallel":
            router = BatcherRouter(cube)
            path = router.route(state)
            steps = matchings_to_steps(path, state)

        elif algo == "bitonic_serial":
            router = BitonicRouter(cube, use_parallel=False)
            path = router.route(state)
            steps = matchings_to_steps(path, state)

        elif algo == "bitonic_parallel":
            router = BitonicRouter(cube, use_parallel=True)
            path = router.route(state)
            steps = matchings_to_steps(path, state)

        elif algo == "greedy_beam":
            router = GreedyMatchingRouter(cube)
            path = router.route(state)
            steps = matchings_to_steps(path, state)

        else:
            return jsonify({"error": "未知演算法"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "dim": dim,
        "initial_state": perm,
        "algo": algo,
        "total_steps": len(steps),
        "steps": steps
    })

@app.route("/")
def index():
    return send_from_directory("web", "index.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)