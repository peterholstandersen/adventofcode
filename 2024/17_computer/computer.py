import sys

# Combo operands 0 through 3 represent literal values 0 through 3.
# Combo operand 4 represents the value of register A.
# Combo operand 5 represents the value of register B.
# Combo operand 6 represents the value of register C.
# Combo operand 7 is reserved and will not appear in valid programs.
#
# The adv instruction (opcode 0) performs division. The numerator is the value in the A register. The denominator is found by raising 2 to the power of the instruction's combo operand.
# (So, an operand of 2 would divide A by 4 (2^2); an operand of 5 would divide A by 2^B.) The result of the division operation is truncated to an integer and then written to the A register.
# A = A // pow(2, combo)
#
# The bxl instruction (opcode 1) calculates the bitwise XOR of register B and the instruction's literal operand, then stores the result in register B.
# B = B xor literal
#
# The bst instruction (opcode 2) calculates the value of its combo operand modulo 8 (thereby keeping only its lowest 3 bits), then writes that value to the B register.
# B = combo % 8
#
# The jnz instruction (opcode 3) does nothing if the A register is 0. However, if the A register is not zero, it jumps by setting the instruction pointer to the value of its literal operand; if this instruction jumps, the instruction pointer is not increased by 2 after this instruction.
# if A != 0: instruction_pointer = literal
#
# The bxc instruction (opcode 4) calculates the bitwise XOR of register B and register C, then stores the result in register B. (For legacy reasons, this instruction reads an operand but ignores it.)
# B = B xor C
# remember to skip operand to get to the next instruction
#
# The out instruction (opcode 5) calculates the value of its combo operand modulo 8, then outputs that value. (If a program outputs multiple values, they are separated by commas.)
# print(combo % 8)
#
# The bdv instruction (opcode 6) works exactly like the adv instruction except that the result is stored in the B register. (The numerator is still read from the A register.)
# B = A // pow(2, combo)
#
# The cdv instruction (opcode 7) works exactly like the adv instruction except that the result is stored in the C register. (The numerator is still read from the A register.)
# C = A // pow(2, combo)

def runit(program, A, B, C):
    out = []
    pc = 0
    while pc < len(program):
        combo = lambda x: [x, x, x, x, A, B, C][x]
        x = program[pc+1]
        match program[pc]:
            case 0: A = A >> combo(x) # A = A // pow(2, combo(x))
            case 1: B = B ^ x
            case 2: B = combo(x) %  8
            case 4: B = B ^ C
            case 5: out.append(combo(x) % 8)
            case 6: B = A >> combo(x) # B = A // pow(2, combo(x))
            case 7: C = A >> combo(x) # C = A // pow(2, combo(x))
            case 3:
                if A != 0:
                    pc = x
                    continue
            case _: print("error"); sys.exit(1)
        pc += 2
    return (A, B, C, out)

# input as given by the puzzle
program = [2, 4, 1, 2, 7, 5, 0, 3, 4, 7, 1, 7, 5, 5, 3, 0]
A_initial_value_part1 = 30878003
print("program:", program)
print("A initial value:", A_initial_value_part1)

end_state = runit(program, A_initial_value_part1, 0, 0)
part1 = ",".join(map(str, end_state[3]))
print("part1:", part1) # 7,1,3,7,5,1,0,3,4
print()

def decompile(program):
    pc = 0
    while pc < len(program):
        x = program[pc+1]
        combo = lambda x: [str(x), str(x), str(x), str(x), 'A', 'B', 'C'][x]
        match program[pc]:
            case 0: print(f"A = A >> {combo(x)}")
            case 1: print(f"B = B ^ {x}")
            case 2: print(f"B = {combo(x)} % 8")
            case 4: print(f"B = B ^ C")
            case 5: print(f"out({combo(x)} % 8)")
            case 6: print(f"B = A >> {combo(x)}")
            case 7: print(f"C = A >> {combo(x)}")
            case 3: print(f"goto {x} if A != 0")
            case _: print("error"); sys.exit(1)
        pc += 2

