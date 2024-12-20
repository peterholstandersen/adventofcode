import sys
from utils import Timer

# file = "small.in"
file = "big.in"
maze = open(file).read()

dim = maze.index("\n")
maze = maze.replace("\n", "")
start = maze.find("S")
end = maze.find("E")

up = lambda pos: pos - dim
down = lambda pos: pos + dim
right = lambda pos: pos + 1
left = lambda pos: pos - 1

def shortest_path(maze, start, end):
    distance = dict()
    work = [(start, 0, (start,))]
    while len(work) > 0:
        (pos, dist, path) = work[0]
        work = work[1:]
        if pos in distance:
            continue
        distance[pos] = dist
        if pos == end:
            break
        neighbours = [direction(pos) for direction in (up, down, left, right)]
        neighbours = [pos for pos in neighbours if 0 < pos % dim < dim - 1 and 0 < pos // dim < dim - 1]
        work = work + [(pos, dist + 1, path + (pos,)) for pos in neighbours if maze[pos] != "#"]
    return (distance, path)

def measure(pos1, pos2):
    global dim
    (x1, y1) = (pos1 % dim, pos1 // dim)
    (x2, y2) = (pos2 % dim, pos2 // dim)
    (dx, dy) = (abs(x1 - x2), abs(y1 - y2))
    return dx + dy

def doit(maze, start, end, max_shortcut_length):
    global dim
    (distance, path) = shortest_path(maze, start, end)
    shortcuts = []
    with Timer():
        for (n, pos1) in zip(range(0, len(path) + 1), path):
            if n % 500 == 0:
                print(".", end="")
                sys.stdout.flush()
            x1 = pos1 % dim
            y1 = pos1 // dim
            for pos2 in path[n + 2:]:
                dx = abs(x1 - pos2 % dim)
                if dx <= max_shortcut_length:
                    dy = abs(y1 - pos2 // dim)
                    if 2 <= dx + dy <= max_shortcut_length:
                        shortcuts.append((pos1, pos2))
        print()
    print("shortcuts:", len(shortcuts))
    cheats = dict()
    distance_without_shortcut = distance[end]
    for (pos1, pos2) in shortcuts:
        distance_with_shortcut = distance[pos1] + measure(pos1, pos2) + (distance[end] - distance[pos2])
        saved = distance_without_shortcut - distance_with_shortcut
        if file == "small.in" and saved == 0:
            continue
        if file == "big.in" and saved < 100:
            continue
        if saved in cheats:
            cheats[saved] += 1
        else:
            cheats[saved] = 1
    result = sum([count for (_, count) in cheats.items()])
    return result

part1 = doit(maze, start, end, 2)
part2 = doit(maze, start, end, 20)
print("part1:", part1) # small: 44, big: 1395
print("part2:", part2) # big: 993178

# ===================================

def shortest_path_not_used(maze, start, end, skip):
    distance = dict()
    work = [(start, 0)]
    while len(work) > 0:
        (pos, dist) = work[0]
        work = work[1:]
        if pos in distance:
            continue
        distance[pos] = dist
        if pos == end:
            break
        neighbours = [direction(pos) for direction in (up, down, left, right)]
        neighbours = [pos for pos in neighbours if 0 < pos % dim < dim - 1 and 0 < pos // dim < dim - 1]
        work = work + [(pos, dist + 1) for pos in neighbours if maze[pos] != "#" or pos == skip]
    return distance.get(end)

# Naive :)
def do_part1_naive(maze, start, end):
    cheats = dict()
    x = shortest_path(maze, start, end, None)
    print("shortest path:", x)
    for skip in range(0, len(maze)):
        if maze[skip] != "#":
            continue
        y = shortest_path(maze, start, end, skip)
        saved = x - y
        if saved < 100:
            continue
        print(skip, saved)
        if saved in cheats:
            cheats[saved] += 1
        else:
            cheats[saved] = 1
    print(sorted(cheats.items()))
    part1 = sum([count for (saved, count) in cheats.items() if saved >= 100])
    print("part1:", part1) # 1395
