import sys
import re
from itertools import product

filename = "./warhead_attack_table.txt"
BLAST_RADII = (0, 1, 2, 3, 4)  # not ideal that the index is -1 of blast radius
BLAST_RADIUS_TEXT = ("GrZ", "1st", "2nd", "4rd", "5th")
BLAST_RADIUS_BONUS = (40, 30, 20, 10, 0)
# TOUCHING_BONUS = 35
GRENADE_MK = 5
ARMOUR_DB = 30
MK_BONUS = GRENADE_MK * 5
HALF_SOFT_DB = 20
FULL_SOFT_DB = 40
HALF_HARD_DB = 50
FULL_HARD_DB = 100
ARMOUR_TYPES = (AT20, AT16, AT11, AT6, AT2) = (0, 1, 2, 3, 4) # must match entries in input file
# ARMOUR_TYPE_TEXT = ("A20", "A16", "A11", "AT6", "AT2")
ARMOUR_TYPE_TEXT = ("AT20", "AT16", "AT11", "AT6", "AT2")

def read_entries(filename):
    with open(filename) as f:
        return [line.strip().split("\t") for line in f if line[0].isdigit() and "F" not in line]

# returns list[roll] -> tuple of damages for each armour type. dam is string of dam-crit
def read_it():
    table = [None] * 151
    roll_from = lambda roll: int(roll.split("-")[0])
    roll_to = lambda roll: int(roll.split("-")[1])
    for entry in read_entries(filename):
        for roll in range(roll_from(entry[0]), roll_to(entry[0]) + 1):
            table[roll] = tuple(entry[1:])
    return table

def read_max_entries():
    max_entries = dict()
    prev_line = None
    for line in open(filename):
        line = line.strip()
        if "MAX" in line:
            match = re.match(r".*(\d).*", line)
            blast_radius = int(match.group(1)) - 1 if match else 0   # magic constant: must match definitions above
            max_entries[blast_radius] = tuple(priv_line.split("\t")[1:])
        priv_line = line
    return max_entries

def justify(x):
    if len(x) == 0:
        return "   "
    if len(x) == 1:
        return " " + x + " "
    if len(x) == 2:
        return x + " "
    return x

def entry_to_string(roll_from, roll_to, entry):
    roll = f"{roll_from:02}" + "-" + f"{roll_to:02}"
    foo = []
    for i in range(0, len(entry), 5):
        xs = entry[i:i+5]
        txt = " ".join([f"{justify(x)}".replace(" 0", " -") for x in xs])
        foo.append(txt)
    #entry_out = " ".join([f"{x:^3}".replace(" 0", " -") for x in entry])
    entry_out = "|" + "|".join(foo) + "|"
    return f"{roll:<7}" + entry_out + f"{roll:<8}"

def print_table(table):
    out = []
    i = 0
    line_number = 0
    while i < len(table):
        if table[i] is None:
            i = i + 1
            continue
        roll_from = i
        roll_to = i
        entry = table[i]
        i = i + 1
        while i < len(table) and table[i] == entry:
            roll_to = i
            i = i + 1
        out.append(entry_to_string(roll_from, roll_to, entry))
        if line_number != 1 and line_number % 5 == 1:
            out.append(
                "-------+-------------------+-------------------+-------------------+-------------------+-------------------+-----")
        line_number += 1
    if out[-1][-1] != "-":
        out.append("-------+-------------------+-------------------+-------------------+-------------------+-------------------+-----")
    print("\n".join(out))
    return len(out)

table = read_it()
max_entries = read_max_entries()
# print("max_entries:", max_entries)

# for each armour_type (AT20, AT16, AT11, AT6, AT2), we want a column for touching, ground zero, blast radii 2-5
armour_types = ARMOUR_TYPES # [-2:]
blast_radii = BLAST_RADII
# apply overall modifiers for Mk#, Armour DB
calculate_bonus = lambda blast_radius: BLAST_RADIUS_BONUS[blast_radius] + MK_BONUS - ARMOUR_DB
# print([calculate_bonus(blast_radius) for blast_radius in BLAST_RADII])
column_specs = tuple(product(armour_types, blast_radii))
# print("column_specs:", column_specs)

# def printable_bonus(bonus):
#    out = ("+" if bonus > 0 else "") + str(bonus)
#     return f"{out:>3}"

