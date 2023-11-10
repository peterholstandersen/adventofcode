import sys
from collections import Counter

def read_file(filename):
    (polymer, rules) = open(filename).read().strip().split("\n\n")
    rules = {rule[:2]: rule[-1] for rule in rules.split("\n")}
    return (polymer, rules)

# Insert new letters between each letter in the polymer according to the rules
def evolve(polymer, rules):
    if len(polymer) <= 1:
        return polymer
    return polymer[0] + rules.get(polymer[:2], "") + evolve(polymer[1:], rules)

# The result is the number of most common letter minus the number of the least common after 10 rounds
def part1(filename, expected):
    (polymer, rules) = read_file(filename)
    for _ in range(10):
        polymer = evolve(polymer, rules)
    c = Counter(polymer)
    most = c.most_common()
    result = most[0][1] - most[-1][1]
    print("part1", filename, result)
    assert(result == expected)

# The result is the number of most common letter minus the number of the least common after 40 rounds
def part2(filename, expected):
    # As it is practically impossible to keep the entire polymer in memory after 40 rounds, we count
    # the number of pairs in the polymer instead, as we are only interested in knowning the count of
    # each letter and not the order. It works, because the transformation of a pair is independent of
    # the rest of the polymer. After the transformation, we count the pairs again and start over.
    (polymer, rules) = read_file(filename)
    counter = Counter()
    counter.update([polymer[i:i+2] for i in range(len(polymer) - 1)])
    for _ in range(40):
        new_elements = counter.copy()
        # The polymer contains N = counter[XY] pairs for each XY pair.
        # Using the rule XY -> Z, it is turned into XZY corresponding to the two pairs XZ and ZY.
        # The old pairs no longer appear in the polymer. Others may be created from other rules, but
        # these particular instances are gone. Therefore, we reduce the count of the old pair with N,
        # and increase the count of XZ and ZY with N each.
        for pp in counter:
            new_elements[pp] -= counter[pp]
            new_elements[pp[0] + rules[pp]] += counter[pp]
            new_elements[rules[pp] + pp[1]] += counter[pp]
        counter = new_elements
    # We are done: Create a new counter with only the first letter of each pair. This covers all
    # letters except the very last. The last letter is always the same as the last of the starting
    # polymer.
    letters = Counter()
    for (pp, y) in counter.most_common():
        letters[pp[0][0]] += y
    letters[polymer[-1]] += 1
    most = letters.most_common()
    result = most[0][1] - most[-1][1]
    print("part2", filename, result)
    assert(result == expected)

if __name__ == "__main__":
    sys.setrecursionlimit(10000)
    part1("small.in", 1588)
    part1("big.in", 2874)
    part2("small.in", 2188189693529)
    part2("big.in", 5208377027195)