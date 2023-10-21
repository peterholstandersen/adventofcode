import sys
import re
import time

class Sensor:
    def __init__(self, x, y, beacon_x, beacon_y):
        self.x = x
        self.y = y
        self.beacon_x = beacon_x
        self.beacon_y = beacon_y
        self.range = distance(x, y, beacon_x, beacon_y)

    def __str__(self):
        return f"({self.x}, {self.y}, {self.range})"

class Interval:
    def __init__(self, x1, x2):
        self.x1 = x1
        self.x2 = x2

def error(msg):
    print(msg)
    sys.exit(1)

def distance(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)

def read_input(filename):
    sensors = []
    # Format example: "Sensor at x=2, y=18: closest beacon is at x=-2, y=15"
    with open(filename) as file:
        for line in file:
            match = re.match("^Sensor at x=([0-9-]+), y=([0-9-]+): closest beacon is at x=([0-9-]+), y=([0-9-]+)$", line)
            if match:
                gr = match.group
                sensor = Sensor(int(gr(1)), int(gr(2)), int(gr(3)), int(gr(4)))
                sensors.append(sensor)
            else:
                error("no match")
    return sensors

def verify_result(result, expected_result, exit_on_fail=True):
    print(f"result={result} expected_result={"None" if expected_result is None else expected_result}", end=" ")
    ok = expected_result is None or result == expected_result
    print("(OK)" if ok else "(NOT OK)")
    if not ok and exit_on_fail:
        print("FAIL")

def compute_covered_intervals_at_y(sensors, y_in):
    intervals = []
    for sensor in sensors:
        vertical_distance = abs(sensor.y - y_in)
        x_offset = sensor.range - vertical_distance
        if x_offset >= 0:
            intervals.append( (sensor.x - x_offset, sensor.x + x_offset) )
    intervals.sort()
    return intervals

def find_non_overlapping_intervals(intervals, start_x, end_x):
    #
    # When a new interval overlaps the current one, and it ends after the current one, we extend the current one
    #     [........]
    #         [........]
    # ->
    #     [............]
    #
    # if the new one ends before the current one, we ignore it
    #     [........]
    #       [...]
    #
    # when we meet a new interval starting after the current one, the current does not overlap with others
    #     [.......]   [...]
    #
    non_overlapping_intervals = []
    current_interval = None
    for (x1, x2) in intervals:
        # Truncate intervals if the search range is limited
        if start_x is not None:
            x1 = max(start_x, x1)
            x2 = min(end_x, x2)
        # print(f"Interval ({x1}, {x2})", end=" ")
        if current_interval is None:
            current_interval = Interval(x1, x2)
        else:
            if x1 <= current_interval.x2 and x2 > current_interval.x2:
                current_interval.x2 = x2
            elif x1 > current_interval.x2:
                non_overlapping_intervals.append( (current_interval.x1, current_interval.x2) )
                current_interval = None
    if current_interval is not None:
        non_overlapping_intervals.append( (current_interval.x1, current_interval.x2) )
    return non_overlapping_intervals

def count_beacons(sensors, y_in, non_overlapping_intervals):
    beacons_found = []
    for (x1, x2) in non_overlapping_intervals:
        for sensor in sensors:
            if sensor.beacon_y == y_in and x1 <= sensor.beacon_x <= x2:
                beacons_found.append( (sensor.beacon_x, sensor.beacon_y) )
                break
    # print(f"beacons found: {beacons_found}")
    return len(beacons_found)

def solve(sensors, y_in, expected_result, exit_on_fail, start_x=None, end_x=None):
    intervals = compute_covered_intervals_at_y(sensors, y_in)
    non_overlapping_intervals = find_non_overlapping_intervals(intervals, start_x, end_x)
    covered_count = 0
    for (x1, x2) in non_overlapping_intervals:
        covered_count += (x2 - x1) + 1
    if start_x is None:
        # it is only for part I of the puzzle, we need to compensate for existing beacons
        beacons_count = count_beacons(sensors, y_in, non_overlapping_intervals)
        covered_count -= beacons_count
    # verify_result(covered_count, expected_result, exit_on_fail)
    return covered_count


def main():
    #filename = "small.in"; y_in = 10; expected_result_1 = 26; max_coordinate = 20
    filename = "big.in"; y_in = 2000000; expected_result_1 = 5073496; max_coordinate = 4000000

    sensors = read_input(filename)
    start_time = time.time()

    if False:
        solve(sensors, y_in=y_in, expected_result=expected_result_1, exit_on_fail=True)

    if True:
        # range(2638237 - 50000, 2638237 + 50000)
        for y in range(0, max_coordinate + 1):
            covered = solve(sensors, y_in=y, expected_result=None, exit_on_fail=False, start_x=0, end_x=max_coordinate)
            if y % 100000 == 0:
                print(y, covered)
            if covered == max_coordinate:
                print(f"Found y={y}")

    if False:
        # range(3270298 - 50000, 3270298 + 50000)
        swapped_sensors = []
        for sensor in sensors:
            swapped_sensors.append(Sensor(sensor.y, sensor.x, sensor.beacon_y, sensor.beacon_x))
        for y in range(0, max_coordinate + 1):
            covered = solve(swapped_sensors, y_in=y, expected_result=None, exit_on_fail=False, start_x=0, end_x=max_coordinate)
            if covered == max_coordinate:
                print(f"Found x={y}")

    print(f"---- {time.time() - start_time} seconds ----")


if __name__ == "__main__":
    y = 2638237
    x = 3270298
    # print(x * 4000000 + y)
    main()