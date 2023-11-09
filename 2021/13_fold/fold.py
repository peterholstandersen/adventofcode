import sys

def read_file(filename):
    (coordinates, folds) = open(filename).read().strip().split("\n\n")
    foo = { (int(coor[0]), int(coor[1])) for coor in (line.strip().split(",") for line in coordinates.strip().split("\n")) }
    print(foo)
    bar = list(map(lambda aa: (aa[0], int(aa[1])), [ (folds.split(" ")[-1]).split("=") for folds in folds.split("\n") ]))
    print(bar)
    return (foo, bar)

def print_it(dots):
    min_x = min([x for (x,y) in dots])
    max_x = max([x for (x,y) in dots])
    min_y = min([y for (x,y) in dots])
    max_y = max([y for (x,y) in dots])
    out = ""
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            out = out + ("#" if (x, y) in dots else ".")
        out = out + "\n"
    print(out)

def part2(filename):
    (dots, folds) = read_file(filename)
    for (axis, coor) in folds:
        if axis == 'y':
            new = {(x, y) for (x, y) in dots if y <= coor}
            new.update({(x, 2 * coor - y) for (x, y) in dots if y > coor})
            dots = new
        elif axis == 'x':
            new = {(x, y) for (x, y) in dots if x <= coor}
            new.update({(2 * coor - x, y) for (x, y) in dots if x > coor})
            dots = new
        else:
            print("error")
            sys.exit(1)
        print()
        print_it(dots)

def part1(filename, expected):
    (dots, folds) = read_file(filename)
    axis = folds[0][0]
    coor = folds[0][1]
    if axis == 'y':
        new = {(x, y) for (x, y) in dots if y <= coor}
        new.update({(x, 2 * coor - y) for (x, y) in dots if y > coor})
    elif axis == 'x':
        new = {(x, y) for (x, y) in dots if x <= coor}
        new.update({(2 * coor - x, y) for (x, y) in dots if x > coor})
    else:
        print("error")
        sys.exit(1)
    print(len(new))
    assert(len(new) == expected)

if __name__ == "__main__":
    part1("big.in", 770)
    part2("big.in")            # EPUELPBR
