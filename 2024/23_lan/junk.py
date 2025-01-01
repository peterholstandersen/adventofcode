def get_group(start_node, edges):
    group = set()
    work = { start_node }
    while len(work) > 0:
        node = work.pop()
        if node in group:
            continue
        group.add(node)
        work.update( { node2 for (node1, node2) in edges if node == node1 })
    return group

group = get_group('ub', edges)
print("group:", len(group), group)

suksuk = { ('co', 'de', 'ta'), ('co', 'ka', 'ta'), ('de', 'ka', 'ta'), ('qp', 'td', 'wh'), ('tb', 'vc', 'wq'), ('tc', 'td', 'wh'), ('td', 'wh', 'yh')}


def do_part1_slow(nodes, edges):
    triplets = permutations(nodes, 3)
    triplets2 = { tuple(sorted((a, b, c))) for (a, b, c) in triplets if (a, b) in edges and (a, c) in edges and (b, c) in edges }
    print("triplets2:", len(triplets2))
    triplets3 = { (a, b, c) for (a, b, c) in triplets2 if a[0] == 't' or b[0] == 't' or c[0] == 't'}
    part1 = len(triplets3)
    print("part1:", part1)  # 1253


nodes = { node for (node, _) in graph}
print("nodes:", len(nodes))
nodes_with_t = { node for node in nodes if node[0] == 't'}
print("nodes_with_t", len(nodes_with_t), nodes_with_t)
whatnot = { node: set() for node in nodes }
print("whatnot:", len(whatnot), whatnot)
for (node1, node2) in graph:
    if node1 in whatnot:
        whatnot[node1].add(node2)
    if node2 in whatnot:
        whatnot[node2].add(node1)
print("whatnot:", len(whatnot), whatnot)
groups = { tuple(sorted(group)) for group in whatnot.values() }
print("groups:", len(groups), groups)


groups = get_connected_groups(graph1)
print("groups:         ", len(groups), groups)
unique_groups = { tuple(sorted(group)) for group in groups.values() }
print("unique_groups:  ", len(unique_groups), unique_groups)
groups_with_t = [group for group in unique_groups if any([node[0] == "t" for node in group])]
print("groups_with_t:  ", len(groups_with_t), groups_with_t)
triplets_with_t = set()
for group_with_t in groups_with_t:
    triplets_with_t.update({ tuple(sorted(triplet)) for triplet in permutations(group_with_t, 3) if any([node[0] == "t" for node in triplet]) })
print("triplets_with_t:", len(triplets_with_t), triplets_with_t)
directly_conn = set()
for triplet in triplets_with_t:
    if any([node[0] == 't' for node in triplet]):
        if all([(node1, node2) in graph for (node1, node2) in permutations(triplet, 2)]):
            directly_conn.add(tuple(sorted(triplet)))
print("directly_conn:  ", len(directly_conn), directly_conn)
