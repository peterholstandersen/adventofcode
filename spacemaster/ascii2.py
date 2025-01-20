import sys
import re
from itertools import product

filename = "./warhead_attack_table.txt"
BLAST_RADII = (GROUND_ZERO, BR2, BR3, BR4, BR5) = (0, 1, 2, 3, 4)  # not ideal that the index is -1 of blast radius
BR1 = GROUND_ZERO
BLAST_RADIUS_BONUS = (40, 30, 20, 10, 0)   # must match indices above (remember ground zero is blast radius 1)
GROUND_ZERO_BONUS = BLAST_RADIUS_BONUS[GROUND_ZERO]
TOUCHING_BONUS = 35
GRENADE_MK = 5
ARMOUR_DB = 30
MK_BONUS = GRENADE_MK * 5
HALF_SOFT_DB = 20
FULL_SOFT_DB = 40
HALF_HARD_DB = 50
FULL_HARD_DB = 100
ARMOUR_TYPES = (AT20, AT16, AT11, AT6, AT2) = (0, 1, 2, 3, 4) # must match entries in input file

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

def entry_to_string(roll_from, roll_to, entry):
    roll = f"{roll_from:02}" + "-" + f"{roll_to:02}"
    entry_out = " ".join([f"{x:>3}".replace(" 0", " -") for x in entry])
    return f"{roll:<8}" + entry_out

def print_table(table):
    out = []
    i = 0
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
    print("\n".join(out))
    print(len(out), "lines")

table = read_it()
max_entries = read_max_entries()
print("max_entries:", max_entries)

# for each armour_type (AT20, AT16, AT11, AT6, AT2), we want a column for touching, ground zero, blast radii 2-5
armour_types = ARMOUR_TYPES
bonuses = (TOUCHING_BONUS + GROUND_ZERO_BONUS,) + BLAST_RADIUS_BONUS
level_two_bonuses_text = ("TCH", "GrZ", "1st", "2nd", "4rd", "5th")  # magic-ish constants
# apply overall modifiers for Mk#, Armour DB
bonuses = tuple(map(lambda bonus: bonus + MK_BONUS - ARMOUR_DB, bonuses))
print(bonuses)
print("level_two_bonuses:", bonuses)
column_specs = tuple(product(armour_types, bonuses))
print("column_specs:", column_specs)

def printable_bonus(bonus):
    out = ("+" if bonus > 0 else "") + str(bonus)
    return f"{out:>3}"

def print_header():
    print(f"Armour DB: -{ARMOUR_DB},  Half Soft: -20, Full Soft: -40, Half Hard: -50, Full Hard: -100")
    print(f"Mk{GRENADE_MK}: +{MK_BONUS}, Touching: +35, Ground Zero: +40, 2nd: +30, 3rd: +20, 4th: +10, 5th: 0")
    # zup = lambda txt: "---------" + txt + "----------"
    zup = lambda txt: "=========" + txt + "=========="
    print("ROLL    " + " ".join(map(zup, ("AT20", "AT16", "AT11", "AT6=", "AT2="))))
    #              TCH GrZ 1st 2nd 4rd 5th TCH  GZ 1st 2nd 4rd 5th TCH  GZ 1st 2nd 4rd 5th TCH  GZ 1st 2nd 4rd 5th TCH  GZ 1st 2nd 4rd 5th
    print("        " + " ".join(level_two_bonuses_text * 5))
    print("01-02  " + "   F" * 30)
    # print("        " + " ".join(map(printable_bonus, bonuses * 5)))

def compute_modified_entry(table, armour_type, roll, modifier, grenade_mk, max_entry):
    if armour_type == 1:
        print("compute_modified_entry:", armour_type, max_entry) # NOT CORRECT
    split_entry = lambda entry: ( (int(entry), "") if entry[-1].isdigit() else (int(entry[:-1]), entry[-1]) )
    modified_roll = roll + modifier
    if modified_roll < 0:
        modified_roll = 0
    elif modified_roll >= len(table):
        modified_roll = len(table) - 1
    if table[modified_roll] is None:
        return "0"
    if table[modified_roll][armour_type] is None:
        return "0"
    (damage, critical) = split_entry(table[modified_roll][armour_type])
    (max_damage, max_critical) =  split_entry(max_entry[armour_type])
    if damage > max_damage or critical > max_critical:
        damage = max_damage
        critical = max_critical
    return str(damage * grenade_mk) + critical

# coloum_specs = tuple(product(armour_types, bonuses))

def generate_new_table(table, column_specs, grenade_mk):
    min_roll = 3
    max_roll = 150 - min(bonuses)
    new_table = [None] * (max_roll + 1)
    for roll in range(min_roll, max_roll + 1):
        new_table[roll] = tuple([compute_modified_entry(table, armour_type, roll, modifier, grenade_mk, max_entries[armour_type]) for (armour_type, modifier) in column_specs])
    return new_table


print_header()
table2 = generate_new_table(table, column_specs, GRENADE_MK)
print_table(table2)

