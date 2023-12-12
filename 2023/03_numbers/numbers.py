from utils import Map, flatten
from collections import defaultdict
import sys

foo = Map("big.in")

valid = set(flatten([ foo.get_neighbours((row, col), diagonal=True)
                      for ((row, col), value) in foo.all()
                      if value != '.' and not value.isdigit() ]))

def is_new_line(row, col):
    return (row != 0) and (col == 0)

(number, ok, result ) = (0, False, 0)
for ((row, col), value) in foo.all():
    if value.isdigit() and not is_new_line(row, col):
        (number, ok, result) = (number * 10 + int(value), ok or ((row, col) in valid), result)
    else:
        (number, ok, result) = (0, False, result + (number if ok else 0))

print("part1", result) # 520019

# argh, man har set pænere kode, men nok er nok
numbers = defaultdict(lambda: set())
number = 0
coords = set()
for ((row, col), value) in foo.all():
    if value.isdigit() and not is_new_line(row, col):
        number = number * 10 + int(value)
        coords.append((row, col))
    else:
        [ numbers[(row2, col2)].add(((row2, col2), number)) for (row1, col1) in coords for (row2, col2) in foo.get_neighbours((row1, col1), diagonal=True) ]
        number = 0
        coords = []

part2 = sum([ n[0][1] * n[1][1]
              for n in [tuple(numbers[(row, col)])
                        for ((row, col), value) in foo.all()
                        if value == "*"]
              if len(n) == 2 ])

print("part2", part2) # 75519888
