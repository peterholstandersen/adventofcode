import sys
import re

# Button A: X+94, Y+34
# Button B: X+22, Y+67
# Prize: X=8400, Y=5400
#
# say a and b equals a number of presses on button A and B respectively
# so, we want 94a + 22b = 8400
# and         34a + 67b = 5400
# two equations with two unknowns .. go solve
# a = 80, b = 40
#
# according to the puzzle, a and b must be postive integers. In part1, a and b may not exceed 100.

# file = "small.in"
file = "big.in"
all_numbers = list(map(int, re.findall(r"\d+", open(file).read().strip("\n"))))
machines = [all_numbers[n:(n+6)] for n in range(0, len(all_numbers), 6)]

# Button A: X+{N}, Y+{R}
# Button B: X+{M}, Y+{P}
# Prize:    X={K}, Y={Q}
#
# Na + Mb = K     (equation for X)
# Ra + Pb = Q     (equation for Y)
def solve_it(machines, part):
    offset = 0 if part == "part1" else 10000000000000
    max_presses = 100 if part == "part1" else None
    tokens = 0
    for [N, R, M, P, K, Q] in machines:
        K += offset
        Q += offset
        if N == 0 or (P - R*M/N) == 0:
            continue
        b = (Q - R*K/N) / (P - R*M/N)
        a = (K - M*b) / N
        a = int(round(a))
        b = int(round(b))
        if a >= 0 and b >= 0 and N*a + M*b == K and R*a + P*b == Q:
            if max_presses and (a > max_presses or b > max_presses):
                continue
            tokens += 3*a + b
    return tokens

part1 = solve_it(machines, "part1")
part2 = solve_it(machines, "part2")

print("part1:", part1) # 32067
print("part2:", part2) # 92871736253789


# --- naive way of solving part1 ... this is what you get when you forgot to solve two equations with two unknowns!

tokens = 0
for [a_x, a_y, b_x, b_y, prize_x, prize_y] in machines:
    max_b = min(prize_x // b_x, prize_y // b_y, 100)
    for press_b in range(0, max_b + 1):
        (x, y) = (press_b * b_x, press_b * b_y)
        (x1, y1) = (prize_x - x, prize_y - y)
        if x1 >= 0 and y1 >= 0 and x1 % a_x == 0 and y1 % a_y == 0:
            press_a1 = x1 // a_x
            press_a2 = y1 // a_y
            if press_a1 == press_a2 and press_a1 <= 100:
                tokens += press_b + press_a1 * 3
                break

print("part1:", tokens)
