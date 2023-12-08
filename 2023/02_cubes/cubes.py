import os

# part1:
# - add up the game-ids of all possible games when red=12, green=13, and blue=14
# - a game is possible if the number of red, green and blue cubes are less than 12, 13, and 14 respectively.
#
# Input file format:
# Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
# Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue
# Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red
# Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red
# Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green

# Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
# => tanslates into =>
# count += 1 if 3 <= blue and 4 <= red and 2 <= green and 6 <= blue and 2 <= green else 0
def translate_part1(txt):
                                                         # txt = "Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green"
    foo = txt.split(":")                                 # foo = ["Game 1", " 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green"]
    bar = foo[1].strip()                                 # bar = "3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green"
    baz = foo[0].strip().split(" ")[1]                   # baz = "1"
    bar = bar.replace(", ", ",").replace("; ", ",").replace(" ", "<=").replace(",", " and ")
                                                         # 3<=blue and 4<=red and 1<=red and 2<=green and 6<=blue and 2<=green
    return f"count += {baz} if " + bar + " else 0"       # count += 1 if 3<=blue and 4<=red and 1<=red and 2<=green and 6<=blue and 2<=green else 0

out = [ "red = 12; green = 13; blue = 14 "]
out += [ "count = 0" ] + list(map(translate_part1, open("big.in").read().strip().split("\n"))) + ["print('part1:', count)"]

with open("/tmp/part1.py", "w") as file:
    file.write("\n".join(out))

os.system("python /tmp/part1.py") # 2278

# part2:
# - for each game, compute the minimum amout of cubes needed to play the game, multiply them, and add up all the numbers for the file
# - e.g., to play Game 1 below, you need at least 4 red, 2 green, and 6 blue, which gives 4*2*6 = 48
# - so, it is matter of finding the max number of each colour
#
# Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
# => translates into =>
# blue = 1; red = 1; green = 1;
# blue = max(3, blue); red = max(4, red); red = max(1, red); green = max(2, green); blue = max(6, blue); green = max(2, green)
# result += (blue * red * green)
#
def translate_part2(txt):
                                                                            # Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
    txt = txt.split(":")[1].strip()                                         # 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
    txt = txt.replace(", ", ";").replace("; ", ";")                         # 3 blue;4 red;1 red;2 green;6 blue;2 green
    txt = [ foo.split(" ") for foo in txt.split(";") ]                      # [['3', 'blue'], ['4', 'red'], ['1', 'red'], ['2', 'green'], ['6', 'blue'], ['2', 'green']]
    txt = [ f"{colour}=max({count},{colour})" for [count, colour] in txt ]  # ['blue=max(3,blue)', 'red=max(4,red)', 'red=max(1,red)', 'green=max(2,green)', 'blue=max(6,blue)', 'green=max(2,green)']
    txt = "; ".join(txt)                                                    # blue=max(3,blue); red=max(4,red); red=max(1,red); green=max(2,green); blue=max(6,blue); green=max(2,green)
    return txt + "; "

out = "result = 0; "
out += "\n".join(["blue=1; red=1; green=1; " + translate_part2(line) + "result += (blue * red * green)" for line in open("big.in").read().strip().split("\n")])
out += "\n" + "print('part2:', result)"
with open("/tmp/part2.py", "w") as file:
    file.write(out)
os.system("python /tmp/part2.py") # 67953
