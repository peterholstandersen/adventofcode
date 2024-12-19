import sys

def print_it(bytez, distance):
    for y in range(0, dim):
        out = ""
        for x in range(0, dim):
            if (x,y) in bytez:
                out += "#"
            elif (x,y) in distance:
                out += "O"
            else:
                out += "."
        print(out)

# (file, dim, part1_limit) = ("small.in", 7, 12)
(file, dim, part1_limit) = ("big.in", 71, 1024)
all_bytes = [(int(x),int(y)) for [x,y] in [line.strip().split(",") for line in open(file)]]

def shortest_distance(all_bytes, dim, nof_bytes):
    bytez = all_bytes[:nof_bytes]
    start = (0, 0)
    end = (dim - 1, dim - 1)
    distance = dict()
    work = [ (start, 0) ]
    while len(work) > 0:
        ((x, y), dist) = work[0]
        work = work[1:]
        if (x, y) in distance:
            continue
        distance[(x, y)] = dist
        if (x, y) == end:
            break
        neighbours = [(x + x1, y + y1) for (x1, y1) in [(1, 0), (-1, 0), (0, 1), (0, -1) ] if 0 <= x + x1 < dim and 0 <= y + y1 < dim]
        work = work + [((x2, y2), dist + 1) for (x2, y2) in neighbours if (x2, y2) not in bytez and (x2, y2) not in distance]
    return distance.get(end)

part1 = shortest_distance(all_bytes, dim, part1_limit)
print("part1:", part1) # 416

low = part1_limit
high = len(all_bytes)
while low + 1 < high:
    mid = (low + high) // 2
    dist = shortest_distance(all_bytes, dim, mid)
    print("(low, mid, high):", (low, mid, high), " distance(mid):", dist)
    if not dist:
        high = mid
    else:
        low = mid

print("part2:", high - 1, all_bytes[high - 1])  # 2868 (50,23)
