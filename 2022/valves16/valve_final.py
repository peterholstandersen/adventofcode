import sys
import re
import time
from typing import Dict, Tuple
from itertools import combinations

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

# All sequences that can be reached within the time limit
def generate_all_sequences(valves, dist, fromm, xs, remaining_time, value_so_far):
    if remaining_time <= 1 or len(xs) <= 1:
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
                for (path, value) in generate_all_sequences(valves, dist, x, ys, remaining_time2, value_so_far2):
                    yield ([x] + path, value)

def solve_part1(valves, distance, useful_valves, start_valve, max_time, expected_result):
    start_time = time.time()
    hmm = generate_all_sequences(valves, distance, start_valve, useful_valves, max_time, 0)
    best = None
    best_value = -1
    count = 0
    for (seq, value) in hmm:
        count = count + 1
        if value > best_value:
            best_value = value
            best = seq
    print(f"{best_value}: {best}", end=" ")
    print("ok" if best_value == expected_result else f"NOT OK, expected {expected_result}")
    print(f"count: {count}")
    print(f"---- {time.time() - start_time} seconds ----")
    if best_value != expected_result:
        sys.exit(1)
    return best, best_value

# Returns list of pairs of sequences ... comma values: [ ([AA, BB, CC], [DD], value), ([AA, BB, DD], [CC], value) ]
def generate_all_pairs_of_sequences(valves, distance, fromm, xs, max_time, max_best_length):
    best_sequence_pair = None
    best_value = -1
    count = 0
    # no need to try both 7/8 split and 8/7 split
    # double work for even numbers of len(xs)
    for i in range(1, len(xs) // 2 + 1):
        # max_best_length is the length of the best sequence; allowing for a longer sequence does not
        # improve anything (as you run out of time). Therefore, there is no need to test sequences
        # longer that max_best_length.
        if i > max_best_length or (len(xs) - i) > max_best_length:
            continue
        print(f"Trying {i} + {len(xs) - i}")
        xss = combinations(xs, i)
        for xs1 in xss:
            xs2 = set(xs) - set(xs1)
            best_value1 = -1
            best_seq1 = None
            for (zs, value1) in generate_all_sequences(valves, distance, fromm, xs1, max_time, 0):
                if value1 > best_value1:
                    best_value1 = value1
                    best_seq1 = zs
            for (ys, value2) in generate_all_sequences(valves, distance, fromm, xs2, max_time, 0):
                # count = count + 1
                if best_value1 + value2 > best_value:
                    best_value = best_value1 + value2
                    best_sequence_pair = (best_seq1, ys)
                    print(f"Best: {best_value}: {best_sequence_pair}")
    print(f"count = {count}")
    return (best_sequence_pair, best_value)


def solve_part2(valves, distance, useful_valves, start_valve, minutes_available, expected_result, max_best_length):
    start_time = time.time()
    (best_sequence_pair, best_value) = generate_all_pairs_of_sequences(valves, distance, start_valve, useful_valves, minutes_available, max_best_length)
    print(f"Best: {best_sequence_pair}")
    print(f"Best: {best_value}", end=" ")
    print("ok" if best_value == expected_result else f"not ok: expected {expected_result}")
    print(f"---- {time.time() - start_time} seconds ----")
    if best_value != expected_result:
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

    (best, best_value) = solve_part1(valves, distance, useful_valves, start_room, 30, expected_result1)
    solve_part2(valves, distance, useful_valves, start_room, 26, expected_result2, len(best))


if __name__ == "__main__":
    main()