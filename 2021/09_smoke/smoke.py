import math
from functools import reduce
from utils import Timer

def read_file(filename):
    text = open(filename).read().strip()
    height = text.count("\n") + 1
    width = text.index("\n")
    text = text.replace("\n", "")
    heightmap = { (row, col): int(text[row * width + col]) for row in range(height) for col in range(width) }
    return (heightmap, lambda pos: heightmap.get(pos, math.inf))

def neighbours(pos, height):
    up = lambda pos: (pos[0] - 1, pos[1])
    down = lambda pos: (pos[0] + 1, pos[1])
    left = lambda pos: (pos[0], pos[1] - 1)
    right = lambda pos: (pos[0], pos[1] + 1)
    return [x for x in [up(pos), down(pos), left(pos), right(pos)] if height(x) != math.inf]

def lowest_points(heightmap, height):
    return (pos for pos in heightmap
                if all((height(pos) < height(n) for n in neighbours(pos, height))))

def part1(filename, expected):
    (heightmap, height) = read_file(filename)
    result = sum([ height(pos) + 1 for pos in lowest_points(heightmap, height) ])
    print("part1", filename, result)
    assert(result == expected)

def get_basin(pos, height):
    return reduce(lambda xs, ys: xs.union(ys),
                  [ get_basin(neighbour, height)
                    for neighbour in neighbours(pos, height)
                    if height(neighbour) != 9 and height(neighbour) > height(pos) ],
                  { pos })

def part2(filename, expected):
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