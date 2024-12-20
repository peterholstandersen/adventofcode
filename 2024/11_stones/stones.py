import sys
from functools import cache

# If the stone is engraved with the number 0, it is replaced by a stone engraved with the number 1.
# If the stone is engraved with a number that has an even number of digits, it is replaced by two stones. The left half of the digits are engraved on the new left stone, and the right half of the digits are engraved on the new right stone. (The new numbers don't keep extra leading zeroes: 1000 would become stones 10 and 0.)
# If none of the other rules apply, the stone is replaced by a new stone; the old stone's number multiplied by 2024 is engraved on the new stone.

# txt = "125 17"
txt = "572556 22 0 528 4679021 1 10725 2790"
stones = list(map(int, txt.split(" ")))
print(stones)

# calculate how many stones you have after splitting a single stone n times
@cache
def split_stone(stone, n):
    if n == 0:
        return 1
    if stone == 0:
        return split_stone(1, n - 1)
    elif len(str(stone)) % 2 == 0:
        txt = str(stone)
        half = len(txt) // 2
        return split_stone(int(txt[:half]), n - 1) + split_stone(int(txt[half:]), n - 1)
    else:
        return split_stone(stone * 2024, n - 1)

part1 = sum([split_stone(stone, 25) for stone in stones])
part2 = sum([split_stone(stone, 75) for stone in stones])

print("part1:", part1) # 228688
print("part2:", part2) # 270673834779359
