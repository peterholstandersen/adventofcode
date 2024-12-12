import sys
import itertools

# file = "small.in"
file = "big.in"
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

part1 = sum([i*x for (i, x) in zip(itertools.count(0), get_next(filesystem))])
print("part1:", part1)  # small: 1928, big: 6331212425418

# ================= PART2 ====================

# 2 3  3  3  13  3  12 14   14   13  14   02
# 00...111...2...333.44.5555.6666.777.888899
# ---move 99--
# 2 0213  3  13  3  12 14   14   13  14   2
# 0099.111...2...333.44.5555.6666.777.8888..
# ---move 777---
# 2 0213  03 13  3  12 14   14   5    4   2
# 0099.1117772...333.44.5555.6666.....8888..
# ---
# 0099.111777244.333....5555.6666.....8888..
# 00992111777.44.333....5555.6666.....8888..

def do_part2(fs):
    index = len(fs) - 1
    while index > 0:
        (file_id, file_size) = fs[index]
        if file_id is None:
            index -= 1
            continue
        found_a_space = False
        # search the filesystem left to right for a suitable space
        for space_index in range(0, index):
            if fs[space_index][0] is not None:
                # Not a space
                continue
            (_, space_size) = fs[space_index]
            if space_size >= file_size:
                found_a_space = True
                # now "delete file", that is, chance the segment to a space.
                # There is no need to join the segment with the spaces before and after, since we will not
                # try to move a file here anymore, as we are handling files right to left in the filesystem
                fs[index] = (None, file_size)
                # "move" the file to fs[space_index] and insert the remaining space after the file
                fs[space_index] = (file_id, file_size)
                fs.insert(space_index + 1, (None, space_size - file_size))
                # ... and now we have changed the list we are working on, bad dog!
                # index is now pointing to the segment before the file, i.e., which was index - 1 before,
                # so, we leave index unchanged ... we could decrease it by one as we "know" that the fs[index]
                # should be a space, which will be skipped anyway, but that is also bad, bad dog!
                break
        if not found_a_space:
            index -= 1

def printable_id(file_id):
    if file_id is None:
        return "."
    if 0 <= file_id <= 9:
        return str(file_id)
    return "X"

def print_filesystem(filesystem):
    print("".join([printable_id(index // 2) * filesystem[index] for index in range(0, len(filesystem))]))

def print_filesystem2(fs2):
    print("".join([printable(file_id) * size for (file_id, size) in fs2]))

# Create a new filesystem with as a list of (file_id, size) where file_id = (index // 2) (spaces have no id):
# [ file_size1, space_size1, file_size2, space_size2 ] =>
# [ (0, file_size1), (None, space_size1), (1, file_size2), (None, space_size2) ]
file_id = lambda index: (index // 2) if index % 2 == 0 else None
fs2 = [ (file_id(index), filesystem[index]) for index in range(0, len(filesystem))]
do_part2(fs2)

pos = 0
checksum = 0
for index in range(0, len(fs2)):
    (file_id, size) = fs2[index]
    if file_id:
        checksum += sum(range(pos, pos + size)) * file_id
    pos += size
print("part2:", checksum) # 6363268339304
