from itertools import combinations

numbers = sorted(list(map(int, open("big.in").read().split("\n"))))
ups = [(x, y, z, x + y + z) for (x, y, z) in combinations(numbers, 3) if x + y + z == 2020]
print(ups, ups[0][0] * ups[0][1] * ups[0][2])