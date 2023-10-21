def solve(sensors, y_in, expected_result, exit_on_fail, start_x=None, end_x=None):
    # Find x intervals covered by the sensors in the y_in coordinate. sorted by start x
    intervals = []
    for sensor in sensors:
        vertical_distance = abs(sensor.y - y_in)
        x_offset = sensor.range - vertical_distance
        if x_offset >= 0:
            intervals.append( (sensor.x - x_offset, sensor.x + x_offset) )
    intervals.sort()

    non_overlapping_intervals = []
    covered_count = 0
    current_x1 = None
    current_x2 = None
    for (x1, x2) in intervals:
        if True and start_x is not None:
            x1 = max(start_x, x1)
            x2 = min(end_x, x2)
        print(f"Interval ({x1}, {x2})", end=" ")
        if current_x1 is None:
            current_x1 = x1
            current_x2 = x2
            print(f"Starting new interval")
        else:
            # New interval begins before the current one ends, so extend, if it ends later than the current one
            if x1 <= current_x2:
                if x2 > current_x2:
                    current_x2 = x2
                    print(f"New interval ends after the current. Extending current interval to ({current_x1}, {current_x2})")
                else:
                    print(f"New interval ends before the current ({current_x1}, {current_x2}). No update")
                    pass
            # if the new interval begins after the current interval ends, then we are outside
            else:
                non_overlapping_intervals.append( (current_x1, current_x2) )
                newly_covered = current_x2 - current_x1 + 1
                print(f"New interval begins after the current ends, so we are outside now", end=" ")
                print(f"add1: {newly_covered} ({current_x1}, {current_x2})")
                covered_count += newly_covered
                current_x1 = None
                current_x2 = None

    if current_x1:
        if current_x2 >= current_x1:
            non_overlapping_intervals.append( (current_x1, current_x2) )
            newly_covered = current_x2 - current_x1 + 1
            print(f"add2: {newly_covered} ({current_x1}, {current_x2})")
            covered_count += newly_covered

    covered_count2 = 0
    for (x1, x2) in non_overlapping_intervals:
        covered_count2 += (x2 - x1) + 1
    if covered_count == covered_count2:
        print("MATCH")
    else:
        error("NO MATCH")

    beacons_found = 0
    for (x1, x2) in non_overlapping_intervals:
        for sensor in sensors:
            if sensor.beacon_y == y_in and x1 <= sensor.beacon_x <= x2:
                print(f"Compensating for a beacon in ({x1}, {x2})")
                beacons_found += 1
                break

    print(f"beacons found: {beacons_found}")
    covered_count -= beacons_found

    print(f"covered: {covered_count} ", end="")
    print("ok" if covered_count == expected_result else "not ok")
    if covered_count != expected_result:
        print("error")
        if exit_on_fail:
            sys.exit(1)
    return covered_count

non_overlapping_intervals = []
    current_x1 = None
    current_x2 = None
    for (x1, x2) in intervals:
        # Truncate intervals if the search range is limited
        if start_x is not None:
            x1 = max(start_x, x1)
            x2 = min(end_x, x2)
        print(f"Interval ({x1}, {x2})", end=" ")
        if current_x1 is None:
            current_x1 = x1
            current_x2 = x2
            print(f"Starting new interval")
        else:
            # The new interval begins before the current one ends; extend if it ends later than the current one
            if x1 <= current_x2:
                if x2 > current_x2:
                    current_x2 = x2
                    print(f"New interval ends after the current. Extending current interval to ({current_x1}, {current_x2})")
                else:
                    print(f"New interval ends before the current ({current_x1}, {current_x2}). No update")
            else:
                print(f"New interval begins after the current ends, so we are outside again")
                non_overlapping_intervals.append( (current_x1, current_x2) )
                current_x1 = None
                current_x2 = None

