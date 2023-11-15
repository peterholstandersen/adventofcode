from functools import reduce
import re

# Input:   start_time
# Bus IDs: 7,13,x,x,59,x,31,19
#
# Bus ID indicates how often the bus leaves for the airport.
# Bus ID 7, leaves every 7 minutes, starting from 0
#
# part1: Leaving at start_time, what is the ID of the earliest bus you can take to the airport multiplied by the number
# of minutes you'll need to wait for that bus?
# That is, when is time % bus_id == 0 and time >= start_time
# This will occur no later than min(bus_id) minutes from start

def part1(filename):
    with open(filename) as file:
        text = file.read().strip().split("\n")
    start_time = int(text[0])
    bus_ids = list(map(int, re.findall(r"[0-9]+", text[1])))
    matches = ((time, bus_id) for time in range(start_time, start_time + min(bus_ids)) for bus_id in bus_ids if time % bus_id == 0)
    match = next(matches)
    wait_time = match[0] - start_time
    bus_id = match[1]
    print("part1", filename, f"wait_time={wait_time}, bus_id={bus_id}, part1_answer={wait_time * bus_id}")

def part2(filename):
    with open(filename) as file:
        text = file.read().strip().split("\n")
    bus_ids = list(map(int, text[1].replace("x", "0").split(",")))
    bus_count = len([1 for x in bus_ids if x != 0])

    # Example:
    # 7,13,x,x,59,x,31,19
    # You are looking for the earliest timestamp (called t) such that:
    # Bus ID 7 departs at timestamp t      (index 0)  (timestamp + index) % bus_id = 0, so: (7, 14, ...)
    # Bus ID 13 departs at timestamp t + 1 (index 1)  (timestamp + index) % bus_id = 0, so: (14, 27, 40, ...)
    # Bus ID 59 departs at timestamp t + 4 (index 4)                                        (63, 122, 181, ...)
    #
    # We do:
    # Find the first timestamp where a bus matches the condition above. This is Bus ID 7 at time 7 (ignoring 0)
    # For Bus ID 7 to continue to match, we only need to examine timestamps which are multipla of 7 after this,
    # Bus ID 31 matches at timestamp 56, where (56 + 6) % 31 == 0. Note that, (56 + 0) % 7 == 0 still holds.
    # Then we continue in increments of 7 * 31 == 217 until the next bus matches
    # Bus ID 19 matches at timestamp 924, where (924 + 7) % 19 == 0
    # We continue in increments of 7 * 31 * 19, etc.
    # When all busses match the conditions, we are done
    timestamp = 0
    increment = 1
    while True:
        timestamp += increment
        matches = [(bus_id, index) for (bus_id, index) in zip(bus_ids, range(len(bus_ids))) if bus_id != 0 and (timestamp + index) % bus_id == 0]
        increment = reduce(lambda id1, id2: id1 * id2[0], matches, 1)  # strictly not necessary to recompute this everytime, but who cares :)
        if len(matches) == bus_count:
            break
    print("part2", filename, timestamp, matches)

if __name__ == "__main__":
    part1("small.in") # 295
    part1("big.in")   # 222
    part2("small.in") # 1068781
    part2("big.in")   # 408270049879073
