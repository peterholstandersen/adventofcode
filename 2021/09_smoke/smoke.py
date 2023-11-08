import math
from typing import Dict, Tuple, Callable, List, Iterable, Set
from functools import reduce
from utils import Timer

Position = Tuple[int, int]
HeightMap = Dict[Position, int]
HeightFunction = Callable[[Position], int]

def read_file(filename: str) -> Tuple[HeightMap, HeightFunction]:
    text = open(filename).read().strip()
    height = text.count("\n") + 1
    width = text.index("\n")
    text = text.replace("\n", "")
    heightmap = { (row, col): int(text[row * width + col]) for row in range(height) for col in range(width) }
    return (heightmap, lambda pos: heightmap.get(pos, math.inf))

def neighbours(pos: Position, height: HeightFunction) -> List[Position]:
    up = lambda pos: (pos[0] - 1, pos[1])
    down = lambda pos: (pos[0] + 1, pos[1])
    left = lambda pos: (pos[0], pos[1] - 1)
    right = lambda pos: (pos[0], pos[1] + 1)
    return [x for x in [up(pos), down(pos), left(pos), right(pos)] if height(x) != math.inf]

def lowest_points(heightmap: HeightMap, height: HeightFunction) -> Iterable[Position]:
    return (pos for pos in heightmap
                if all((height(pos) < height(n) for n in neighbours(pos, height))))

# find the sum of the risk levels of all lowest points, where risk level = height + 1
def part1(filename: str, expected: int) -> None:
    (heightmap, height) = read_file(filename)
    result = sum([ height(pos) + 1 for pos in lowest_points(heightmap, height) ])
    print("part1", filename, result)
    assert(result == expected)

# find the basin surround pos, i.e., go up in all directions until you get to the top (9 is not included)
def get_basin(pos: Position, height: HeightFunction) -> Set[Position]:
    return reduce(lambda xs, ys: xs.union(ys),
                  [ get_basin(neighbour, height)
                    for neighbour in neighbours(pos, height)
                    if height(neighbour) != 9 and height(neighbour) > height(pos) ],
                  { pos })

# compute the multipla of the sizes of the three largest basins
def part2(filename: str, expected: int) -> None:
    (heightmap, height) = read_file(filename)
    basins = sorted([ len(get_basin(pos, height)) for pos in lowest_points(heightmap, height) ])
    result = basins[-3] * basins[-2] * basins[-1]
    print("part2", filename, result)
    assert(result == expected)

if __name__ == "__main__":
    with Timer():
        part1("small.in", 15)
        part1("big.in", 436)
        part2("small.in", 1134)
        part2("big.in", 1317792)