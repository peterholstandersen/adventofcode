#         [G]         [D]     [Q]
# [P]     [T]         [L] [M] [Z]
# [Z] [Z] [C]         [Z] [G] [W]
# [M] [B] [F]         [P] [C] [H] [N]
# [T] [S] [R]     [H] [W] [R] [L] [W]
# [R] [T] [Q] [Z] [R] [S] [Z] [F] [P]
# [C] [N] [H] [R] [N] [H] [D] [J] [Q]
# [N] [D] [M] [G] [Z] [F] [W] [S] [S]
#  1   2   3   4   5   6   7   8   9

def get_towers(filename):
    if filename == "small.in":
        towers = [ "", "NZ", "DCM", "P" ]
    else:
        towers = [ "", "PZMTRCN", "ZBSTND", "GTCFRQHM", "ZRG", "HRNZ", "DLZPWSHF", "MGCRZDW", "QZWHLFJS", "NWPQS" ]
    return [ list(tower) for tower in towers ]

def get_moves(filename):
    with (open(filename) as file):
        text = file.read().strip()
        text = text[text.index("move"):]
        return text.split("\n")

def part1(towers, moves):
    for move in moves:
        match (move.split(" ")):
            case ["move", number, "from", source, "to", target]:
                for _ in range(0, int(number)):
                    towers[int(target)].insert(0, towers[int(source)].pop(0))
            case _:
                print("hmm")
        print(towers)
    return towers

def part2(towers, moves):
    for move in moves:
        print(towers, move)
        match (move.split(" ")):
            case ["move", number, "from", source, "to", target]:
                number = int(number)
                source = int(source)
                target = int(target)
                to_move = towers[source][0:number]
                towers[source] = towers[source][number:]
                towers[target] = to_move + towers[target]
            case _:
                print("hmm")
        print(towers)
    return towers


def main():
    if False:
        towers = get_towers("big.in")
        moves = get_moves("big.in")
        towers = part1(towers, moves)
        print(towers)
        print("part1: ", end="") # big.in: RTGWZTHLD
        for tower in towers[1:]:
            print(tower[0], end="")
        print()
        print()
    towers = get_towers("big.in")
    moves = get_moves("big.in")
    towers = part2(towers, moves) # small.in: MCD, big.in: STHGRZZFR
    print(towers)
    print("part2: ", end="")
    for tower in towers[1:]:
        print(tower[0], end="")
    print()

if __name__ == "__main__":
    main()