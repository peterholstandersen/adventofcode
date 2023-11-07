# https://adventofcode.com/2021/day/6
#
# fish have an internal timer (0-8) that counts down each round, when it reaches 0,
# it is reset to 6 and a new fish is spawned with timer 8.

#dataset = "small.in"; xs = list(map(int, "3,4,3,1,2".split(","))); part1 = 5934; part2 = 26984457539
dataset = "big.in"; xs = list(map(int, open(dataset).read().strip().split(","))); part1 = 362740; part2 = 1644874076764
xs_copy = xs.copy()
for i in range(80):
    xs = [x - 1 if x != 0 else 6 for x in xs] + [8] * xs.count(0)
print("part1", dataset, len(xs), "fishseses")
assert(len(xs) == part1)

# instead of representing fish as one element per fish in a list as above, we keep a count of the number
# fish for each timer value, so that fish[timer_value] = N. That is, we have N fish with time_valuer.
#
# Subtracting one from all timer values is a matter of shifting the list down: Thus, the new fish counters
# are fish[1:]. For N = fish[0], we need to add N to fish[6] and fish[8] in the new list as the timer is
# reset to 6 when it reaches 0 and new fish with timer 8 are spawned.

xs = xs_copy
fish = [xs.count(n) for n in range(9)]
for i in range(256):
    fish = fish[1:7] + [ fish[7] + fish[0], fish[8], fish[0] ]
print("part2", dataset, sum(fish), "fishseses")
assert(sum(fish) == part2)