# vibrant plum bags contain 5 faded blue bags, 6 dotted black bags.
# faded blue bags contain no other bags.

def read_file(filename):
    text = open(filename).read().strip().split("\n")
    rules = dict()
    for line in text:
        line = line.replace(" ", "_").replace("_bags_contain_", " ").replace(",_", " ").replace(".", "").replace("_bags", "").replace("_bag", "")
        foo = line.split(" ")
        if "other" in line:
            rules[foo[0]] = []
        else:
            rules[foo[0]] = [(eval(x), y) for (x, y) in map(lambda s: tuple(s.replace("_", " ", 1).split(" ")), foo[1:])]
    return rules

def transitive_closure(bag, rules):
    foo = [ bag ]
    for (_, other) in rules[bag]:
        foo.extend(transitive_closure(other, rules))
    return foo

def part1(filename):
    what = "shiny_gold"
    rules = read_file(filename)
    total = 0
    for bag in rules:
        if what in transitive_closure(bag, rules):
            total += 1
    print("part1", filename, total - 1)

def count_it(bag, rules):
    total = 1
    for (count, other) in rules[bag]:
        total += count * count_it(other, rules)
    return total

def part2(filename):
    what = "shiny_gold"
    rules = read_file(filename)
    total = count_it(what, rules) - 1
    print("part2", filename, total)

if __name__ == "__main__":
    part1("small.in") # 4
    part1("big.in")   # 169
    part2("small.in") # 32
    part2("big.in")   # 82372
