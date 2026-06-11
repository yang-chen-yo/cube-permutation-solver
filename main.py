from utils import Cube
from algorithms.bfs import BFSRouter

cube = Cube(dim=3)
router = BFSRouter(cube, use_matchings=False)
path = router.route((2,0,1,3,5,4,6,7))

for i, matching in enumerate(path):
    print(f"步驟 {i+1}: {matching}")