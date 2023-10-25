from typing import List

def read_input(filename: str) -> List[str]:
    with open(filename) as file:
        rucksacks = [ text.strip() for text in file.read().strip("\n").split("\n") ]
    return rucksacks

def value(ch):
    if 'a' <= ch <= 'z':
        return ord(ch) - ord('a') + 1
    elif 'A' <= ch <= 'Z':
        return ord(ch) - ord('A') + 27
    else:
        assert(False)

def part1(rucksacks):
    total = 0
    for rucksack in rucksacks:
        count = len(rucksack) // 2
        items1 = set(rucksack[:count])
        items2 = set(rucksack[count:])
        common = items1.intersection(items2)
        assert(len(common) == 1)
        item = common.pop()
        print(item, value(item))
        total += value(item)
    return total

def part2(rucksacks):
    total = 0
    # split into threes
    for i in range(0, len(rucksacks) // 3):
        items1 = set(rucksacks[i * 3])
        items2 = set(rucksacks[i * 3 + 1])
        items3 = set(rucksacks[i * 3 + 2])
        common = items1.intersection(items2).intersection(items3)
        assert(len(common) == 1)
        item = common.pop()
        print(item, value(item))
        total += value(item)
    return total

def main():
    small = read_input("small.in")
    big = read_input("big.in")
    part1_small = part1(small)
    part2_small = part2(small)
    part1_big = part1(big)
    part2_big = part2(big)
    print("part1 small", part1_small)
    print("part1 big", part1_big)
    print("part2 small", part2_small)
    print("part2 big", part2_big)

if __name__ == "__main__":
    main()