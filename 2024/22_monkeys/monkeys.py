import sys
from utils import Timer

# file = "small.in"
file = "big.in"

numbers = list(map(int, open(file)))
# print(numbers)

# Calculate the result of multiplying the secret number by 64. Then, mix this result into the secret number. Finally, prune the secret number.
# Calculate the result of dividing the secret number by 32. Round the result down to the nearest integer. Then, mix this result into the secret number. Finally, prune the secret number.
# Calculate the result of multiplying the secret number by 2048. Then, mix this result into the secret number. Finally, prune the secret number.
#
# Each step of the above process involves mixing and pruning:
# - To mix a value into the secret number, calculate the bitwise XOR of the given value and the secret number. Then, the secret number becomes the result of that operation. (If the secret number is 42 and you were to mix 15 into the secret number, the secret number would become 37.)
# - To prune the secret number, calculate the value of the secret number modulo 16777216. Then, the secret number becomes the result of that operation. (If the secret number is 100000000 and you were to prune the secret number, the secret number would become 16113920.)

def get_next_number(x):
    x = (x ^ (x * 64)) % 16777216
    x = (x ^ (x // 32)) % 16777216
    x = (x ^ (x * 2048)) % 16777216
    return x

def do_part1():
    result = 0
    for n in numbers:
        for _ in range(0, 2000):
            n = get_next_number(n)
        result += n
    print("part1:", result)  # 20411980517

do_part1()

best_change = None
best_result = -1

def do_one_sequence(n, result):
    global best_change, best_result
    prices = [n % 10]
    for _ in range(3, 2000):
        n = get_next_number(n)
        prices.append(n % 10)
    changes = [(y - x) for (x, y) in zip(prices, prices[1:])]  # 1 sec

    seen_before = set()
    for i in range(0, len(changes) - 3):
        change = (changes[i], changes[i+1], changes[i+2], changes[i+3])
        if change not in seen_before:
            seen_before.add(change)
            if change not in result:
                result[change] = prices[i + 4]
            else:
                result[change] += prices[i + 4]
            if result[change] > best_result:
                best_change = change
                best_result = result[change]
    return

def do_part2():
    global best_change, best_result
    # numbers = [1, 2, 3, 2024]
    result = dict()
    with Timer():  # 6.5 sec
        for n in numbers:
            do_one_sequence(n, result)
    print(best_change, best_result)

do_part2() # 2362,  (-2, 1, -1, 2)
