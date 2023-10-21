import sys

def error(msg):
    print(msg)
    sys.exit(1)

def sign(x):
    return 0 if x == 0 else -1 if x < 0 else 1

def my_range(a, b):
    return [a] if a == b else range(a, b + sign(b-a), sign(b-a))

down = lambda xy: (xy[0], xy[1] + 1)
downleft = lambda xy: (xy[0] - 1, xy[1] + 1)
downright = lambda xy: (xy[0] + 1, xy[1] + 1)

def read_input(filename):
    # Format example: "498,4 -> 498,6 -> 496,6"
    paths = []
    with open(filename) as file:
        for line in file:
            paths.append( [ (int(xy[0]), int(xy[1])) for xy in [ xys.split(",") for xys in line.split(" -> ") ] ] )
    return paths

def get_all_rocks(paths):
    rocks = set()
    for path in paths:
        path_pairs = [ (path[i - 1], path[i]) for i in range(1, len(path)) ]
        for (x1,y1), (x2,y2) in path_pairs:
            [ rocks.add( (x, y) ) for x in my_range(x1, x2) for y in my_range(y1, y2) ]
    return rocks

def print_it(rocks, occupied, entry, floor):
    xs = [x for (x,y) in occupied]
    ys = [y for (x,y) in occupied]
    min_x = min(xs)
    max_x = max(xs)
    min_y = min(ys)
    # goto home: out = chr(27) + "[H" + chr(27) + "[?25l"
    for y in my_range(min_y, floor):
        out = ""
        for x in my_range(min_x-1, max_x+1):
            if (x, y) in rocks or y == floor:
                out = out + "#"
            elif (x, y) in occupied:
                out = out + "o"
            elif (x, y) == entry:
                out = out + "+"
            else:
                out = out + "."
        print(out)

# goto position: print(chr(27) + f"[{sand[1] - 1};{sand[0] - min_x + 2}H" + ".")
def drop_one(occupied, sand, floor):
    while True:
        if sand[1] >= floor - 1:
            break
        if down(sand) not in occupied:
            sand = down(sand)
        elif downleft(sand) not in occupied:
            sand = downleft(sand)
        elif downright(sand) not in occupied:
            sand = downright(sand)
        else:
            break
    occupied.add(sand)

def drop_sand(occupied, entry, max_count, floor):
    count = 0
    while entry not in occupied:
        drop_one(occupied, entry, floor)
        count = count + 1
        # if False and count % 100 == 1:
        #    print_it(rocks, occupied, entry, floor)
        if max_count is not None and count >= max_count:
            print(f"Max count reached {max_count}")
            break

def main():
    #filename = "big.in"
    filename = "small.in"
    entry = (500, 0)
    paths = read_input(filename)
    rocks = get_all_rocks(paths)
    floor = max([y for (x, y) in rocks]) + 2
    occupied = rocks.copy()
    drop_sand(occupied, entry, 200000, floor)
    print_it(rocks, occupied, entry, floor)
    print(f"rocks={len(rocks)}  occupied={len(occupied)}  sand={len(occupied) - len(rocks)}")
    # 25402

if __name__ == "__main__":
    main()