def print_header():
    #       ROLL    A20
    print(f"GRENADE MK{GRENADE_MK}")
    print()
    print(f"Opponent DB: -{ARMOUR_DB}, Mk{GRENADE_MK}: +{MK_BONUS}, Ground Zero: +40, 2nd: +30, 3rd: +20, 4th: +10, 5th: 0")
    print(f"Touching: +30, Half Soft: -20, Full Soft: -40, Half Hard: -50, Full Hard: -100 [not included below]")

def print_blast_radii():
    out = "Blast Radius: "
    for (grenade_type, calc) in ("Enh", lambda x: x * 3), ("Std", lambda x: x * 2), ("PD", lambda x: x):
        # out += grenade_type + ": " + ", ".join([BLAST_RADIUS_TEXT[blast_radius] + " " + str(calc(GRENADE_MK * (blast_radius + 1))) + "m" for blast_radius in BLAST_RADII]) + "\n"
        out += grenade_type + ": " + ", ".join([str(calc(GRENADE_MK * (blast_radius + 1))) + "m" for blast_radius in BLAST_RADII]) + "  "
    print(out)

def print_roll():
    #print("ROLL    " + " ".join([ARMOUR_TYPE_TEXT[armour_type] for (armour_type, _) in column_specs]) + " ROLL")
    #print("        " + " ".join([BLAST_RADIUS_TEXT[blast_radius] for (_, blast_radius) in column_specs]))
    print("ROLL   |" + "|".join([f"{ARMOUR_TYPE_TEXT[armour_type]:^19}" for armour_type in ARMOUR_TYPES]) + "|ROLL")
    print("       |" + "|".join([" ".join(BLAST_RADIUS_TEXT)] * 5) + "|")

def print_sep():
    print("-----------------------------------------------------------------------------------------------------------------")

def print_sep2():
    print("-------+-------------------+-------------------+-------------------+-------------------+-------------------+-----")

def print_fail():
    roll = "01-02"
    one_block = "|" + " ".join([" F "] * 5)
    five_blocks = one_block * 5
    print(roll + "  " + five_blocks + "|" + roll)
    # print("01-02  " + "  F " * len(column_specs) + " 01-02")

split_element = lambda entry: ((int(entry), "") if entry[-1].isdigit() else (int(entry[:-1]), entry[-1]))

def compute_modified_entry(table, armour_type, roll, modifier, grenade_mk, max_entry):
    modified_roll = roll + modifier
    if modified_roll < 0:
        modified_roll = 0
    elif modified_roll >= len(table):
        modified_roll = len(table) - 1
    if table[modified_roll] is None:
        return "0"
    if table[modified_roll][armour_type] is None:
        return "0"
    (damage, critical) = split_element(table[modified_roll][armour_type])
    (max_damage, max_critical) =  split_element(max_entry[armour_type])
    if damage > max_damage or critical > max_critical:
        damage = max_damage
        critical = max_critical
    return str(damage * grenade_mk) + critical

def generate_new_table(table, column_specs, grenade_mk):
    min_roll = 3
    max_roll = 150 - min([calculate_bonus(blast_radius) for (_, blast_radius) in column_specs])
    new_table = [None] * (max_roll + 1)
    for roll in range(min_roll, max_roll + 1):
        new_table[roll] = list([compute_modified_entry(table, armour_type, roll, calculate_bonus(blast_radius), grenade_mk, max_entries[blast_radius]) for (armour_type, blast_radius) in column_specs])
    return new_table

def compress_two_elements(x, y, z=None):
    if not z:
        z = y
    (d1, c1) = split_element(x)
    (d2, c2) = split_element(y)
    (d3, c3) = split_element(z)
    # avoid a gap, so that printing can collapse entries (probably only relevant for the first entries in the table)
    return x if (d2 == d3) else y

def compress_table(table):
    table = table.copy()
    i = 3
    while i < len(table) - 2:
        zip_it = list(zip(table[i], table[i + 1]))
        if not all([split_element(x)[1] == split_element(y)[1] for (x, y) in zip_it]):
            i = i + 1
            continue
        if not all([abs(split_element(x)[0] - split_element(y)[0]) <= 5 for (x, y) in zip_it]):
            i = i + 1
            continue
        table[i] = table[i + 1] = [compress_two_elements(x, y, z) for (x, y, z) in zip(table[i], table[i + 1], table[i + 2])]
        i = i + 1
    return table

doit = lambda factor: f"(factor {factor * GRENADE_MK}): " + ", ".join(map(lambda br: f"{factor * br * GRENADE_MK}m", range(1, 6)))

