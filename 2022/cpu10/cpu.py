#
# Start by figuring out the signal being sent by the CPU. The CPU has a single register, X,
# which starts with the value 1. It supports only two instructions:
#
#    addx V takes two cycles to complete. After two cycles, the X register is increased by the value V. (V can be negative.)
#    noop takes one cycle to complete. It has no other effect.
#
# The CPU uses these instructions in a program (your puzzle input) to, somehow, tell the screen what to draw.
#
# Consider the following small program:
#   noop
#   addx 3
#   addx -5
#
# Execution of this program proceeds as follows:
#    At the start of the first cycle, the noop instruction begins execution. During the first cycle, X is 1.
#    After the first cycle, the noop instruction finishes execution, doing nothing.
#    At the start of the second cycle, the addx 3 instruction begins execution. During the second cycle, X is still 1.
#    During the third cycle, X is still 1. After the third cycle, the addx 3 instruction finishes execution, setting X to 4.
#    At the start of the fourth cycle, the addx -5 instruction begins execution. During the fourth cycle, X is still 4.
#    During the fifth cycle, X is still 4. After the fifth cycle, the addx -5 instruction finishes execution, setting X to -1.
#
#  Values of X after completion of the cycles
#    1: 1
#    2: 1
#    3: 4
#    4: 4
#    5: -1

# Solution: we view the input as assembly language for an accumulator.
# The assembly language is "translated" into codes for the accumulator, each instruction takes one cycle.
# The accumulator simply adds the codes.
# noop is translated to 0
# addx Y is translated to the sequence 0, Y

# The accumulator is initialized by the first value, namely 1. For the purpose of the puzzle we add a
# zero to the list of codes, so that the index of the trace equals "middle of the cycle number" which is
# the same as end of cycle number cycle - 1
#
# assembler: addx 15; addx -11;
# trace:     [0, 1, 1, 16, 16, ...]
#
# trace[0]  not used
#           cycle 1 begins, X = 1
#           begin executing addx 15, X = 1
# trace[1]  middle of cycle 1, X = 1
#           end of cycle 1, X = 1
#           begin of cycle 1, X = 1
# trace[2]  middle of cycle 2, X = 1
#           end executing addx 15
#           end of cycle 2, X = 16
#           begin of cycle 3, X = 16
# trace[3]  middle of cycle 3, X = 16
#
# As a small hack to ease the translation, we define noop as 0 and addx as zero, and treat the assembly instructions
# (the input) as a sequence of commands and arguments alike. For example, the program "noop; addx 3; addx -5" becomes
# [noop, addx, -5, noop] which in turns becomes [0, 0, -5, 0]. Since each code takes one cycle, we very conveniently
# achieve noop taking 1 cycle and addx taking 2.

from itertools import accumulate

# Dirty
noop = 0
addx = 0
# Dirty indeed
trace = list(accumulate([0,1] + list(map(eval, open("big.in").read().strip().split()))))
print("big.in     ", sum([ i * trace[i] for i in [20, 60, 100, 140, 180, 220] ]))
print()

with open("small.in") as file:
    assembler = file.read().strip().split()
    accumulator = [0, 1] + list(map(eval, assembler))
    trace = list(accumulate(accumulator))
    result = sum( [i * trace[i] for i in range(20, len(trace), 20) ] )
    print("assembler  ", assembler)
    print("accumulator", accumulator)
    print("trace      ", trace)
    print("small.in   ", result)

with open("big.in") as file:
    assembler = file.read().strip().split()
    accumulator = [0, 1] + list(map(eval, assembler))
    trace = list(accumulate(accumulator))
    result = sum([i * trace[i] for i in [20, 60, 100, 140, 180, 220]])
    print()
    print("assembler  ", assembler)
    print("accumulator", accumulator)
    print("trace      ", trace)
    print("big.in     ", result)

# result small.in: 31140
# result big.in:   14220