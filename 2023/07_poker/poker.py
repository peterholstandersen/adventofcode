from itertools import product
from collections import Counter

five_of_a_kind = lambda hand: len(Counter(hand)) == 1
four_of_a_kind = lambda hand: Counter(hand).most_common(1)[0][1] == 4
full_house = lambda hand: [x for (_, x) in Counter(hand).most_common(2) ] == [3, 2]
three_of_a_kind = lambda hand: Counter(hand).most_common(1)[0][1] == 3
two_pair = lambda hand: [x for (_, x) in Counter(hand).most_common(2) ] == [2, 2]
one_pair = lambda hand: Counter(hand).most_common(1)[0][1] == 2

def hand_rank(hand):
    if five_of_a_kind(hand):    return 1
    elif four_of_a_kind(hand):  return 2
    elif full_house(hand):      return 3
    elif three_of_a_kind(hand): return 4
    elif two_pair(hand):        return 5
    elif one_pair(hand):        return 6
    else:                       return 7

# Jacks are wild
def hand_rank2(hand):
    replace = lambda x: "AKQT98765432" if x == "J" else x
    foo = list(map(replace, hand))
    bar = product(foo[0], foo[1], foo[2], foo[3], foo[4])
    return min(map(hand_rank, bar))

card_rank = lambda x: "AKQJT98765432".index(x)
card_rank2 = lambda x: 13 if x == "J" else card_rank(x)

lines = [line.split(" ") for line in open("big.in").read().strip().split("\n")]

foo = [(hand_rank(hand), tuple(map(card_rank, hand)), int(bid)) for [hand, bid] in lines]
part1 = sum([rank * bid for (rank, (_,_,bid)) in zip(range(1, len(foo) + 1), sorted(foo, reverse=True))])
print("part1", part1) # 253313241

foo = [(hand_rank2(hand), tuple(map(card_rank2, hand)), int(bid)) for [hand, bid] in lines]
part2 = sum([rank * bid for (rank, (_,_,bid)) in zip(range(1, len(foo) + 1), sorted(foo, reverse=True))])
print("part2", part2) # 253362743