blast_radii_blurb =\
f"""
BLAST RADII (Mk{GRENADE_MK}) [T12]
PD  GP/Concussion/Shrapnel/Plasma/Aerosol {doit(1)}
Std GP/Concussion/Shrapnel/Plasma/Aerosol {doit(2)}
Enh GP/Concussion/Shrapnel/Plasma/Aerosol {doit(3)}
PD  Smoke {doit(2)}
Std Smoke {doit(4)}
Enh Smoke {doit(6)}

CRITICALS [T12]
General Purpose: Shrapnel and Impact
Concussion: 2 Impact
Shrapnel: 2 Shrapnel critical
Plasma: Heat, Impact and Radition
Enhanced Plasma (Crowd Control): Automatic C Heat critical in Ground Zero in next round
"""

more_blurb =\
"""
01-02 = Failure. If Failure is rolled, roll 1d10: 01-05: Grenade malfunction, roll on Weapon Malfunction Chart (T63); 
6-10: fumble, roll on Weapon Fumble Table [T95-96]
"""

warning =\
"""
Enhanced Plasma Mk5 disclaimer: EN: Handle with care. Do not fumble. WARNING: may set off incineration devices. Not for indoor use. Newbies, go pick something in the kid’s section. NO: Håndteres med forsiktighet. Ikke fumle. ADVARSEL: kan sette ut forbrenningsenheter. Ikke for innendørs bruk. Nybegynnere, gå og velg noe i barneavdelingen.  SE: Hantera med försiktighet. Fumla inte. VARNING: kan sätta igång förbränningsanordningar. Ej för inomhusbruk. Nybörjare, gå och välj något för barnen. DE: Vorsichtig behandeln. Fummeln Sie nicht herum. ACHTUNG: Verbrennungsgeräte können ausgelöst werden. Nicht für den Innenbereich geeignet. Neulinge, sucht euch etwas aus der Kinderabteilung aus. FI: Käsittele varovasti. Älä haukkua. VAROITUS: saattaa sytyttää polttolaitteita. Ei sisäkäyttöön. Aloittelijat, menkää valitsemaan jotain lastenosastosta.
"""

def print_rest():
    print(more_blurb, end="")
    print(blast_radii_blurb, end="")
    if GRENADE_MK == 5:
        print(warning, end="")
    # launcher error
    # range

def test(table, roll, armour_type, blast_radius, result):
    x = table[roll][armour_type * 5 + blast_radius]
    ok = "ok" if x == result else f"not ok, expected {result}"
    print(f"roll: {roll}, armour_type {armour_type}: {x}. {ok}")
    if x != result:
        sys.exit(1)

table2 = generate_new_table(table, column_specs, GRENADE_MK)

if GRENADE_MK == 5:
    # print(table2[100])
    # it is +25 for mk5, +40/+30/+20/+10/0 for blast radius, -30 for DN
    # +35/+25/+15/+5/-5 for blast radius
    GROUND_ZERO = BLAST_RADII[0]
    test(table2, 90 - 35, AT20, GROUND_ZERO, "0")
    test(table2, 91 - 35, AT20, GROUND_ZERO, "5")
    test(table2, 126 - 35, AT20, GROUND_ZERO, "15")
    test(table2, 127 - 35, AT20, GROUND_ZERO, "15A")
    test(table2, 135 - 35, AT20, GROUND_ZERO, "25A")
    test(table2, 136 - 35, AT20, GROUND_ZERO, "30B")
    test(table2, 142 - 35, AT20, GROUND_ZERO, "40C")
    test(table2, 145 - 35, AT20, GROUND_ZERO, "45D")
    test(table2, 148 - 35, AT20, GROUND_ZERO, "50E")
    test(table2, 165 - 35, AT20, GROUND_ZERO, "50E")

    foo = (
        # AT20
        ((88, 89, 90), "0", (91, 92, 93), "1", (106, 107, 108), "1", tuple(range(109, 123+1)), "2", (124, 125, 126), "3", (127, 128, 129), "3A", (130, 131, 132), "4A", 134, "5A", 137, "6B", 143, "8C", 146, "9D", (148, 149, 150), "10E")
    )

table2 = compress_table(table2)
table2 = compress_table(table2)  # may not buy us anything
# table2 = compress_table3(table2)  # compressing 2 entries twice should be better

print_header()
print_blast_radii()
print_sep2()
print_roll()
print_sep2()
print_fail()
nof_lines = print_table(table2)
print_roll()
print_sep2()

print_rest()

print()
print("nof_lines in table:", nof_lines)

