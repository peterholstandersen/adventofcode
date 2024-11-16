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

def pesudo_dist(loc1, loc2):
    (y1, x1) = loc1
    (y2, x2) = loc2
    dy = y1 - y2
    dx = x1 - x2
    return dy * dy + dx * dx

def geo_dist(loc1, loc2):
    (lat1, lon1) = loc1
    (lat2, lon2) = loc2
    sin = math.sin
    cos = math.cos
    return math.acos(sin(lat1)*sin(lat2)+cos(lat1)*cos(lat2)*cos(lon2-lon1))*6371

def doit(nodes, walk):
    foo = []
    started = False
    for (location, index) in zip(walk, range(0, len(walk) + 1)):
        # find the closest node in nodes
        a = [ (geo_dist(location, node), node) for node in nodes ]
        a.sort()
        b = [(node_ids[node], round(distance, 2)) for (distance, node) in a]
        (node, distance) = b[0]

        if distance > 5.0:
            continue

        if (not started and distance < 1.0):
            started = True
            foo.append(node)
            continue

        if started:
            previous_node = foo[-1]
            if previous_node != node:
                foo.append(node)

        print(foo)

doit(nodes, walk)