import time

class Timer:
    def __init__(self):
        pass

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, *args):
        print("time:", time.time() - self.start)

class Map():
    def __init__(self, filename):
        with open(filename) as file:
            self.text = file.read().strip("\n")
            self.lines = self.text.split("\n")
            self.height = len(self.lines)
            self.width = self.text.index("\n")
            self.text = self.text.replace("\n", "")
            self.rows = list(range(1, self.height + 1))
            self.cols = list(range(1, self.width + 1))
            self._all = [(row, col) for row in self.rows for col in self.cols]
            self._map = {(row, col): self.text[(row - 1) * self.width + (col - 1)] for (row, col) in self._all}

    def all(self):
        return (item for item in self._map.items())

    def __getitem__(self, pos):
        return self._map.get(pos, None)

    def __setitem__(self, pos, value):
        self._map[pos] = value

    def __contains__(self, pos):
        return pos in self._map

    def get_neighbours(self, pos, diagonal=False):
        (row, col) = pos
        rc = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)] if diagonal else [(-1,0), (1,0), (0,-1), (0,1)]
        return ((row + r, col + c) for (r, c) in rc if (row + r, col + c) in self._map)

    def get_some(self, condition):
        return {pos for pos in self._map if condition(self._map[pos])}

    def for_all(self, f):
        for pos in self._map:
            self._map[pos] = f(self._map[pos])

    def find(self, value):
        return [pos for (pos, v) in self._map.items() if v == value]

    def __str__(self, f=lambda x: x):
        return '\n'.join([ ''.join([f(self._map[(row, col)]) for col in self.cols]) for row in self.rows])


class ansi:
    green = "\u001b[32m"
    white = "\u001b[37m"
    bold = "\u001b[1m"
    reset = "\u001b[0m"
    reverse = "\u001b[7m"
    top = "\u001b[0;0H"

from itertools import chain
flatten = lambda xs: chain.from_iterable(xs)
