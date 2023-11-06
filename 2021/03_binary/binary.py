
# https://adventofcode.com/2021/day/3
#
# 00100
# 11110
# 10110
# 10111
#
# part 1:
# gamma = most common bits in positions 1, 2, 3, 4, 5: 10110
# episilon = bit-wise not of gamma
# The binary not operator (~) in python works on signed numbers, so it will return a negative number,
# which is not what we need. Instead, we xor with 11111.
#
# part2:
# repeat for each position until there is one number left (this is our oxygen generator rating)
#   only keep numbers with the most common bit at the position
# start over with all numbers
# repeat for each position until there is one number left (this is our CO2 scrubber rating)
#   only keep numbers with the least common bit at the position

def part1(filename, result):                                            # Example:
    xss = open(filename).read().strip().split("\n")                     # [00100, 11110, 10110, 10111]
    wordsize = len(xss[0])                                              # 5
    words = len(xss)                                                    # 4
    snip = [[xs[n] for xs in xss] for n in range(wordsize)]             # transpose the input: [0111, 0100, 1111, 0111, 0001]
    snap = ['0' if xs.count('0') > words // 2 else '1' for xs in snip]  # find the most common bit: [1, 0, 1, 1, 0]
    gamma = int("".join(snap), 2)                                       # 10110 = 22
    epsilon = ((2**wordsize) - 1) ^ gamma   # 0b11111 xor gamma         # 01001 =  9
    print(f"part1 {filename} {gamma * epsilon}")
    assert(gamma * epsilon == result)

def foo(xss, select_ones):
    wordsize = len(xss[0])
    for position in range(wordsize):
        ones = [xs for xs in xss if xs[position] == '1']
        xss = ones if select_ones(ones, xss) else [xs for xs in xss if xs[position] == '0']
        if len(xss) == 1:
            break
    return xss

def part2(filename, result):
    xss = open(filename).read().strip().split("\n")
    do = foo(xss.copy(), lambda ones, xss: len(ones) >= len(xss) / 2)  # select ones if they are more or equal of half the xss
    it = foo(xss.copy(), lambda ones, xss: len(ones) < len(xss) / 2)   # select ones if they are less than half of the xss
                                                                       # which is same as select zeros if there are more or equal of the xss
    oxygen = int(do[0], 2)
    co2 = int(it[0], 2)
    print(f"part2 {filename} {oxygen * co2}")
    assert(oxygen * co2 == result)

part1("small.in", 198)
part1("big.in", 4103154)
part2("small.in", 230)
part2("big.in", 4245351)