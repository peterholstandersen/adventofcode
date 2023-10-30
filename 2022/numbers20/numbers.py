import sys

# Note that, this implementation does not move the number to the same absolute position
# as the example on the AoC page. The relative position is still the same. I believe the
# intention of the puzzle is that the absolute positioning does not matter, since the
# puzzle answers only involves the relative positioning.
#
# My implementation works for the dataset in the big.in (5000 numbers), but it is O(n^2),
# so it doesn't really scale, Lowering the complexity would require keeping track of the
# numbers after they have been moved. But, it gets the job done, so I'll leave it at that :)
# It is the only X-mas once a year, right?
#
# Initial arrangement:          length 7, list starts at index 0
# 1, 2, -3, 3, -2, 0, 4
#
# 1 moves between 2 and -3:     move 1: old_index = 0
# 2, -3, 3, -2, 0, 4            remove 1
# 2, 1, -3, 3, -2, 0, 4         insert at index 1 = old_index + 1
#
# 2 moves between -3 and 3:     move 2: old_index = 0
# 1, -3, 3, -2, 0, 4            remove 2
# 1, -3, 2, 3, -2, 0, 4         insert at index 2 = old_index + 2
#
# -3 moves between -2 and 0:    move -3: old_index = 1
# 1, 2, 3, -2, 0, 4             remove -3
# 1, 2, 3, -2, -3, 0, 4         insert at 4 = (old_index - 3) % (length - 1) = -2 % 6
#
# 3 moves between 0 and 4:      move 3: old_index 2
# 1, 2, -2, -3, 0, 4            remove 3
# 1, 2, -2, -3, 0, 3, 4         insert at 5 = old_index + 3
#
# -2 moves between 4 and 1:     move -2: index 2
# 1, 2, -3, 0, 3, 4             remove -2
# -2, 1, 2, -3, 0, 3, 4         insert at 0 = old_index - 2
#
# As explaining above, the absolute positioning differs from the example on the AoC page.

def small():
    # This only works when the numbers in the lists are unique as in the small set of numbers.
    # So, it does not work for the big set of numbers.
    numbers = list(map(int, open("small.in").read().strip().split("\n")))
    length = len(numbers)
    for number in numbers.copy():
        old_index = numbers.index(number)
        new_index = (old_index + number) % (length - 1)
        del numbers[old_index]
        numbers.insert(new_index, number)
    index = numbers.index(0)
    result = sum([numbers[(index + x) % length] for x in [1000, 2000, 3000]])
    print("small-part1:", result)

def big(part2=False):
    data = list(map(int, open("big.in").read().strip().split("\n")))
    length = len(data)
    if part2:
        data = list(map(lambda x: x * 811589153, data))
    if data.count(0) != 1:
        print("error in input")
        sys.exit(1)
    # Attach a unique index to each number, so that we can find it after it has been moved
    # [1, 2, -3, 3, -2, 0, 4] becomes [(0,1), (1,2), (2,-3), ...]
    numbers = list(zip(range(length), data))
    original_numbers = numbers.copy()
    for _ in range(10 if part2 else 1):
        for pair in original_numbers:
            old_index = numbers.index(pair)
            new_index = (old_index + pair[1]) % (length - 1)
            del numbers[old_index]
            numbers.insert(new_index, pair)
    unzip = [ n for (_,n) in numbers ]
    index = unzip.index(0)
    result = sum([unzip[(index + x) % length] for x in [1000, 2000, 3000]])
    print("big-part2:" if part2 else "big-part1:", result)

if __name__ == "__main__":
    small()
    big()
    big(part2=True)

# small-part1: 3
# small-part2: 1623178306 (not implemented)
# big-part1: 10763
# big-part2: 4979911042808