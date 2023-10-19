import sys
import re
import time
from typing import Dict, Tuple
from itertools import combinations

# Algorithm (see puzzle on https://adventofcode.com/2022/day/16).
#
# First, find all shortest paths between all valve rooms. Stored in a dictionary mapping from (room1,room2) to distance.
# Otherwise, we only focus on useful valves, i.e, those with rate > 0.
#
# Part I: We want to find the most optimal sequence to open the valves in, so we test all the possible combinations of
# "useful" valves. Brute force! The puzzle in big.in has 15 valves with rate > 0. Testing all sequences of the 15
# would amount to testing 15! = 1307674368000 combinations. However, only a few of these can be reached within the time
# limit of 30 minutes, so it is doable.
#
# Part II: Now we have two individuals to open valves. We want to find the combination of two sequences to open the
# valves in, one for each individual. Again, we test all possible combinations that can be reached within (now) 26
# minutes. We evaluate all possible two-way splits of useful valves, then try all combinations of each set to
# find the best. For example, the set [1,2,3] can be split into [1],[2,3] and [2],[1,3] and [3],[1,2]. As the
# evaluation of the sequences are independent, we only need to look at either the 1-2 split or the 2-1 split.
#
# Also, suppose it is not possible to open all valves within the time limit, it does not make sense to try
# sequences longer than the length of the best one. Suppose the best has length 6, then we only need to look at
# the 6-9 split for a puzzle with 15 valves.

class Valve:
    def __init__(self, name, rate, tunnels):
        self.name = name
        self.rate = rate
        self.tunnels = tunnels

    def __str__(self):
        return f"{self.name}: {self.rate}, tunnels={self.tunnels}"

# Find the shortest path from one valve to all others
def find_shortest_paths(dist: Dict[Tuple[str, str], int], start_valve_name: str, valves: Dict[str, Valve]) -> None:
    queue = [ (start_valve_name, 0) ]
    dist[ (start_valve_name, start_valve_name) ] = 0
    while len(queue) > 0:
        # print(queue)
        (valve_name, distance_from_start) = queue.pop(0)
        for neighbour_name in valves[valve_name].tunnels:
            if not (start_valve_name, neighbour_name) in dist:
                dist[ (start_valve_name, neighbour_name) ] = distance_from_start + 1
                queue.append( (neighbour_name, distance_from_start + 1) )

# Find the shortest paths between all valves
def find_all_shortest_paths(valves):
    dist = dict()  # from (v1, v2) to distance
    for valve in valves:
        find_shortest_paths(dist, valve, valves)
    return dist

# Evaluate all sequences that can be reached within the time limit
def evaluate_all_sequences(valves, dist, fromm, xs, remaining_time, value_so_far):
    if remaining_time <= 2 or len(xs) == 0:
        yield ([], value_so_far)
    else:
        for x in xs:
            remaining_time2 = remaining_time - 1 - dist[(fromm, x)]
            if (remaining_time2 <= 0):
                yield([], value_so_far)
            else:
                value_so_far2 = value_so_far + valves[x].rate * remaining_time2
                # ys = xs - {x}
                ys = [y for y in xs if x != y]
                for (path, value) in evaluate_all_sequences(valves, dist, x, ys, remaining_time2, value_so_far2):
                    yield ([x] + path, value)

def solve_part1(valves, distance, useful_valves, start_valve, max_time, expected_result):
    start_time = time.time()
    hmm = evaluate_all_sequences(valves, distance, start_valve, useful_valves, max_time, 0)
    best = None
    best_value = -1
    count = 0
    for (seq, value) in hmm:
        count = count + 1
        if value > best_value:
            best_value = value
            best = seq
    print(f"{best_value}: {best}", end=" ")
    print("ok" if best_value == expected_result or expected_result == 0 else f"NOT OK, expected {expected_result}")
    print(f"count: {count}")
    print(f"---- {time.time() - start_time} seconds ----")
    if best_value != expected_result and expected_result != 0:
        print("abort")
        sys.exit(1)
    return best, best_value

