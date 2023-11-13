def sums_of(numbers):
    return (x + y for x in numbers for y in numbers)

def part1(filename):
    numbers = list(map(int, open(filename).read().strip().split("\n")))
    result = None
    for n in range(25, len(numbers)):
        if numbers[n] not in sums_of(numbers[n-25:n]):
            result = numbers[n]
            break
    print("part1", filename, result)

def part2(filename):
    numbers = list(map(int, open(filename).read().strip().split("\n")))
    xxx = None
    for n in range(25, len(numbers)):
        if numbers[n] not in sums_of(numbers[n-25:n]):
            xxx = numbers[n]
            break
    for n in range(2, len(numbers)):
        for i in range(n, len(numbers)):
            if sum(numbers[i-n:i]) == xxx:
                xx = min(numbers[i-n:i])
                yy = max(numbers[i-n:i])
                print("part2", filename, xx + yy)

if __name__ == "__main__":
    part1("big.in") # 90433990
    part2("big.in") # 11691646
