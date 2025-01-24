from ascii3 import *

def test(table, roll, armour_type, blast_radius, result):
    x = table[roll][armour_type * 5 + blast_radius]
    ok = "ok" if x == result else f"not ok, expected {result}"
    print(f"roll: {roll}, armour_type {armour_type}: {x}. {ok}")
    if x != result:
        sys.exit(1)

def do_test():
    # for the uncompressed table
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
        ((88, 89, 90), "0", (91, 92, 93), "1", (106, 107, 108), "1", tuple(range(109, 123 + 1)), "2",
        (124, 125, 126), "3", (127, 128, 129), "3A", (130, 131, 132), "4A", 134, "5A", 137, "6B", 143, "8C",
        146, "9D", (148, 149, 150), "10E")
        )

print(table2)

do_test()