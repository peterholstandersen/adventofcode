elves = []
total = 0

for line in open("big.in"):
    line = line.strip()
    if line == "":
        elves.append(total)
        total = 0
    else:
        total += int(line)

elves.sort(reverse=True)

print(elves)
print(elves[0] + elves[1] + elves[2])

# 70116, 68706, 67760, 67516, 66882, ...