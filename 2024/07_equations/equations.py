import sys
import itertools as it
import operator as op

#file = "small.in"
file = "big.in"
equations = [(x, y.strip().split(" ")) for [x,y] in [line.split(":") for line in open(file) ]]

def doit(opps):
    final_sum = 0
    for (result, numbers) in equations:
        opss = [opps] * (len(numbers) - 1)
        for ops in it.product(*opss):
            equation = numbers[0]
            for i in range(1, len(numbers)):
                equation = ops[i - 1] + "(" + equation + "," + numbers[i] + ")"
            equation += " == " + result
            if eval(equation):
                print(equation)
                final_sum += int(result)
                break
    return final_sum

concatenate = lambda x, y: int(str(x) + str(y))

# print("part1:", doit(('op.mul', 'op.add'))) # 10741443549536
# print("part2:", doit(('op.mul', 'op.add', 'concatenate'))) # 500335179214836 ... very slow :)

def ok(result, numbers, operators, result_so_far):
    if result_so_far > result:
        return False
    if numbers == []:
        return result_so_far == result
    for op in operators:
        if ok(result, numbers[1:], operators, op(result_so_far, numbers[0])):
            return True
    return False

equations = [ (int(result), list(map(int, numbers))) for (result, numbers) in equations ]

doit2 = lambda operators: sum([result for (result, numbers) in equations if ok(result, numbers, operators, 0)])

print("part1:", doit2((op.add, op.mul))) # 10741443549536
print("part2:", doit2((op.add, op.mul, concatenate))) # 500335179214836 ... faster!
