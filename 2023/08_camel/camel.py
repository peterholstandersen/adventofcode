import os
import sys
from itertools import cycle
from functools import reduce
from math import lcm

[dirr, des] = open("big.in").read().strip().split("\n\n")
directions = cycle(dirr.strip())
desert = des.strip().replace(" = ", " = lambda dir: ").replace(")", ")[dir]")

L = 0
R = 1

exec(desert)

location = AAA
steps = 0
while location != ZZZ:
    location = location(eval(next(directions)))
    steps += 1
print(steps) # 21251

starts = [ eval(line[:3]) for line in des.split("\n") if line[2] == "A"]
ends = [ eval(line[:3]) for line in des.split("\n") if line[2] == "Z"]

# For the given input file (big.in) apparently it is the case, that:
#
# For each start position in starts, it turns out to be the case that the number of steps to reach an
# end position is the same as reaching an end position the next time again (and henceforth). Also, it
# is the _same_ end position every time _and_ each start position reaches different end positions.
# So there is a distinct loop for each start position, with only one end position in the loop.
#
# For the given input file, the cycle length of each cycle is a multipla of the number of directions
# (the first line) in the input file, i.e., 269 in this case. It needn't be, but as it happens, it is.
#
# It is probably something to do with how the puzzle data was generated. Anyway, the result produced
# below is accepted as the correct answer to the puzzle, so that's all, folks!

cycle_lengths = []
for location in starts:
    directions = cycle(dirr.strip())
    steps = 0
    times = 3 # not necessary for the given input, but interesting to see the number of steps for more than one cycle
    while times > 0:
        location = location(eval(next(directions)))
        steps += 1
        if location in ends:
            times = times - 1
            print(steps, lcm(269, steps))
            cycle_lengths.append(steps)
            steps = 0
print(cycle_lengths)

# 269: length of directions
x = reduce(lambda x,y: lcm(x,y), cycle_lengths)
print(x) # 11678319315857
print(lcm(x, 269))
