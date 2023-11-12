# Python rounds to the nearest _even_ number
# That is, round(2.5) rounds to 2 and round(3.5) rounds to 4, wtf!
#
#  First shalt thou take out the Holy Pin. Then shalt thou count to three, no more, no less. Three shall be the
#  number thou shalt count, and the number of the counting shall be three. Four shalt thou not count, neither
#  count thou two, excepting that thou then proceed to three. Five is right out. Once the number three, being
#  the third number, be reached, then lobbest thou thy Holy Hand Grenade of Antioch towards thy foe, who, being
#  naughty in My sight, shall snuff it.

mid = lambda x, y: int(round((x + y + 0.00001) / 2))

F = lambda x: (x[0], mid(x[0], x[1]), x[2], x[3])
B = lambda x: (mid(x[0], x[1]), x[1], x[2], x[3])
L = lambda x: (x[0], x[1], x[2], mid(x[2], x[3]))
R = lambda x: (x[0], x[1], mid(x[2], x[3]), x[3])

lines = open("big.in").read().split("\n")
part1 = 0
ids = { row * 8 + seat for row in range(0, 128) for seat in range(0, 8) }

for line in lines:
    x = (0, 127, 0, 7)
    for f in line:
        x = eval(f)(x)
    seat_id = x[0] * 8 + x[2]
    part1 = max(part1, seat_id)
    ids.remove(seat_id)

print("part1", part1)  # 998
print("part2", { x for x in ids if (x+1) not in ids and (x-1) not in ids }.pop()) # 676

