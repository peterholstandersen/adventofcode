# Opponent
# A: rock
# B: paper
# C: scissors
#
# You
# X: rock
# Y: paper
# Z: scissors

# wins
# C X  =>  C A  =>  6 + A  => 7
# A Y  =>  A B  =>  6 + B  => 8
# B Z  =>  B C  =>  6 + C  => 9

A = 1
B = 2
C = 3

AA = A + 3
AB = B + 6
AC = C

BA = A
BB = B + 3
BC = C + 6

CA = A + 6
CB = B
CC = C + 3

print(sum(map(eval, open("small.in").read().strip().replace(" ", "").replace("X", "A").replace("Y", "B").replace("Z", "C").split("\n"))))
print(sum(map(eval, open("big.in").read().strip().replace(" ", "").replace("X", "A").replace("Y", "B").replace("Z", "C").split("\n"))))

# 15
# 11386