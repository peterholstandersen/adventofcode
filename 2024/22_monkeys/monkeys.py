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

# changes_to_price is mapping from a 4-tuple representing the 4 most recent price changes to the price
def get_changes_to_price(n, count_changes):
    prices = [n % 10]
    for _ in range(3, 2000):
        n = get_next_number(n)
        prices.append(n % 10)
    changes = [(y - x) for (x, y) in zip(prices, prices[1:])]  # 1 sec

    # Make a mapping from each 4-tuple of price changes to the price
    changes_to_price = dict()
    for i in range(0, len(changes) - 3):
        change = (changes[i], changes[i+1], changes[i+2], changes[i+3])
        if change not in changes_to_price:
            changes_to_price[change] = prices[i + 4]
            if change not in count_changes:
                count_changes[change] = 1
            else:
                count_changes[change] += 1
    return changes_to_price

def do_part2():
    # numbers = [1, 2, 3, 2024]
    count_changes = dict()
    with Timer():  # 6.8 sec
        # list of mappings from change to price
        all_changes_to_price = [get_changes_to_price(n, count_changes) for n in numbers]
    print(all_changes_to_price[:1])
    most_common_changes = sorted(count_changes.items(), key=lambda x: x[1], reverse=True) # <0.1 sec

    with Timer(): # 1.4 sec
        best_change = None
        max_result = -1
        for (change, change_count) in most_common_changes:
            if change_count * 9 < max_result:
                print("limit")
                break
            result = sum([changes_to_price[change] for changes_to_price in all_changes_to_price if change in changes_to_price])
            if result > max_result:
                print("better:", result)
                max_result = result
                best_change = change
        print("result:", max_result, "best_change:", best_change)

do_part2() # 2362,  (-2, 1, -1, 2)