# program = [2, 4, 1, 2, 7, 5, 0, 3, 4, 7, 1, 7, 5, 5, 3, 0]
#
# decompile(program)
# sys.exit(1)
#
# B = A % 8        (get input)                   B = A
# B = B ^ 2        (flip bit 2 of input)         B = A ^ 2
# C = A >> B       (C = input shifted down)      C = A >> (A ^ 2)
# A = A >> 3       (next input)
# B = B ^ C        (calculate stuff)             B = (A ^ 2) ^ (A >> (A ^ 2))
# B = B ^ 7        (calculate more stuff)        B = (A ^ 2) ^ (A >> (A ^ 2)) ^ 7
# out(B % 8)
# goto 0 if A != 0

# determine which input for A will result in the program outputting itself.
def doit_again():
    # program2 is the program without the loop at the end
    program2 = program[0:-2] # [2, 4, 1, 2, 7, 5, 0, 3, 4, 7, 1, 7, 5, 5]
    result = 0
    for output in program[-1::-1]:
        found = False
        for input1 in range(0, 8):
            test = runit(program2, result * 8 + input1, 0, 0)
            # print(test, test[3][-1])
            if test[3][-1] == output:
                result = result * 8 + input1
                found = True
                break
        if not found:
            print("error")
            sys.exit(1)
    print("doit_again: A:", result)

doit_again()
sys.exit(1)

def fun(A):
    B = A % 8
    B = B ^ 2    # B in range 0-7
    C = A >> B   # C = A shifted down 0-7 times [so we use 3 bits somewhere in A], meaning C[0:3] = A[X:X+3]
    B = B ^ C    # only the 3 lowest bits of C are relevant
    B = B ^ 7
    return B % 8

result = 0
out = program.copy()
for output in program[-1::-1]:
    # print("--- looking for output:", output, "result so far:", result)
    found = False
    for input1 in range(0, 8):
        test = fun(result * 8 + input1)
        # print("input1", input1, "test:", test)
        if test == output:
            # print("found one for input:", input1)
            result = result * 8 + input1
            found = True
            break
    if not found:
        print("error")
        sys.exit(1)
print("result for part2 using 'fun'. A =", result) # A = 190384113204239

A = result
print("========= test using 'fun',   A =", A)
out = []
while A > 0:
    out.append(fun(A))
    A = A // 8
print("output 'fun':", out)     # must equal program
print("program:     ", program)
print()

A = result
print("========= test using 'runit', A =", A)
x = runit(program, A, 0, 0)
print("ouput 'runit':", x[3])
print("program:      ", program)
print()

sys.exit(1)

# ===========================
# trying to figure out how to run the program backwards, but the part
# where A is shifted down a variable number of times makes it difficult

def fun2(A0):
    # lowest 3 bits of A0 = 0b010
    B0 = A0 & 0b111    # A0 = 010, B0 = 010,            C0=?
    B1 = B0 ^ 0b010    # A0 = 010, B1 = 000,            C0=?
    C0 = A0 >> B1      # A0 = 010, B1 = 000,            C0 = 010
    B2 = B1 ^ C0       # A0 = 010, B2 = B1^C0 = 010,    C0 = 010
    B3 = B2 ^ 0b111    # B2 = 011, B3 = B2^111 = 101, C0 = 010
    return B3 & 0b111  # returns B3 & 111 = 101

# work in progress
def reverse(program):
    pc = len(program) - 2
    while pc >= 0:
        x = program[pc+1]
        combo = lambda x: [str(x), str(x), str(x), str(x), 'A', 'B', 'C'][x]
        match program[pc]:
            case 0: print(f"A << {combo(x)}")
            case 1: print(f"B = B ^ {x}")
            case 2:
                if x < 4:
                    print(f"unhandled")
                    sys.exit(1)
                c = combo(x)
                print(f"{c}0,{c}1,{c}2 = B0,B1,B2")
            case 4: print(f"B = B ^ C (same?)")
            case 5:
                if x < 4:
                    print("unhandled")
                    sys.exit(1)
                c = combo(x)
                print(f"{c}0,{c}1,{c}2 = input or stop")
            case 6:
                # B = A << combo(x)
                c = combo(x)
                if x != 3:
                    print("unhandled")
                    sys.exit(1)
                # B =
                print(f"A0,A1,A2 = ")
            case 7: print(f",,, C << {combo(x)}")
            case 3: print(f"loop")
            case _: print("error"); sys.exit(1)
        pc -= 2
