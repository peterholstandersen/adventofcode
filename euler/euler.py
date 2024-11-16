import sys
import math

def read_coords(filename):
    return [(float(x), float(y)) for (x, y) in [line.split(" ") for line in open(filename).read().strip().split("\n")]]

nodes = read_coords("nodes")
nodes.sort()
node_ids = dict(zip(nodes, range(1, len(nodes) + 1))) # mapping from (lattitude, longtitude) to id
walk = read_coords("Euler_1.txt")
print(nodes)
print(len(walk), walk)
# print()

def dist(loc1, loc2):
    (y1, x1) = loc1
    (y2, x2) = loc2
    dy = y1 - y2
    dx = x1 - x2
    return math.sqrt(dy * dy + dx * dx)

def geo_dist(loc1, loc2):
    (lat1, lon1) = loc1
    (lat2, lon2) = loc2
    sin = math.sin
    cos = math.cos
    return math.acos(sin(lat1)*sin(lat2)+cos(lat1)*cos(lat2)*cos(lon2-lon1))*6371

def doit(nodes, walk):
    foo = [-1]
    started = False
    for (location, index) in zip(walk, range(0, len(walk) + 1)):
        # find the closest node in nodes

        a = [ (geo_dist(location, node), node) for node in nodes ]
        a.sort()
        b = [(node_ids[node], round(distance, 2)) for (distance, node) in a]
        # print(index, b)

        (node, distance) = b[0]

        if distance > 5.0:
            continue

        #started = True
        if (not started and distance < 1.0):
            started = True
            foo.append(node)
            continue

        if started:
            previous_node = foo[-1]
            if previous_node != node:
                foo.append(node)

        print(foo[1:])
        # sys.exit(1)


doit(nodes, walk)

sys.exit(1)

my_reverse = lambda x: x[::-1]

def center(line):
    col = len(line) // 2
    if line[:col] == my_reverse(line[col:-1]):
        return col
    col = len(line) // 2 + 1
    if line[1:col] == my_reverse(line[col:]):
        return col
    return -1

def center2(line):
    foobar = []
    for col in range(1, len(line)):
        foo = line[:col]
        bar = line[col:]
        if my_reverse(foo)[:len(bar)] == bar[:len(foo)]:
            foobar.append(col)
    return foobar

#print(center2("#.##..##"))
#sys.exit(1)

for pat in foo:
    #print("\n".join(pat))
    xx = [center2(line) for line in pat]
    yy = [y for y in range(1, len(pat[0])) if all([y in xs for xs in xx])]
    print(yy)