import sys
import re
from itertools import product

dam = lambda n: int(re.findall(r"\d+", n)[0])
crit = lambda n: n[-1] if n[-1] in "ABCDEFGHIJKL" else ""

def read_it():
    roll_from = lambda roll: int(roll.split("-")[0])
    roll_to = lambda roll: int(roll.split("-")[1])
    filename = "./warhead_attack_table.txt"
    with open(filename) as f:
        xs = [line.strip().split("\t") for line in f if "-" in line and "F" not in line]
    ys = [ (roll_from(roll), roll_to(roll), (dam(n1), crit(n1)), (dam(n2), crit(n2)), (dam(n3), crit(n3)), (dam(n4), crit(n4)), (dam(n5), crit(n5))) for (roll, n1, n2, n3, n4, n5) in xs ]
    return ys

ys = read_it()

maks = { "TCH": "10E 10E 12E 16E 16E",
         "GZ":  "10E 10E 12E 16E 16E",
       }
#max_damage = { (AT20, TCH): "10E", (AT20, GZ): "10E", }  # etc


# print(ys)

# 	   20	16	11	6	2
# 01-02	F	F	F	F	F
# 03-30	0	0	0	0	0
# 31-33	0	0	0	0	1

def print_table(ys):
    out = ""
    for (x, y, (n1, c1), (n2, c2), (n3, c3), (n4, c4), (n5, c5)) in ys:
        out += f"{x:02}-{y}\t{n1}{c1}\t{n2}{c2}\t{n3}{c3}\t{n4}{c4}\t{n5}{c5}\n"
    print(out)

at16 = [ (x, y, nc1) for (x, y, nc1, nc2, nc3, nc4, nc5) in ys]
print(at16)

mk = 5
#         Opponent DB: -30,
#         Mk5: +25, tch: +35, gz: +40, 2nd: +30, 3rd: +20, 4th: +10, 5th: 0,
#         half hard (-50)                     full hard (-100)
#         tch,    gz,    2,    3,   4,   5    tch,    gz,    2,    3,   4,    5
armour_db = 30
mk_bonus = mk * 5
blast_radii = (75, 40, 30, 20, 10, 0)
max_radii   = ("10E", "10E", "5B", "3A", "3", "1")
half_hard = tuple(map(lambda x: x - 50, blast_radii))
full_hard = tuple(map(lambda x: x - 100, blast_radii))
mods = blast_radii + half_hard + full_hard
mods = tuple(map(lambda x: x + mk_bonus - armour_db, mods))
print(mods)
#mods = (   70,   -10,  -20,  -30, -40, -50,   +25,   -60,  -70,  -80, -90, -100)
maxx = max_radii + max_radii + max_radii
maxx = [(dam(x), crit(x)) for x in maxx]

(AT20, AT16, AT11, AT6, AT2) = (0, 1, 2, 3, 4)
(TCH, GZ, BR2, BR3, BR4, BR5) = (0, 1, 2, 3, 4, 5)

armour_types = (AT20, AT16, AT11, AT6, AT2)
blast_radii  = (TCH, GZ, BR2, BR3, BR4, BR5)
blast_radius_bonus = { TCH: 75, GZ: 40, BR2: 30, BR3: 20, BR4: 10, BR5: 0}
godmock = [ (armour_type, blast_radius_bonus[blast_radius] + mk_bonus - armour_db) for (armour_type, blast_radius) in product(armour_types, blast_radii) ]
print(godmock) # TODO: add seperators




# print(len("ROLL    AT20                     AT16                     AT11                     AT6                      AT2                      ROLL")) # 137

print()
print(f"Armour DB: -{armour_db},  Half Soft: -20, Full Soft: -40, Half Hard: -50, Full Hard: -100")
print(f"Mk{mk}: +{mk_bonus}, Touching: +35, Ground Zero: +40, 2nd: +30, 3rd: +20, 4th: +10, 5th: 0")
print("ROLL    AT20                     AT16                     AT11                     AT6                      AT2                      ROLL")

print("        TCH  GZ   2   3   4   5  TCH  GZ   2   3   4   5  TCH  GZ   2   3   4   5  TCH  GZ   2   3   4   5  TCH  GZ   2   3   4   5")
print("        +70 +35 +25 +15  +5  -5  +70 +35 +25 +15  +5  -5  +70 +35 +25 +15  +5  -5  +70 +35 +25 +15  +5  -5  +70 +35 +25 +15  +5  -5")
print("MAX     50E 50E 25A  10   5   0  50E 50E 25B 15A  15   5  ...")


sys.exit(1)

min_roll = 3
max_roll = 150 - min(mods)

def get_entry(roll, table, max_entry):
    if roll < table[0][0]:
        entry = (0, "")
    elif roll > table[-1][0]:  # >last
        entry = table[-1][2]
    else:
        for (x, y, entry) in table:
            if x <= roll <= y:
                entry = entry
                break
    (max_dam, max_crit) = max_entry
    (damm, critt) = entry
    if damm > max_dam or critt > max_crit:
        entry = max_entry
    return (entry[0] * mk, entry[1])

table = []
for roll in range(min_roll, max_roll + 1):
    table.append(([roll, roll] + [get_entry(roll + modifier, at16, max_entry) for (modifier, max_entry) in zip(mods, maxx)]))

def print_table2(table):
    out = ""
    for entry in table:
        x = entry[0]
        y = entry[1]
        rest = entry[2:]
        max_dam = max([n for (n, _) in rest])
        if max_dam == 0:
            continue
        xxx = [f"{n if n > 0 else "-"}{c}" for (n, c) in rest]
        xxx = [f"{x:>3}" for x in xxx]
        hop = f"{x:02}" + "-" + f"{y:02}"
        out += f"{hop:<8}" + " ".join(xxx) + "\n"
    print("Opponent DB: -30")
    print("Mk5: +25, tch: +35, gz: +40, 2nd: +30, 3rd: +20, 4th: +10, 5th: 0")
    #      186-188 50E 50E 25B 15A  15   5 50E 50E 25B 15A  15   5 50E  10  10   5   5   -
    #print("        No cover                Half Hard               Full Hard")
    #print("        TCH  GZ   2   3   4   5 TCH  GZ   2   3   4   5 TCH  GZ  2   3   4   5 ")

    print("        AT20                    AT16                    AT11                    AT6                     AT2")
    print("        TCH  GZ   2   3   4   5 TCH  GZ   2   3   4   5 TCH  GZ  2   3   4   5  TCH  GZ  2   3   4   5  TCH  GZ  2   3   4   5")
    print(out)
    print(out.count("\n"), "lines")



def compress_table(table):
    table2 = []
    i = 0
    while i < len(table):
        from_roll = table[i][0]
        to_roll = table[i][1]
        rest = table[i][2:]
        i = i + 1
        while i < len(table) and table[i][2:] == rest:
            to_roll = table[i][1]
            i = i + 1
        table2.append([from_roll, to_roll] + rest)
    return table2

table2 = compress_table(table)
print_table2(table2)

