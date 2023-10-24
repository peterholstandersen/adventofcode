AdventOfCode 2022, Day 9: https://adventofcode.com/2022/day/9

In short, we move a rope around according to directions specified in the input file. For part 1 of the puzzle, the
rope is only 2 element, a head and a tail. For part 2 the rope is 10 elements long.

The rest of the body follows the head according to some pre-defined rules. The task is to figure out how many positions
the tail covers when the head is moved as described in the input file.

Example input. Move three right, move two down, move one left, etc
R 3
D 2
L 1

So, eh, what fun can we get out of this puzzle rather solving it the straightforward way. First, we transform the input
to a sequence of letters instead: RRRDDL (this happens in read_file). We want to treat the input as a program, so the
letters R, D, L, R are functions which accepts a position as a parameter and returns the new position in the appropriate
direction. For example D(line, column) = (line + 1, column).

If we treat the input as a sequence of applications of the "direction functions", we just need to apply them
in order to get the new position: L(D(D(R(R(R(start)))))).

Once we define the composite functions UL, UR, DL, DR for up-left, up-right, down-left and down-right, we can specify
how the tail shall follow the head. We do this visually, so we can see that it is correctly done. The tail is at the
middle position and the head is somewhere around the tail. Suppose the head is two lines directly above the head, we
see an U meaning that the tail shall move up to follow the head. Similarly, if the head is two lines up and one column
to the right, we get an UR, meaning the tail shall move up-right.

        [UL, UL, U, UR, UR],
        [UL, _,  _,  _, UR],
        [ L, _,  _,  _, R ],
        [DL, _,  _,  _, DR],
        [DL, DL, D, DR, DR],

To summarize: to solve part 1 of the puzzle we
- read the input, turning it into a sequence of letters:    directions = "RRRDDL..."
- we then call each function in turn to move the head:      eval(directions[i])
- and then we move the tail according to the matrix above   move_tail(head, tail)

See the function part1 in rope.py or just read the meat of it here.
    for d in directions:
        head = eval(d)(head)              # d is a string, eval(d) is the function, which is applied to head
        tail = move_tail(head, tail)
        visited.add(tail)

For part 2 the rope length is 10, so the solution above needs to be generalize. Not so much fun ... but ...
what if we take the functiomania a bit further ... I want to treat the input as a program when executed will
give the answer to the puzzle. In practice, I do a small transformation of the input so that you can still
recognize it as the input, then call eval on it to get the answer.

I redefine the movement functions R, D, ... so instead of taking a single position as parameter they take a
sequence of positions denoting the entire rope, we call the sequence "body" (if it has a head and a tail and a body,
then it must be a python!). The functions R, D, ... shall return the new body _and_ the number of visited positions
by the tail. In order to collect the number of visited positions, a small bag is tied to the tail of the snake.
In the bag there is a set of positions. For example, you could have a three long snake with the head in (0,3) and
tail in (0,1) the sequence would look like [ (0,3), (0,2), (0,1), { (0,1) } ]. The last element is the bag, saying
that the tail (second but last position) has visited (0,1). Suppose the snake moves right, then we have:
[ (0,4), (0,3), (0,2), {(0,1), (0,2)} ].

In rope_fun.py we have redefined the movement functions, so that they move the entire body, then we transform the input
to a sequence of function calls as above: L(D(D(R(R(R(start)))))) take the last element of this (the bag) and see
how many position we visited ... only, Python said: "too many parentheses" ... I guess, we are not in Lisp anymore.

Oki oki, we redefine the world to fit our needs: in a sequence of functions RRRDDL, we treat the empty space between
the letters as function composition. We just need to make our own eval function :) ... problem solved, see rope_fun.py.