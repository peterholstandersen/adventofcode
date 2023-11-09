class Map():
    def __init__(self, filename):
        with open(filename) as file:
            self.text = file.read().strip("\n")
            self.lines = self.text.split("\n")
            self.height = len(self.lines)
            self.width = self.text.index("\n")
            self.text = self.text.replace("\n", "")
            self.rows = [ row for row in range(1, self.height + 1) ]
            self.cols = [ col for col in range(1, self.width + 1)]
            self.all = [ (row, col) for row in self.rows for col in self.cols ]
            self.map = { (row, col): int(self.text[(row - 1) * self.width + (col - 1)]) for (row, col) in self.all }

    def get_neighbours(self, pos):
        (row, col) = pos
        return [ (row + r, col + c) for (r,c) in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)] if (row + r, col + c) in self.map ]

    def get_some(self, condition):
        return { pos for pos in self.map if condition(self.map[pos]) }

    def for_all(self, f):
        for pos in self.map:
            self.map[pos] = f(self.map[pos])

    def __str__(self):
        f = lambda x: str(9 if x > 9 else x)
        return '\n'.join([ ''.join([ f(self.map[(row, col)]) for col in self.cols ]) for row in self.rows ])

# part1 result is the total number of flashes after 100 steps
# part2 result is step count when all octopuses flash in one step for the first time
def doit(filename, part1_expected, part2_expected):
    octopuses = Map(filename)
    octo = octopuses.map
    total_flashes = 0
    for step in range(1000):
        if step == 100:
            part1_result = total_flashes
        octopuses.for_all(lambda x: x + 1)
        do_flash = octopuses.get_some(lambda x: x > 9)
        this_step = 0
        while len(do_flash) > 0:
            pos = do_flash.pop()
            if octo[pos] != 0:
                total_flashes += 1
                this_step += 1
                octo[pos] = 0
                for n in octopuses.get_neighbours(pos):
                    if octo[n] != 0:
                        octo[n] += 1
                    if octo[n] > 9:
                        do_flash.add(n)
        if this_step == 100:
            break

    part2_result = step + 1
    print("part1", filename, part1_result)
    print("part2", filename, part2_result)
    assert(part1_result == part1_expected)
    assert(part2_result == part2_expected)


if __name__ == "__main__":
    doit("small.in", 1656, 195)
    doit("big.in", 1683, 788)