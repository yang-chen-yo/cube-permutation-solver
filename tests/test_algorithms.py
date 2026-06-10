from src.core import Cube
from src.utils import load_algorithms


def test_algorithm_auto_discovery_contains_required_algorithms():
    algorithms = load_algorithms({"bfs", "batcher", "custom"})
    assert {"bfs", "batcher", "custom"}.issubset(set(algorithms.keys()))


def test_all_algorithms_can_route_simple_3d_state_to_identity():
    cube = Cube(3)
    state = (1, 0, 2, 3, 4, 5, 6, 7)
    algorithms = load_algorithms({"bfs", "batcher", "custom"})

    for name, cls in algorithms.items():
        router = cls(cube)
        path = router.route(state)
        final = router.apply_path(state, path)
        assert final == cube.identity, f"algorithm {name} failed"
