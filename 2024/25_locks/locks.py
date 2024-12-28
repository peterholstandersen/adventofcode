import sys

file = "small.in"
file = "big.in"

text = open(file).read().strip().replace("#", "1").replace(".", "0").split("\n\n")
locks_and_keys = [int(xxx.replace("\n", ""), 2) for xxx in text]
print(len(locks_and_keys))
locks = list(filter(lambda x: x % 2 == 0, locks_and_keys))
keys = list(filter(lambda x: x % 2 != 0, locks_and_keys))
part1 = [(lock, key) for lock in locks for key in keys if lock & key == 0]
print("part1:", len(part1))
sys.exit(1)

# need to solve other puzzles to do part 2