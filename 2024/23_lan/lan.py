import sys
from itertools import product
from utils import Timer

# file = "small.in"
file = "big.in"
edges1 = {(node1, node2) for [node1, node2] in [line.strip().split("-") for line in open(file)]}
edges2 = {(node2, node1) for (node1, node2) in edges1}
edges = edges1.union(edges2)
nodes = { node for (node, _) in edges }

print("nodes:", len(nodes))
print("edges:", len(edges))

def do_part1(nodes, edges):
    triplets = ( (a, b, c) for (a, b) in edges for c in nodes if (a, c) in edges and (b, c) in edges )
    triplets_with_t = { tuple(sorted((a, b, c))) for (a, b, c) in triplets if a[0] == 't' or b[0] == 't' or c[0] == 't' }
    part1 = len(triplets_with_t)
    print("part1:", part1) # 1253

# Complexity: O(nodes * edges^2)
def do_part2(nodes, edges):
    best = set()
    for a in nodes:
        # invariant: all nodes in 'connected' are directly connected to each other
        connected = { a }
        potentials = ( y for (x, y) in edges if x == a )
        for y in potentials:
            if all([(x, y) in edges for x in connected]):
                connected.add(y)
        if len(connected) > len(best):
            best = connected
    print("part2:", ",".join(sorted(best))) # ag,bt,cq,da,hp,hs,mi,pa,qd,qe,qi,ri,uq
    ok = all([(a, b) in edges for (a, b) in product(best, best) if a != b]) #:)
    print(ok)

with Timer():
    do_part1(nodes, edges)
with Timer():
    do_part2(nodes, edges)
