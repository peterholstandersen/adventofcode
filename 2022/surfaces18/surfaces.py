import sys
import time

def get_neighbours(block):
    (x, y, z) = block
    for (dx, dy, dz) in ( (-1,0,0), (1,0,0), (0,-1,0), (0,1,0), (0,0,-1), (0,0,1) ):
        yield (x+dx, y+dy, z+dz)

def count_free_surfaces(blocks):
    count = 0
    for block in blocks:
        for neighbour in get_neighbours(block):
            if not neighbour in blocks:
                count += 1
    return count

def count_hot_surfaces(blocks):
    hot = get_hot_blocks(blocks)
    count = 0
    for block in blocks:
        for neighbour in get_neighbours(block):
            if not neighbour in blocks and neighbour in hot:
                count += 1
    return count

def inside(block, minimum, maximum):
    (x, y, z) = block
    (x1, y1, z1) = minimum
    (x2, y2, z2) = maximum
    return (x1 <= x <= x2) and (y1 <= y <= y2) and (z1 <= z <= z2)

def find_min_max(blocks):
    xs = [ x for (x, _, _) in blocks ]
    ys = [ y for (_, y, _) in blocks ]
    zs = [ z for (_, _, z) in blocks ]
    return ( (min(xs) - 1, min(ys) - 1, min(zs) - 1) , (max(xs) + 1, max(ys) + 2, max(zs) + 2) )

def get_hot_blocks1(block, blocks, minimum, maximum, hot):
    if block in hot:
        return
    hot.add(block)
    for neighbour in get_neighbours(block):
        if neighbour not in blocks and inside(neighbour, minimum, maximum):
            get_hot_blocks1(neighbour, blocks, minimum, maximum, hot)

def get_hot_blocks(blocks):
    (minimum, maximum) = find_min_max(blocks)
    hot = set()
    get_hot_blocks1(minimum, blocks, minimum, maximum, hot)
    return hot

def read_file(filename):
    blocks = set()
    with open(filename) as file:
        for line in file:
            if len(line) == 0:
                continue
            block = line.strip().split(",")
            blocks.add( (int(block[0]), int(block[1]), int(block[2])) )
    return blocks

def main():
    sys.setrecursionlimit(10000)
    # filename = "small.in"; expected_free_count = 64; expected_hot_count = 58
    filename = "big.in"; expected_free_count = 4332; expected_hot_count = 2524
    blocks = read_file(filename)
    start_time = time.time()
    free_count = count_free_surfaces(blocks)
    hot_count = count_hot_surfaces(blocks)
    print(f"free_count = {free_count}:", "ok" if free_count == expected_free_count else f"not ok: expected {expected_free_count}")
    print(f"hot_count = {hot_count}:", "ok" if hot_count == expected_hot_count else f"not ok: expected {expected_hot_count}")
    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__":
    main()