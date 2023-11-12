# 8-10 g: cggggggvgcg
lines = open("big.in").read().strip().replace("-", " ").replace(":", "").split("\n")
part1 = 0
part2 = 0
for line in lines:
    (low, high, letter, text) = line.split(" ")
    low = int(low)
    high = int(high)
    part1 = part1 + (1 if low <= text.count(letter) <= high else 0)
    part2 = part2 + (1 if (text[low - 1] == letter) ^ (text[high - 1] == letter) else 0)
print("part1", part1)  # 607
print("part2", part2)  # 321

sp = [(int(low), int(high), letter, text, text.count(letter)) for (low, high, letter, text) in [line.split(" ") for line in lines]]
print("part1", len([0 for (low, high, _, _, count) in sp if low <= count <= high]))
print("part2", len([0 for (low, high, letter, text, _) in sp if (text[low-1] == letter) ^ (text[high-1] == letter)]))