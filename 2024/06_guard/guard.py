import sys

def walkabout(mapp, dim, line, col, direction, extra_line=None, extra_col=None):
    visited = set()
    visited2 = set()
    is_loop = False
    while True:
        visited.add((line, col))
        if (line, col, direction) in visited2:
            is_loop = True
            break
        visited2.add((line, col, direction))
        (line1, col1) = (line, col)
        match direction:
            case "^": line1 = line - 1
            case "v": line1 = line + 1
            case ">": col1 = col + 1
            case "<": col1 = col - 1
            case _: print("invalid direction", direction); sys.exit(1)
        if line1 < 0 or line1 >= dim or col1 < 0 or col1 >= dim:
            break
        if mapp[line1][col1] == "#" or (line1 == extra_line and col1 == extra_col):
            direction = { "^": ">", ">": "v", "v": "<", "<": "^" }[direction]
        else:
            (line, col) = (line1, col1)
    return (visited, is_loop)

# file = "small.in"
file = "big.in"
text = open(file).read().strip()
mapp = text.split("\n")
dim = len(mapp)
(line, col) = [ (line, col) for line in range(0, dim) for col in range(0, dim) if mapp[line][col] not in { "#", "." } ][0]
direction = mapp[line][col]
(visited, _) = walkabout(mapp, dim, line, col, direction)

print("part1:", len(visited))  # 5242

# Naive approach
# x = [ walkabout(mapp, dim, line, col, direction, extra_line, extra_col) for (extra_line, extra_col) in visited ]
# part2 = len([ z for (z, what) in x if what ])
# print("part2:", part2) # 1424

# ====================================
# Attempt to optimize ... somewhat

def walkabout2(obstacles, dim, line, col, direction, extra_line=None, extra_col=None):
    obstacles = obstacles.copy()
    obstacles.add( (extra_line, extra_col) )
    visited = set()
    visited2 = set()
    is_loop = False
    while True:
        visited.add((line, col))
        if (line, col, direction) in visited2:
            is_loop = True
            break
        visited2.add((line, col, direction))
        match direction:
            case "^":
                (line1, col1) = (line - 1, col)
                if line1 < 0: break
            case "v":
                (line1, col1) = (line + 1, col)
                if line1 >= dim: break
            case ">":
                (line1, col1) = (line, col + 1)
                if col1 >= dim: break
            case "<":
                (line1, col1) = (line, col - 1)
                if col1 < 0: break
            case _:
                print("invalid direction", direction); sys.exit(1)
        if (line1, col1) in obstacles:
            direction = { "^": ">", ">": "v", "v": "<", "<": "^" }[direction]
        else:
            (line, col) = (line1, col1)
    return (visited, is_loop)

obstacles = { (line, col) for line in range(0, dim) for col in range(0, dim) if mapp[line][col] == "#"}
x = [ walkabout2(obstacles, dim, line, col, direction, extra_line, extra_col) for (extra_line, extra_col) in visited ]
part2 = len([ z for (z, what) in x if what ])
print("part2:", part2) # 1424