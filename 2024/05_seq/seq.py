import sys

import itertools

# file = "small.in"
file = "big.in"
(rules, seqs) = open(file).read().strip().split("\n\n")
seqs = [x.split(",") for x in seqs.split("\n")]

is_valid = lambda seq: all([ f"{seq[page1]}|{seq[page2]}" not in rules
                                  for page1 in range(len(seq) - 1, -1, -1)
                                  for page2 in range(0, page1)])

middle_number = lambda xs: int(xs[len(xs) // 2])
part1 = sum([middle_number(seq) for seq in seqs if is_valid(seq)])
# part1 = sum_middle_number(seqs)

def find_valid_page(orig_seq, fixed_seq, rules):
    invalid_pages = [after for (before, after) in rules if before not in fixed_seq and before in orig_seq]
    pages = [page for page in orig_seq if page not in fixed_seq and page not in invalid_pages]
    if len(pages) == 0:
        print("uh oh, cannot find a valid page")
        sys.exit(1)
    if len(pages) > 1:
        print("uh oh, several valid pages", pages)
        sys.exit(1)
    return pages[0]

rules_as_pairs = [ tuple(rule.split("|")) for rule in rules.split("\n") ]

fixed_seqs = set()
for seq in seqs:
    if is_valid(seq):
        continue
    fixed = []
    while len(fixed) < len(seq):
        fixed.append(find_valid_page(seq, fixed, rules_as_pairs))
    fixed_seqs.add((tuple(seq), tuple(fixed)))

part2 = sum([middle_number(seq) for (_, seq) in fixed_seqs])

print("part1:", part1) # 5129
print("part2:", part2) # 4077
