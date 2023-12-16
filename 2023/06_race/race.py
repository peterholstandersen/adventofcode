import re

small_in =\
"""
Time:      7  15   30
Distance:  9  40  200
"""

big_in =\
"""
Time:        60     94     78     82
Distance:   475   2138   1015   1650
"""

spec = big_in

# part2
# spec = spec.replace(" ", "")

numbers = list(map(int, re.findall(r"\d+", spec)))
half = len(numbers) // 2
races = zip(numbers[0:half], numbers[half:])

result = 1
for (time, distance_to_beat) in races:
    wins = 0
    # brute force
    for speed in range(1, time):
        distance = (time - speed) * speed
        if distance > distance_to_beat:
            wins += 1
    result = result * wins
print(result) # part1: 345015

# part2: 42588603
