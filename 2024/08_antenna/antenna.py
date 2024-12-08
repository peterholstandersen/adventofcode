import sys

# file = "small.in"
file = "big.in"
text = open(file).read().strip("\n")
dim = text.index("\n")
text = text.replace("\n", "")

antennas = [(pos, text[pos]) for pos in range(0, len(text)) if text[pos] != '.']
antenna_pairs = [(pos1, pos2) for (pos1, freq1) in antennas for (pos2, freq2) in antennas if freq1 == freq2 and pos1 != pos2]

to_pos = lambda x, y: x + y * dim if 0 <= x < dim and 0 <= y < dim else None

def get_antinode(pos1, pos2, n=1):
    (x1, y1) = (pos1 % dim, pos1 // dim)
    (x2, y2) = (pos2 % dim, pos2 // dim)
    (dx, dy) = (x2 - x1, y2 - y1)
    return to_pos(x2 + dx * n, y2 + dy * n)

antinodes1 = {get_antinode(pos1, pos2) for (pos1, pos2) in antenna_pairs if get_antinode(pos1, pos2)}
part1 = len(antinodes1)
print("part1:", part1) # 265

def get_antinodes2(pos1, pos2):
    antinodes2 = {get_antinode(pos1, pos2, n) for n in range(0, dim)}
    antinodes2.remove(None)
    return antinodes2

antinodes2 = set().union(*[get_antinodes2(pos1, pos2) for (pos1, pos2) in antenna_pairs])
part2 = len(antinodes2)
print("part2:", part2) # 962
