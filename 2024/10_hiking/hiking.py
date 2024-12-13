import sys

# file = "small.in"
file = "big.in"
mapp = open(file).read().strip("\n")
dim = mapp.index("\n")
mapp = mapp.replace("\n", "")

def neighbours(dim, pos):
    result = set()
    (x, y) = (pos % dim, pos // dim)
    for (dx, dy) in ((1, 0), (-1, 0), (0, -1), (0, 1)):
        (x1, y1) = (x + dx, y + dy)
        if 0 <= x1 < dim and 0 <= y1 < dim:
            result.add(x1 + y1 * dim)
    return result

# score is the number of 9s that can be reached from starting_pos
def trail_score(mapp, dim, starting_pos):
    work = { starting_pos }
    nines = set()
    while len(work) > 0:
        pos = work.pop()
        if mapp[pos] == '9':
            nines.add(pos)
        work = work.union({pos1 for pos1 in neighbours(dim, pos) if int(mapp[pos1]) == int(mapp[pos]) + 1})
    return len(nines)

def trail_rating(mapp, dim, starting_pos):
    work = [ (starting_pos,) ]
    trails = set()
    while len(work) > 0:
        trail = work.pop()
        last_pos = trail[-1]
        if mapp[last_pos] == '9':
            trails.add(trail)
        for pos1 in neighbours(dim, last_pos):
            if int(mapp[pos1]) == int(mapp[last_pos]) + 1:
                work.append(trail + (pos1,))
    return len(trails)

part1 = sum([trail_score(mapp, dim, pos) for pos in range(0, len(mapp)) if mapp[pos] == "0"])
part2 = sum([trail_rating(mapp, dim, pos) for pos in range(0, len(mapp)) if mapp[pos] == "0"])
print("part1:", part1) # 611
print("part2:", part2) # 1380
