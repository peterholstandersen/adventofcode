import sys
from collections import Counter

# part1: Sort ascending, sum difference between each element
# 3   4
# 4   3
# 2   5
# 1   3
# 3   9
# 3   3
#
# part2: sum of [ each number in the left list: multiply the number with list2.count(number) ]

# file = "small.in"
file = "big.in"
numbers = [line.strip().split("  ") for line in open(file).read().strip().split("\n")]

list1 = sorted([int(x) for (x,_) in numbers])
list2 = sorted([int(y) for (_,y) in numbers])
part1 = sum([abs(x - y) for (x, y) in zip(list1, list2)])

counter = Counter(list2)
part2 = sum([counter[number] * number for number in list1])

print("part1:", part1) # 1660292
print("part2:", part2) # 22776016