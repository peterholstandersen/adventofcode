from ascii3 import *

# woo woo: https://powerman.name/doc/asciidoc

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
            out.append("-------+-------------------+-------------------+-------------------+-------------------+-------------------+-----")
        line_number += 1
    if out[-1][-1] != "-":
        out.append("-------+-------------------+-------------------+-------------------+-------------------+-------------------+-----")
    print("\n".join(out))
    return len(out)

def print_header():
    print(f"GRENADE MK{GRENADE_MK}")
    print()
    print(f"Opponent DB: -{ARMOUR_DB}, Mk{GRENADE_MK}: +{MK_BONUS}, Ground Zero: +40, 2nd: +30, 3rd: +20, 4th: +10, 5th: 0")
    print(f"Touching: +30, Half Soft: -20, Full Soft: -40, Half Hard: -50, Full Hard: -100 [not included below]")

def print_blast_radii():
    out = "Blast Radius: "
    for (grenade_type, calc) in ("Enh", lambda x: x * 3), ("Std", lambda x: x * 2), ("PD", lambda x: x):
        out += grenade_type + ": " + ", ".join([str(calc(GRENADE_MK * (blast_radius + 1))) + "m" for blast_radius in BLAST_RADII]) + "  "
    print(out)

def print_roll():
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

scale_blast_radius = lambda factor: f"(factor {factor * GRENADE_MK}): " + ", ".join(map(lambda br: f"{factor * br * GRENADE_MK}m", range(1, 6)))

blast_radii_blurb =\
f"""
BLAST RADII (Mk{GRENADE_MK}) [T12]
PD  GP/Concussion/Shrapnel/Plasma/Aerosol {scale_blast_radius(1)}
Std GP/Concussion/Shrapnel/Plasma/Aerosol {scale_blast_radius(2)}
Enh GP/Concussion/Shrapnel/Plasma/Aerosol {scale_blast_radius(3)}
PD  Smoke {scale_blast_radius(2)}
Std Smoke {scale_blast_radius(4)}
Enh Smoke {scale_blast_radius(6)}

CRITICALS [T12]
General Purpose: Shrapnel and Impact
Concussion: 2 Impact
Shrapnel: 2 Shrapnel critical
Plasma: Heat, Impact and Radition
Enhanced Plasma (Crowd Control): Automatic C Heat critical in Ground Zero in next round
"""

more_blurb =\
"""
01-02 = Failure. If Failure is rolled, roll 1d10: 01-05: Grenade malfunction, roll on Weapon Malfunction Chart (T63); 6-10: fumble, roll on Weapon Fumble Table [T95-96]
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

print_header()
print_blast_radii()
print_sep2()
print_roll()
print_sep2()
print_fail()
nof_lines = print_table(table3)
print_roll()
print_sep2()
print_rest()
