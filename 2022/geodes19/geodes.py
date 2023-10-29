import sys
import time
import math
import re
from functools import cache

# Blueprint 1:
#  Each ore robot costs 4 ore.
#  Each clay robot costs 2 ore.
#  Each obsidian robot costs 3 ore and 14 clay.
#  Each geode robot costs 2 ore and 7 obsidian.

# Blueprint internal representation. Maybe not the smartest ... but, ...
# Blueprint: (robot, (ore, clay, obsidian, geode)) x 4
# Example
# (
#    ((1, 0, 0, 0), (4,  0, 0, 0)),
#    ((0, 1, 0, 0), (2,  0, 0, 0)),
#    ((0, 0, 1, 0), (3, 14, 0, 0)),
#    ((0, 0, 0, 1), (2,  0, 7, 0)),
# )

count = 0

class State:
    def __init__(self, blueprint, max_useful, resources, robots):
        self.blueprint  = blueprint
        self.max_useful = max_useful
        self.resources  = resources
        self.robots     = robots

    def __str__(self):
        return f"resources={self.resources} robots={self.robots}"

    def __eq__(self, other) -> bool:
        return self.resources == other.resources and self.robots == other.robots

    def __hash__(self):
        return hash( (self.resources, self.robots) )

def add(xs, ys):
    return ( xs[0] + ys[0], xs[1] + ys[1], xs[2] + ys[2], xs[3] + ys[3] )

def subtract(xs, ys):
    return ( xs[0] - ys[0], xs[1] - ys[1], xs[2] - ys[2], xs[3] - ys[3] )

def mult(n, xs):
    return ( n * xs[0], n * xs[1], n * xs[2], n * xs[3] )

# Blueprint 1:
#   Each ore robot costs 4 ore.
#   Each clay robot costs 2 ore.
#   Each obsidian robot costs 3 ore and 14 clay.
#   Each geode robot costs 2 ore and 7 obsidian.
#
# 7 numbers in total for a blueprint
def read_input(filename):
    with open(filename) as file:
        numbers = list(map(int, re.findall(r"\d+", file.read().strip())))
    blueprints = []
    for i in range(0, len(numbers), 7):
        blueprint = (
            ((1, 0, 0, 0), (numbers[i+1], 0, 0, 0)),
            ((0, 1, 0, 0), (numbers[i+2], 0, 0, 0)),
            ((0, 0, 1, 0), (numbers[i+3], numbers[i+4], 0, 0)),
            ((0, 0, 0, 1), (numbers[i+5], 0, numbers[i+6], 0))
        )
        blueprints.append(blueprint)
    return blueprints

def calculate_time_needed1(need, robot_count):
    if need <= 0:
        return 0
    if robot_count == 0:
        return math.inf
    time = need // robot_count
    if need % robot_count != 0:
        time = time + 1
    return time

# time needed until you have all the needed resources, 0 if you have them all
def calculate_time_needed(state, needs):
    return max([calculate_time_needed1(need - res, rob) for (res, rob, need) in zip(state.resources, state.robots, needs)])

@cache
def find_max(state, time_left):
    # 4% speedup to remove count
    global count
    count += 1
    if count % 100000 == 0:
        print(count)
    if time_left == 0:
        return state.resources[3]

    for i in range(3):
        # time_left * state.max_useful[i] is the maximum amount of resources we can possibly spend in the time left
        # state.robots[i] * (time_left - 1) is the amount of resources we will produce
        # max_useful_resource is then the maximum number of resources we could have right now
        # Having more resource than that will not produce more or less geodes.
        # By calling find_max using max_useful_resources rather than the actual amount of resources,
        # will use the cached value, reducing the runtime complexity significantly.
        max_useful_resources = time_left * state.max_useful[i] - state.robots[i] * (time_left - 1)
        if state.resources[i] > max_useful_resources:
            # not so nice, but cant change a tuple ...
            suk = list(state.resources)
            suk[i] = max_useful_resources
            new_resources = tuple(suk)
            # use the cached value
            new_state = State(state.blueprint, state.max_useful, new_resources, state.robots)
            return find_max(new_state, time_left)

    max_value = -1
    built_something = False
    for i in range(0, len(state.blueprint)):
        (robot, cost) = (state.blueprint[i][0], state.blueprint[i][1])
        # No point in building another if we already have the amount we need
        if state.robots[i] >= state.max_useful[i]:
            continue
        # Time needed to have enough resources to build the robot
        time_needed = calculate_time_needed(state, cost)
        if time_left - time_needed >= 0:
            built_something = True
            # The new robot is not productive till the round after it has been built
            new_resources = add(state.resources, mult(time_needed + 1, state.robots))
            new_resources = subtract(new_resources, cost)
            new_robots = add(state.robots, robot)
            new_state = State(state.blueprint, state.max_useful, new_resources, new_robots)
            # Fastforward to the round after the robot has been built
            value = find_max(new_state, time_left - time_needed - 1)
            if value > max_value:
                max_value = value

    if not built_something:
        # Compute how many geodes we will have at the end
        value = state.resources[3] + time_left * state.robots[3]
        if value > max_value:
            max_value = value

    return max_value

def get_start_state(blueprint):
    # Maximum number of useful robots.
    # There is no point in producing more resources than we can spend in one round.
    max_useful =(
        max([cost[0] for (_, cost) in blueprint]),
        max([cost[1] for (_, cost) in blueprint]),
        max([cost[2] for (_, cost) in blueprint]),
        math.inf  # you can never have too many geodes robots :)
    )
    # We start with 0 resources and 1 ore robot.
    return State(blueprint, max_useful, (0, 0, 0, 0), (1, 0, 0, 0))

def main():
    filename = "small.in"; blueprints_part1 = read_input(filename); blueprints_part2 = blueprints_part1
    # filename = "big.in"; blueprints_part1 = read_input(filename); blueprints_part2 = blueprints_part1[0:3]
    start_time = time.time()
    result_part1 = 0
    for index in range(len(blueprints_part1)):
        find_max.cache_clear()
        start = get_start_state(blueprints_part1[index])
        x_24 = find_max(start, 24)
        print("x_24:", x_24)
        result_part1 += (index + 1) * x_24

    result_part2 = 1
    for blueprint in blueprints_part2:
        start = get_start_state(blueprint)
        find_max.cache_clear()
        x_32 = find_max(start, 32)
        print("x_32:", x_32)
        result_part2 = result_part2 * x_32

    print(f"part1 {filename}: {result_part1}")
    print(f"part2 {filename}: {result_part2}")
    print(f"=== {time.time() - start_time} seconds ===")

# part1: small.in 9*1 + 12*2 = 33
# part2: small.in 3472
# 80 seconds
#
# part1: big.in   1092
# part2: big.in   3542
# 17 seconds
if __name__ == "__main__":
    main()