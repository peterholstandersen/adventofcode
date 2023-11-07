import sys
from functools import reduce
from statistics import median

# dataset = "small.in"; crabs = list(map(int, "16,1,2,0,4,2,7,1,2,14".split(","))); part1 = 37; part2 = 168
dataset = "big.in"; crabs = list(map(int, open(dataset).read().strip().split(","))); part1 = 342730; part2 = 92335207

# part 1
med = int(median(crabs))
result = sum([abs(crab - med) for crab in crabs])
print("part1", dataset, med, result)
assert(result == part1)

# part 2
def compute_cost(crabs, target, sums):
    return reduce(lambda total, crab: total + sums[abs(target - crab)], crabs, 0)

low = min(crabs)
high = max(crabs)

# Pre-calculate the needed sums: sums[N] = N + (N-1) + (N-2) + ...
sums = [0] * (high + 1)
for n in range(1, high + 1):
    sums[n] = sums[n-1] + n

result = None
while True:
    cost_low = compute_cost(crabs, low, sums)
    cost_high = compute_cost(crabs, high, sums)
    print(low, high, cost_low, cost_high)
    if high - low <= 1:
        result = cost_low if cost_low < cost_high else cost_high
        break
    mid = round((high - low) / 2)
    if cost_low < cost_high:
        (low, high) = (low, low + mid)
    else:
        (low, high) = (low + mid, high)

print("part2", dataset, result)
assert(result == part2)