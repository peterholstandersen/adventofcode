from collections import Counter

# part1: sum of the number of answers anyone answered. Amounts to finding all the unique letters in a group (and disregard newline)
# part2: sum of the number of answers everone answered. Amounts to finding the letters that appears in every line of a group
# The number of persons in a group equals counter["\n"] + 1 (there is no trailing newline)

groups = open("big.in").read().split("\n\n")

counters = [Counter(group) for group in groups]
part1 = sum([len(counter.keys() - "\n") for counter in counters])
part2 = len([x for counter in counters for (x, y) in counter.most_common() if y == counter["\n"] + 1])

print("part1", part1) # 6437
print("part2", part2) # 3229