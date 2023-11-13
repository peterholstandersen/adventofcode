from functools import cache
from networkx import DiGraph, shortest_path
from utils import Map, Timer

def part1(filename):
    size = 100 if filename == "big.in" else 10
    mapp = Map(filename)
    graph = DiGraph()
    for (pos, value) in mapp.all():
        for neighbour in mapp.get_neighbours(pos):
            graph.add_edge(pos, neighbour, weight=value)
    sp = shortest_path(graph, (1, 1), (size, size), "weight")
    part1 = sum(map(lambda pos: mapp[pos], sp[1:]))
    print("part1", filename, part1)  # part1 big.in: 553

def get_neighbours(x, y, line, col, factor, size, mapp):
    for xylc in [(x, y, l, c) for (l, c) in mapp.get_neighbours((line, col))]:
        yield xylc
    if line == 1 and y != 0:
        yield (x, y - 1, size, col)
    elif line == size and y != (factor - 1):
        yield (x, y + 1, 1, col)
    if col == 1 and x != 0:
        yield (x - 1, y, line, size)
    elif col == size and x != (factor - 1):
        yield (x + 1, y, line, 1)

def get_value(pos, mapp):
    (x, y, line, col) = pos
    return (x + y + mapp[(line, col)] - 1) % 9 + 1

def part2(filename):
    size = 100 if filename == "big.in" else 10
    factor = 5
    mapp = Map(filename)
    graph = DiGraph()
    for (x, y) in ((x, y) for x in range(0, factor) for y in range(0, factor)):
        for ((line, col), value) in mapp.all():
            for neighbour in get_neighbours(x, y, line, col, factor, size, mapp):
                graph.add_edge((x, y, line, col), neighbour, weight=get_value(neighbour, mapp))
    sp = shortest_path(graph, (0, 0, 1, 1), (factor - 1, factor - 1, size, size), "weight")
    part2 = sum(map(lambda xylc: get_value(xylc, mapp), sp[1:]))
    print("part2", filename, part2)

if __name__ == "__main__":
    part1("small.in")   # 490
    part1("big.in")     # 553
    part2("small.in")   # 315
    with Timer() as _:
        part2("big.in") # 2858
