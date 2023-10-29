import sys
import time
import math
import re
from functools import cache

# Blueprint 1:
#
# Each ore robot costs 4 ore.
#  Each clay robot costs 2 ore.
#  Each obsidian robot costs 3 ore and 14 clay.
#  Each geode robot costs 2 ore and 7 obsidian.

blueprint1 = (
    # robot, (ore, clay, obsidian, geode)
    ((1, 0, 0, 0), (4,  0, 0, 0)),
    ((0, 1, 0, 0), (2,  0, 0, 0)),
    ((0, 0, 1, 0), (3, 14, 0, 0)),
    ((0, 0, 0, 1), (2,  0, 7, 0)),
    )

blueprint2 = (
    # robot, (ore, clay, obsidian, geode)
    ((1, 0, 0, 0), (2, 0,  0, 0)),
    ((0, 1, 0, 0), (3, 0,  0, 0)),
    ((0, 0, 1, 0), (3, 8,  0, 0)),
    ((0, 0, 0, 1), (3, 0, 12, 0)),
)

class State:
    def __init__(self, blueprint, max_useful, resources, robots):
        self.blueprint  = blueprint
        self.max_useful = max_useful
        self.resources  = resources
        self.robots     = robots

    def evaluate(self, time_left):
        return self.resources[3]

    def __str__(self):
        return f"resources={self.resources} robots={self.robots} value={self.evaluate(0)}"

    def __eq__(self, other) -> bool:
        return self.resources == other.resources and self.robots == other.robots

    def __hash__(self):
        return hash( (self.resources, self.robots) )

def add(xs, ys):
    return ( xs[0] + ys[0], xs[1] + ys[1], xs[2] + ys[2], xs[3] + ys[3] )

def subtract(xs, ys):
    return ( xs[0] - ys[0], xs[1] - ys[1], xs[2] - ys[2], xs[3] - ys[3] )

def mult(n, xs):
    # marginal speedup
    return ( n * xs[0], n * xs[1], n * xs[2], n * xs[3] )
    # return tuple([ n * x for x in xs ])

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
    # need > 0
    if robot_count == 0:
        return math.inf
    # need > 0 and robot_count > 0
    time = need // robot_count
    if need % robot_count != 0:
        time = time + 1
    return time

# time needed until you have the necessary resources, 0 if you have them all
def calculate_time_needed(state, needs):
    ctn = calculate_time_needed1
    res = state.resources
    rob = state.robots
    # 11% speedup
    #return max((
    #    ctn(needs[0] - res[0], rob[0]),
    #    ctn(needs[1] - res[1], rob[1]),
    #    ctn(needs[2] - res[2], rob[2]),
    #3))
    return max([calculate_time_needed1(need - res, rob) for (res, rob, need) in zip(state.resources, state.robots, needs)])

count = 0
max_value_global = -1

@cache
def find_max(state, time_left):
    # print("time_left", time_left, "state:", state)
    # 4% speedup
    global count, max_value_global
    count += 1
    if count % 100000 == 0:
        print(count)
    if time_left == 0:
        return state.evaluate(0)

    for i in range(3):
        max_useful_resources = time_left * state.max_useful[i] - state.robots[i] * (time_left - 1)
        if state.resources[i] > max_useful_resources:
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
        if state.robots[i] >= state.max_useful[i]:
            continue
        time_needed = calculate_time_needed(state, cost)
        if time_left - time_needed >= 0:  # marginal
            # current resources plus production till the (end - 1) without building is: ... could be -2 or -3, but opt. later
            x = state.resources[i] + state.robots[i] * (time_left - 1)
            # resources with the built
            y = state.resources[i] + state.robots[i] + (state.robots[i] + 1) * (time_left - 2)
            if False and y <= x:
                continue
            built_something = True
            new_resources = add(state.resources, mult(time_needed + 1, state.robots))   # The new robot is not productive yet
            new_resources = subtract(new_resources, cost)        # build
            new_robots = add(state.robots, robot)
            new_state = State(state.blueprint, state.max_useful, new_resources, new_robots)
            value = find_max(new_state, time_left - time_needed - 1)
            if value > max_value:
                max_value = value

    if not built_something:
        new_resources = add(state.resources, mult(time_left, state.robots))
        new_state = State(state.blueprint, state.max_useful, new_resources, state.robots)
        value = new_state.evaluate(0)
        if value > max_value:
            max_value = value

    return max_value


def main():
    blueprints = read_input("small.in")
    # blueprints = read_input("big.in")[0:3]
    start_time = time.time()
    result = 1
    for blueprint in blueprints:
        print(blueprint)
        max_useful = (
            max([cost[0] for (_, cost) in blueprint]),
            max([cost[1] for (_, cost) in blueprint]),
            max([cost[2] for (_, cost) in blueprint]),
            math.inf  # you can never have too many geodes robots :)
        )
        start = State(blueprint, max_useful, (0,0,0,0), (1,0,0,0)) # blueprints[0] gives 9, blueprints[1] gives 12
        find_max.cache_clear()
        #global max_value_global
        #max_value_global = -1
        x = find_max(start, 24)
        print(x, x[0] if type(x) == tuple else "", "geodes")
        print("count", count)
        result = result * x
    print("result", result)
    print(f"=== {time.time() - start_time} seconds ===")
    sys.exit(1)
    # 3542

    minutes = 24
    result = 0
    index = 0
    for bp in blueprints[1:]:
        index += 1
        print(bp)
        max_useful = (
            max([cost[0] for (_, cost) in bp]),
            max([cost[1] for (_, cost) in bp]),
            max([cost[2] for (_, cost) in bp]),
            math.inf  # you can never have too many geodes robots :)
        )
        start = State(bp, max_useful, (0,0,0,0), (1,0,0,0)) # blueprints[0] gives 9, blueprints[1] gives 12
        find_max.cache_clear()
        x = find_max(start, minutes)
        result += x * index
        print(x, x[0] if type(x) == tuple else "", "geodes")
        # print(count)
    print("result", result)
    print(f"=== {time.time() - start_time} seconds ===")

# part1: small.in 33
# part1: big.in 1092

if __name__ == "__main__":
    main()