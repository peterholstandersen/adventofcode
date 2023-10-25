def read_input(filename: str):
    with open(filename) as file:
        # list where each element is pair - one for each elf.
        # The pairs themselves are also pairs denoting the sections (to, from) inclusive
        # For example, [((2, 4), (6, 8)), ((2, 3), (4, 5)), ... ]
        return [ (tuple(map(int, elf1.split("-"))), tuple(map(int, elf2.split("-")))) for (elf1, elf2) in [ pair.split(",") for pair in file.read().strip("\n").split("\n") ]]

def part1(work):
    count = 0
    for elf_pair in work:
        ((start1, end1), (start2, end2)) = elf_pair
        if start1 >= start2 and end1 <= end2:
            count += 1
        elif start2 >= start1 and end2 <= end1:
            count += 1
    return count

def part2(work):
    count = 0
    for elf_pair in work:
        ((start1, end1), (start2, end2)) = elf_pair
        if start2 < start1:
            (start1, start2) = (start2, start1)
            (end1, end2) = (end2, end1)
        if end1 >= start2:
            count += 1
    return count

def main():
    small_work = read_input("small.in")
    big_work = read_input("big.in")

    small_count = part1(small_work)
    big_count = part1(big_work)
    part2_count = part2(big_work)

    print("part1 small.in:", small_count)  # 2
    print("part1 big.in:", big_count)      # 532
    print("part2 big.in", part2_count)     # 854

if __name__ == "__main__":
    main()