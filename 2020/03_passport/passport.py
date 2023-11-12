import re

passports = open("big.in").read().strip().split("\n\n")

# part1 are those that have all the required fields
required = ["byr", "iyr", "eyr", "hgt", "hcl", "ecl", "pid"]
part1_valid = [p for p in passports if all([req in p for req in required])]
print("part1", len(part1_valid)) # 219

# part2 are those that have all the required field fulfiling these conditions. cid is ignored so it is always valid
byr = lambda x: len(x) == 4 and x.isdigit() and 1920 <= int(x) <= 2002
iyr = lambda x: len(x) == 4 and x.isdigit() and 2010 <= int(x) <= 2020
eyr = lambda x: len(x) == 4 and x.isdigit() and 2020 <= int(x) <= 2030
hgt = lambda x: (x[-2:] == "cm" and 150 <= int(x[:-2]) <= 193) or (x[-2:] == "in" and 59 <= int(x[:-2]) <= 76)
hcl = lambda x: x[0] == "#" and len(x) == 7 and all([a in "0123456789abcdef" for a in x[1:]])
ecl = lambda x: x in ["amb", "blu", "brn", "gry", "grn", "hzl", "oth"]
pid = lambda x: len(x) == 9 and x.isdigit()
cid = lambda x: True

# iyr:2016
# hgt:168cm
# eyr:2027 cid:60 ecl:gry hcl:#cfa07d
# pid:322944081 byr:1993

valid = 0
for p in part1_valid:
    xs = re.split(r"[\n ]", p)
    ys = [ x[:3] + "('" + x[4:] + "')" for x in xs ]   # convert fff:x to fff('x')
    zs = " and ".join(ys)                              # covert [ f('x'), g('y'), ... ] to f('x') and g('y') and ...
    if eval(zs):
        valid += 1
print("part2", valid) # 127