# Returns list of pairs of sequence and values: [ ([AA, BB, CC], [DD], value), ([AA, BB, DD], [CC], value) ]
def evaluate_all_pairs_of_sequences(valves, distance, fromm, xs, max_time, max_best_length):
    best_sequence_pair = None
    best_value = -1
    count = 0
    print(f"Trying {max_best_length} / {len(xs) - max_best_length} split")
    xss = combinations(xs, max_best_length)
    for xs1 in xss:
        best_value1 = -1
        best_seq1 = None
        for (zs, value1) in evaluate_all_sequences(valves, distance, fromm, xs1, max_time, 0):
            if value1 > best_value1:
                best_value1 = value1
                best_seq1 = zs
        xs2 = set(xs) - set(xs1)
        for (ys, value2) in evaluate_all_sequences(valves, distance, fromm, xs2, max_time, 0):
            # count = count + 1
            if best_value1 + value2 > best_value:
                best_value = best_value1 + value2
                best_sequence_pair = (best_seq1, ys)
                print(f"Best: {best_value}: {best_sequence_pair}")
    print(f"count = {count}")
    return (best_sequence_pair, best_value)

def solve_part2(valves, distance, useful_valves, start_valve, minutes_available, expected_result, max_best_length):
    start_time = time.time()
    (best_sequence_pair, best_value) = evaluate_all_pairs_of_sequences(valves, distance, start_valve, useful_valves, minutes_available, max_best_length)
    print(f"Best: {best_sequence_pair}")
    print(f"Best: {best_value}", end=" ")
    print("ok" if best_value == expected_result or expected_result == 0 else f"not ok: expected {expected_result}")
    print(f"---- {time.time() - start_time} seconds ----")
    if best_value != expected_result and expected_result != 0:
        print("abort")
        sys.exit(1)

def valve_name_to_id(name):
    return name
    # saves 10% running time to use numbers rather than strings of 2 length
    if len(name) > 2:
        print("ups")
        sys.exit(1)
    return ord(name[0]) + 256 * ord(name[1])

def read_input(filename):
    # valve_name -> Valve
    valves = dict()
    with open(filename) as file:
        for line in file:
            match = re.match("^Valve ([a-zA-Z0-9]+) has flow rate=([0-9]+); tunnel.* lead.* to valve.? ([a-zA-Z0-90, ]+)$", line)
            if match:
                gr = match.group
                # print("match:", gr(1), gr(2), gr(3))
                valve_id = valve_name_to_id(gr(1))
                rate = int(gr(2))
                tunnels = [valve_name_to_id(tunnel.strip()) for tunnel in gr(3).strip().split(",")]
                valves[valve_id] = Valve(valve_id, rate, tunnels)
            else:
                print(line.strip())
                print("no match")
                sys.exit(1)
    return valves


def main():
    # filename = "micro.in"; expected_result1 = 0; expected_result2 = 0
    # filename = "small.in"; expected_result1 = 1651; expected_result2 = 1707
    filename = "big.in"; expected_result1 = 1716; expected_result2 = 2504 # (['UV', 'FC', 'EZ', 'OY', 'FU', 'NN'], ['JT', 'KE', 'IR', 'PH', 'IF', 'SV'])

    valves = read_input(filename)
    useful_valves = [valve_name for (valve_name, valve) in valves.items() if valve.rate != 0]
    print(f"useful_valves({len(useful_valves)}): {useful_valves}")

    # distance: (valve-name, valve-name) -> distance
    distance = find_all_shortest_paths(valves)
    start_room = valve_name_to_id("AA")
    (_, _) = solve_part1(valves, distance, useful_valves, start_room, 30, expected_result1)
    (best, best_value) = solve_part1(valves, distance, useful_valves, start_room, 26, 0)
    solve_part2(valves, distance, useful_valves, start_room, 26, expected_result2, len(best))


if __name__ == "__main__":
    main()