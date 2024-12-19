import sys
import re

if False:
    for y in range(0, 103):
        count = 0
        blah = y * 2 + 1
        count += blah
        print("." * ((103 - blah) // 2) + "*" * blah + "." * ((103 - blah) // 2))
        if count > 500:
            print(y)
            break

# p=10,3 v=-1,2

# (file, width, height) = ("small.in", 11, 7)
(file, width, height) = ("big.in", 101, 103)
all_numbers = list(map(int, re.findall(r"[\-\d]+", open(file).read())))
# print(all_numbers)

# (x, y, dx, dy)
robots = [tuple(all_numbers[n : n + 4]) for n in range(0, len(all_numbers), 4)]
# print(robots)

seconds = 100

at_100 = [((x + dx * seconds) % width, (y + dy * seconds) % height) for (x, y, dx, dy) in robots]

quad1 = len([(x, y) for (x, y) in at_100 if x < width // 2 and y < height // 2])
quad2 = len([(x, y) for (x, y) in at_100 if x > width // 2 and y < height // 2])
quad3 = len([(x, y) for (x, y) in at_100 if x < width // 2 and y > height // 2])
quad4 = len([(x, y) for (x, y) in at_100 if x > width // 2 and y > height // 2])

print(quad1, quad2, quad3, quad4)
print("part1:", quad1 * quad2 * quad3 * quad4) # 229839456

def print_it(robots, width, height):
    top = "\u001b[0;0H"
    #print(top)
    print("============")
    out = ""
    for y in range(0, width):
        for x in range(0, height):
            if (x, y) in robots:
                out += "*"
            else:
                out += "."
        out += "\n"
    print(out)

seconds = 7138
xxx = [((x + dx * seconds) % width, (y + dy * seconds) % height) for (x, y, dx, dy) in robots]
print_it(xxx, width, height)
sys.exit(1)

seconds = 183989
midx = width // 2
midy = height // 2
n = 20
while seconds > 0:
    seconds -= 10403
    if seconds < 0:
        break
    xxx = [((x + dx * seconds) % width, (y + dy * seconds) % height) for (x, y, dx, dy) in robots]
    count = len([(x, y) for (x, y) in xxx if midx - n < x < midx + n and midy - n < y < midy + n])
    if count < n * n // 2 - 100:
        continue
    print_it(xxx, width, height)

print(seconds)
    # x = input()

# 7138 ... bleh