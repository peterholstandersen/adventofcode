from utils import Map, Timer

def get_visible_seats(start_x, start_y, mapp):
    for (x1, y1) in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
        (x, y) = (start_x, start_y)
        while (x, y) in mapp:
            (x, y) = (x + x1, y + y1)
            if mapp[(x, y)] != ".":
                yield mapp[(x, y)]
                break

def part1(filename, part1=False):
    count = 4 if part1 else 5
    mapp = Map(filename)
    # If a seat is empty (L) and there are no occupied seats adjacent to it, the seat becomes occupied.
    # If a seat is occupied (#) and four or more seats adjacent to it are also occupied, the seat becomes empty. (five for part2)
    while True:
        becomes_occupied = list()
        becomes_empty = list()
        for ((x, y), value) in mapp.all():
            if value == ".":
                continue
            if part1:
                seats = (mapp[neighbour] for neighbour in mapp.get_neighbours((x, y), diagonal=True))
            else:
                seats = get_visible_seats(x, y, mapp)
            match value:
                case "L" if all((seat != "#" for seat in seats)): becomes_occupied.append((x, y))
                case "#" if list(seats).count("#") >= count:      becomes_empty.append((x, y))
        for seat in becomes_occupied: mapp[seat] = "#"
        for seat in becomes_empty: mapp[seat] = "L"
        if len(becomes_occupied) == 0 and len(becomes_empty) == 0:
            break

    occupied_seats = [value for ((x, y), value) in mapp.all()].count("#")
    print("part1" if part1 else "part2", filename, occupied_seats)

if __name__ == "__main__":
    with Timer() as _:
        part1("small.in", part1=True)  # 37
        part1("big.in", part1=True)    # 2324
        part1("small.in", part1=False) # 26
        part1("big.in", part1=False)   # 2068