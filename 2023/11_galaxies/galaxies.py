from utils import Map
from itertools import combinations

mapp = Map("big.in")
rows = [ row for row in mapp.rows if all([x == "." for col in mapp.cols for x in mapp[(row, col)]]) ]
cols = [ col for col in mapp.cols if all([x == "." for row in mapp.rows for x in mapp[(row, col)]]) ]
galaxies = [pos for (pos, value) in mapp.all() if value == "#"]

def distance(g1, g2, rows, cols, age=1):
    (r1, c1) = g1
    (r2, c2) = g2
    if r2 < r1:
        (r1, r2) = (r2, r1)
    if c2 < c1:
        (c1, c2) = (c2, c1)
    extra = len([1 for rr in rows if r1 < rr < r2]) + len([1 for cc in cols if c1 < cc < c2])
    return (r2 - r1) + (c2 - c1) + extra * age

part1 = sum([distance(g1, g2, rows, cols) for (g1, g2) in combinations(galaxies, 2)])
part2 = sum([distance(g1, g2, rows, cols, 999999) for (g1, g2) in combinations(galaxies, 2)])
print("part1", part1)
print("part2", part2)
