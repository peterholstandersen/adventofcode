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
# HALF_SOFT_DB = 20
# FULL_SOFT_DB = 40
# HALF_HARD_DB = 50
# FULL_HARD_DB = 100
ARMOUR_TYPES = (AT20, AT16, AT11, AT6, AT2) = (0, 1, 2, 3, 4) # must match the order in input file
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

def generate_new_table(table, columns, grenade_mk):
    min_roll = 3
    max_roll = 150 - min([calculate_bonus(blast_radius) for (_, blast_radius) in columns])
    new_table = [None] * (max_roll + 1)
    for roll in range(min_roll, max_roll + 1):
        new_table[roll] = list([compute_modified_entry(table, armour_type, roll, calculate_bonus(blast_radius), grenade_mk, max_entries[blast_radius]) for (armour_type, blast_radius) in columns])
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

table = read_it()
max_entries = read_max_entries()
# we want a column for each armour type and each blast radius
columns = tuple(product(ARMOUR_TYPES, BLAST_RADII))
# apply modifiers for blast radius, Mk#, Armour DB
calculate_bonus = lambda blast_radius: BLAST_RADIUS_BONUS[blast_radius] + MK_BONUS - ARMOUR_DB

table2 = generate_new_table(table, columns, GRENADE_MK)
table3 = compress_table(table2)
table3 = compress_table(table3)  # may not buy us anything
