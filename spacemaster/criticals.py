import sys
import re

xyz =\
"""
Shoulder smashed. Foe spins back
10 feet. He is stunned and unable to parry
for 7 rnds. Arm is useless. Receives
6 hits/rnd. +26 hits.
"""
filename = "shrapnel_criticals.txt"

with open(filename) as file:
    table = [
        [foo.strip() for foo in line.strip().replace("\n", " ").split(".") if len(foo.strip()) > 0]
        for line in file.read().strip().split("\n\n")
    ]

print("table:", table)

stunned = lambda x: f"stunned {x} rounds"
hits_per_round = lambda x: f"{x} hits/rnd"
extra_hits = lambda x: f"+{x.replace("O", "0")} hits"

patterns = (
    (r".*stunned.*(\d+).*", stunned),
    (r".*(\d+).*hits/rnd.*", hits_per_round),
    (r".*([O\d]+).*hit.*", extra_hits),
)

#print(re.match(patterns[2][0], "t0 hits"))
#sys.exit()

def parse_entry(entry):
    something = []
    text = []
    for sentence in entry:
        found_a_match = False
        for (pattern, action) in patterns:
            match = re.match(pattern, sentence)
            if match:
                something.append(action(match.group(1)))
                found_a_match = True
                break
        if not found_a_match:
            text.append(sentence)
    print(". ".join(text))

def parse_table(table):
    [ parse_entry(entry) for entry in table ]

parse_table(table)
