import sys
import itertools

file = "small.in"
# file = "big.in"
filesystem = list(map(int, open(file).read().strip()))

def get_next(filesystem):
    # every other position denotes a file size and a free space respectively
    files = [filesystem[i] for i in range(0, len(filesystem), 2)]
    free_space = [filesystem[i] for i in range(1, len(filesystem), 2)]
    file_index1 = 0  # also the id
    file_index2 = len(files) - 1
    space_index = 0
    consume_from_front = True
    while files[file_index1] > 0 or files[file_index2] > 0:
        if consume_from_front:
            if files[file_index1] == 0:
                # end of file
                consume_from_front = False
                file_index1 += 1
                continue
            # Take from the front file (does not consume empty spaces)
            files[file_index1] -= 1
            yield file_index1
        else:
            # consume from back
            if files[file_index2] == 0:
                # end of file, continue with the next file
                file_index2 -= 1
                continue
            if free_space[space_index] == 0:
                space_index += 1
                consume_from_front = True
                continue
            # Take from back file (and consume empty space)
            files[file_index2] -= 1
            free_space[space_index] -= 1
            yield file_index2




# part1 = sum([i*x for (i, x) in zip(itertools.count(0), get_next(filesystem))])
# print("part1:", part1)  # small: 1928, big: 6331212425418

def get_file(filesystem, index):
    current_id = filesystem[index] if 0 <= index < len(filesystem) else None
    end = index - 1
    while end > 0 and (filesystem[end] == current_id or filesystem[end] == "."):
        end -= 1
    if end == -1:
        return None
    file_id = filesystem[end]
    start = end
    while start > 0 and filesystem[start] == file_id:
        start -= 1
    start += 1
    return (start, end)

def find_slot(filesystem, file):
    file_size = file[1] - file[0] + 1
    # search from left-to-right (front-to-back) for a large enough slot
    index = 0
    while True:
        while index < len(filesystem) and filesystem[index] != ".":
            index += 1
        if index == len(filesystem):
            return None
        start = index
        print("slot start:", start)
        while index < len(filesystem) and filesystem[index] == ".":
            index += 1
        end = index - 1
        slot_size = end - start + 1
        if slot_size >= file_size:
            return (start, end)
    return None

def move_file(filesytem, file, slot):
    file_size = file[1] - file[0] + 1
    file_index = file[0]
    slot_index = slot[0]
    for n in range(0, file_size):
        filesystem[slot_index + n] = filesystem[file_index + n]
        filesystem[file_index + n] = "."

def doit2(filesystem):
    while True:
        index = len(filesystem)
        while index > 0:
            file = get_file(filesystem, index)
            if not file:
                break
            (start, end) = file
            print("file:", file, "".join(filesystem[start:end + 1]))
            slot = find_slot(filesystem, file)
            print("slot:", slot)
            if slot:
                move_file(filesystem, file, slot)
                print("".join(filesystem))
            index = file[0]

# print(filesystem)
filesystem = [ (str((index + 1) // 2) if index % 2 == 0 else ".") * filesystem[index] for index in range(0, len(filesystem)) ]
filesystem = list("".join(filesystem))
# print(filesystem)
print("".join(filesystem))

doit2(filesystem)

sys.exit(1)


sys.exit(1)

# part2 = sum([i*x for (i, x) in zip(itertools.count(0), get_next2(filesystem))])
# print("part2:", part2)





# ==== Junk

def get_next2(filesystem):
    # every other position denotes a file size and a free space respectively
    index1 = 0
    index2 = len(filesystem) - 1
    while index1 < index2:
        if index1 % 2 == 0:
            # print("regular file")
            # regular file
            yield from itertools.repeat((index1 + 1) // 2, filesystem[index1])
            index1 += 1
            continue
        # print("empty space")
        # empty space: find a file that fits, searching from the right
        while filesystem[index2] > filesystem[index1] and index2 >= 0:
            index2 -= 2
        if index2 < 0:
            break
        yield from itertools.repeat((index2 + 1) // 2, filesystem[index2])
        yield from itertools.repeat(".", filesystem[index1] - filesystem[index2])
        index2 -= 2
        index1 += 1
    yield -1
