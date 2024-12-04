import sys
import re

# part1: only mul(x,y) where x and y are 1-3 digit numbers ... and sum them

# text = "xmul(2,4)%&mul[3,7]!@^do_not_mul(5,5)+mul(32,64]then(mul(11,8)mul(8,5))" # part1 example
# text = "xmul(2,4)&mul[3,7]!^don't()_mul(5,5)+mul(32,64](mul(11,8)undo()?mul(8,5))" # part2 example

file = "big.in"
text = open(file).read().strip()

pattern = re.compile(r"mul\(\d\d?\d?,\d\d?\d?\)")
mul = lambda x, y: x * y
part1 = sum([eval(op) for op in pattern.findall(text)])

pattern2 = re.compile(r"(mul\(\d\d?\d?,\d\d?\d?\))|(do\(\))|(don\'t\(\))")
foo = [x+y+z for (x,y,z) in pattern2.findall(text)]

bleh = 1
part2 = 0
for f in foo:
    match f:
        case "don\'t()": bleh = 0
        case "do()":     bleh = 1
        case _:          part2 += eval(f) * bleh

print("part1:", part1) # 161289189
print("part2:", part2) # 83595109