import sys
from typing import Dict, Tuple, Optional, Callable

Position = Tuple[int, int]

up = lambda pos: (pos[0] - 1, pos[1])
down = lambda pos: (pos[0] + 1, pos[1])
left = lambda pos: (pos[0], pos[1] - 1)
right = lambda pos: (pos[0], pos[1] + 1)

def find_shortest_path_part1(start: Position, end: Position, hills: Dict[Position, int]) -> Optional[int]:
    queue = [ (start, 0) ]
    visited = set()
    while len(queue) > 0:
        (position, distance) = queue.pop(0)
        if position == end:
            return distance
        for direction in [up, down, left, right]:
            neighbour = direction(position)
            if (neighbour not in visited) and (neighbour in hills) and (hills[neighbour] <= hills[position] + 1):
                visited.add(neighbour)
                queue.append( (neighbour, distance + 1) )
    return None

def find_shortest_path_part2(start: Position, hills: Dict[Position, int]) -> Optional[Tuple[Position, int]]:
    queue = [ (start, 0) ]
    visited = set()
    while len(queue) > 0:
        (position, distance) = queue.pop(0)
        if hills[position] == ord("a"):
            return (position, distance)
        for direction in [up, down, left, right]:
            neighbour = direction(position)
            if (neighbour not in visited) and (neighbour in hills) and (hills[neighbour] >= hills[position] - 1):
                visited.add(neighbour)
                queue.append( (neighbour, distance + 1) )
    return None

def find_shortest_path_generic(start: Position, end_condition: Callable[[Position], bool], neighbour_condition: Callable[[Position, Position], bool], hills: Dict[Position, int]) -> Optional[Tuple[Position, int]]:
    queue = [ (start, 0) ]
    visited = set()
    while len(queue) > 0:
        (position, distance) = queue.pop(0)
        if end_condition(position):
            return (position, distance)
        for direction in [up, down, left, right]:
            neighbour = direction(position)
            if (neighbour not in visited) and (neighbour in hills) and neighbour_condition(position, neighbour):
                visited.add(neighbour)
                queue.append( (neighbour, distance + 1) )
    return None

def read_input(filename):
    with open(filename) as file:
        text = file.read().strip()
        width = text.index("\n")
        text = text.replace("\n", "")
        i = text.find("S")
        start = (i // width, i % width)
        i = text.find("E")
        end = (i // width, i % width)
        text = text.replace("S", "a").replace("E", "z")
        hills = { (i // width, i % width): ord(text[i]) for i in range(0, len(text)) }
        return (start, end, hills)

def main():
    for filename in ["small.in", "big.in"]:
        (start, end, hills) = read_input(filename)
        # pd1 = find_shortest_path_part1(start, end, hills)
        pd1 = find_shortest_path_generic(start, lambda position: position == end, lambda position, neighbour: hills[neighbour] <= hills[position] + 1, hills)
        print(f"Part1 {filename}: shortest distance from start to end: {pd1}")
        # pd2 = find_shortest_path_part2(end, hills)
        pd2 = find_shortest_path_generic(end, lambda position: hills[position] == ord("a"), lambda position, neighbour: hills[neighbour] >= hills[position] - 1, hills)
        print(f"Part2 {filename}: shortest distance from end to any 'a': {pd2}")

main()