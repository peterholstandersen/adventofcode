import os
import sys
import math

class ANSI:
    black = "\u001b[30m"
    red = "\u001b[31m"
    green = "\u001b[32m"
    yellow = "\u001b[33m"
    blue = "\u001b[34m"
    purple = "\u001b[35m"
    cyan = "\u001b[36m"
    white = "\u001b[37m"
    bold = "\u001b[1m"
    reset = "\u001b[0m"
    reverse = "\u001b[7m"
    top = "\u001b[0;0H"

def error(message):
    print(message)
    sys.exit(1)

def read_file(filename):
    with open(filename) as file:
        return file.read().strip().split("\n")

class Filesystem:
    def __init__(self, size):
        self.size = size
        self.root = Directory("/", None)
        self.cwd = self.root
        self.root.parent = self.root

    def mkdir(self, name: str):
        self.cwd.mkdir(name)

    def cd(self, dirname):
        if dirname == "/":
            self.cwd = self.root
        elif dirname == "..":
            self.cwd = self.cwd.parent
        elif dirname not in self.cwd.children:
            print(f"{dirname}: No such file or directory")
        elif isinstance(self.cwd.children[dirname], File):
            print(f"{dirname}: Not a directory")
        else:
            self.cwd = self.cwd.children[dirname]

    def fallocate(self, filename, size):
        self.cwd.fallocate(filename, size)

    def ls(self):
        self.cwd.ls()

    def ll(self):
        self.cwd.ll()

    def get_current_pathname(self):
        return "/" if self.cwd == self.root else self.cwd.get_pathname()

    def du(self, limit=math.inf, silent=False):
        return self.cwd.du(limit, silent)

    # Filesystem     1K-blocks     Used Available Use% Mounted on
    # /dev/nvme0n1p2 237280828 43803660 181397860  20% /
    def df(self):
        used = self.root.du(limit=math.inf, silent=True)
        print(f"Filesystem      Size     Used Available Use% Mounted on")
        print(f"/dev/nice   {self.size} {used} {self.size-used}    {round(used / self.size * 100.0)} /")

    def part1(self, limit):
        all_directories = dict()
        self.root.part1(all_directories)
        print(all_directories)
        result = sum( [size for size in all_directories.values() if size <= limit])
        print("Result part1:", result)

    def part2(self, needed_space):
        self.df()
        used = self.root.du(limit=math.inf, silent=True)
        free = self.size - used
        print(f"Need {needed_space} bytes. Have {free} free bytes. Lack {needed_space - free}")
        all_directories = dict()
        self.root.part1(all_directories)
        sizes = sorted(all_directories.values())
        for size in sizes:
            if size > needed_space - free:
                print(f"Size of directory to delete: {size}")
                return
        print(f"Didn't find a directory?")

    def __str__(self):
        return self.root.__str__()

class Directory:
    def __init__(self, dirname, parent):
        self.name = dirname
        self.children = dict()
        self.parent = parent

    def fallocate(self, filename, size):
        if filename in self.children:
            error(f"filename: `{filename}': File exists")
        self.children[filename] = File(filename, size)

    def mkdir(self, dirname: str):
        if dirname in self.children:
            error(f"dirname: cannot create direction `{dirname}': File exists")
        self.children[dirname] = Directory(dirname, self)

    def ls(self):
        for child in self.children.values():
            if isinstance(child, Directory):
                print(f"{ANSI.green}{child}{ANSI.reset}")
            else:
                print(f"{child.name}")

    def ll(self):
        for child in self.children.values():
            if isinstance(child, Directory):
                print(f"{ANSI.green}{child}{ANSI.reset}")
            else:
                print(f"{child.name:<10} {child.size:>10}")

    def get_pathname(self):
        if self.parent is None or self.parent == self:
            return ""
        else:
            return self.parent.get_pathname() + "/" + self.name

    def du(self, limit=math.inf, silent=False):
        total_size = 0
        for child in self.children.values():
            if isinstance(child, Directory):
                child_size = child.du(limit, silent)
                total_size += child_size
            elif isinstance(child, File):
                total_size += child.size
        if total_size < limit and not silent:
            print(f"{total_size:<10} {self.get_pathname()}")
        return total_size

    def part1(self, all_directories):
        total_size = 0
        for child in self.children.values():
            if isinstance(child, Directory):
                child_size = child.part1(all_directories)
                total_size += child_size
            elif isinstance(child, File):
                total_size += child.size
        all_directories[self.get_pathname()] = total_size
        return total_size

    def __str__(self):
        return self.name

class File:
    def __init__(self, name, size):
        self.name = name
        self.size = int(size)

    def __str__(self):
        return f"{self.name} {self.size}"


def main():
    # commands = read_file("small.in")
    commands = read_file("big.in")
    fs = Filesystem(70000000) # 70 million bytes

    for command in commands:
        match command.split(" "):
            case ["$", "cd", dirname]: fs.cd(dirname)   # also covers / and ..
            case ["$", "ls"]: pass
            case ["dir", dirname]: fs.mkdir(dirname)
            case [size, filename]: fs.fallocate(filename, size)
            case _: error(f"unknown command: {command}")

    fs.cd("/")

    while True:
        cmd = input(f"python:{fs.get_current_pathname()}$ ")
        match cmd.split(" "):
            case ["pwd", *_]:  print(fs.cwd)
            case ["ls", "-l"]: fs.ll()
            case ["ll", *_]: fs.ll()
            case ["l", *_]: fs.ls()
            case ["ls", *_]: fs.ls()
            case ["exit", *_]: sys.exit(1)
            case ["moria", *_]: print("sorry games are not allowed right now")
            case ["cd"]: fs.cd("/")
            case ["cd", dirname]: fs.cd(dirname)
            case ["cd", *_]: print("cd: too many arguments")
            case ["du"]: fs.du()
            case ["du", arg]: fs.du(limit=int(arg))
            case ["du", *_]: print("du: not supported")
            case ["df", *_]: fs.df()
            case ["rm", *_]: print("I cannot do that, Dave")
            case ["part1"]: fs.part1(100000)
            case ["part2"]: fs.part2(30000000)
            # case _: os.system(cmd)
            case _: print(f"{cmd}: command not found")


if __name__ == "__main__":
    main()