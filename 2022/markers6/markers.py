from typing import Optional

def get_input(filename):
    # return "mjqjpqmgbljsphdztnvjfqwrcgsmlb" # _, 19
    # return "bvwbjplbgvbhsrlpgdmjqwftvncz"  # 5, 23
    # return "nppdvjthqldpwncqszvftbrmjlhg"  # 6, 23
    # return "nznrnfrfntjfmvfwmzdfjlvtqnbhcprsg" # 10, 29
    # return "zcfzfwzzqfrljwzlrfnpqdbhtmscgvjw" # 11, 26
    with open(filename) as file:
        return file.read().strip()

def find_marker(text: str, length: int) -> Optional[int]:
    for i in range(length, len(text)):
        ok = True
        for x in range(1, length):
            for y in range(x+1, length+1):
                if text[i-x] == text[i-y]:
                    ok = False
                    break # from y loop
            if not ok:
                break # from x loop
        if ok:
            return i
    return None

def find_marker_length4(text: str) -> Optional[int]:
    for i in range(4, len(text) - 4):
        if (text[i-1] != text[i-2] and text[i-1] != text[i-3] and text[i-1] != text[i-4] and
            text[i-2] != text[i-3] and text[i-2] != text[i-4] and
            text[i-3] != text[i-4]):
            return i
    return None

def find_marker_mark2(text: str, length: int) -> Optional[int]:
    for i in range(length, len(text)):
        if all( [ text[i-x] != text[i-y] for x in range(1, length) for y in range(x+1, length+1) ] ):
            return i
    return None

def main():
    text = get_input("big.in")
    print("part1", find_marker_length4(text))
    print("part1", find_marker(text, 4)) # 1640
    print("part2", find_marker(text, 14)) # 3613
    print("part2b", find_marker_mark2(text, 14))

if __name__ == "__main__":
    main()

