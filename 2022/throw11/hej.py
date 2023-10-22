# This file is generated

monkeys = [
    [57, 58],
    [66, 52, 59, 79, 94, 73],
    [80],
    [82, 81, 68, 66, 71, 83, 75, 97],
    [55, 52, 67, 70, 69, 94, 90],
    [69, 85, 89, 91],
    [75, 53, 73, 52, 75],
    [94, 60, 79],
]
inspect = [0] * 8
def one_round():
    while len(monkeys[0]) > 0:
        old = monkeys[0].pop(0)
        inspect[0] += 1
        new = old * 19
        new = new % (7 * 19 * 5 * 11 * 17 * 13 * 2 * 3)
        test = (new % 7 == 0)
        if test: monkeys[2].append(new)
        if not test: monkeys[3].append(new)
    while len(monkeys[1]) > 0:
        old = monkeys[1].pop(0)
        inspect[1] += 1
        new = old + 1
        new = new % (7 * 19 * 5 * 11 * 17 * 13 * 2 * 3)
        test = (new % 19 == 0)
        if test: monkeys[4].append(new)
        if not test: monkeys[6].append(new)
    while len(monkeys[2]) > 0:
        old = monkeys[2].pop(0)
        inspect[2] += 1
        new = old + 6
        new = new % (7 * 19 * 5 * 11 * 17 * 13 * 2 * 3)
        test = (new % 5 == 0)
        if test: monkeys[7].append(new)
        if not test: monkeys[5].append(new)
    while len(monkeys[3]) > 0:
        old = monkeys[3].pop(0)
        inspect[3] += 1
        new = old + 5
        new = new % (7 * 19 * 5 * 11 * 17 * 13 * 2 * 3)
        test = (new % 11 == 0)
        if test: monkeys[5].append(new)
        if not test: monkeys[2].append(new)
    while len(monkeys[4]) > 0:
        old = monkeys[4].pop(0)
        inspect[4] += 1
        new = old * old
        new = new % (7 * 19 * 5 * 11 * 17 * 13 * 2 * 3)
        test = (new % 17 == 0)
        if test: monkeys[0].append(new)
        if not test: monkeys[3].append(new)
    while len(monkeys[5]) > 0:
        old = monkeys[5].pop(0)
        inspect[5] += 1
        new = old + 7
        new = new % (7 * 19 * 5 * 11 * 17 * 13 * 2 * 3)
        test = (new % 13 == 0)
        if test: monkeys[1].append(new)
        if not test: monkeys[7].append(new)
    while len(monkeys[6]) > 0:
        old = monkeys[6].pop(0)
        inspect[6] += 1
        new = old * 7
        new = new % (7 * 19 * 5 * 11 * 17 * 13 * 2 * 3)
        test = (new % 2 == 0)
        if test: monkeys[0].append(new)
        if not test: monkeys[4].append(new)
    while len(monkeys[7]) > 0:
        old = monkeys[7].pop(0)
        inspect[7] += 1
        new = old + 2
        new = new % (7 * 19 * 5 * 11 * 17 * 13 * 2 * 3)
        test = (new % 3 == 0)
        if test: monkeys[1].append(new)
        if not test: monkeys[6].append(new)
for _ in range(0, 10000):
    one_round()
print(inspect)
