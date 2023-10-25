# but now you need to figure out what shape to choose so the round ends as indicated

# Opponent
# A: rock
# B: paper
# C: scissors

# X means you need to lose
# Y means you need to end the round in a draw, and
# Z means you need to win.

Rock = 1
Paper = 2
Scissors = 3

Loose = 0
Draw = 3
Win = 6

# Scenarios I need to draw, Y replaced by Equals below
RockEquals = Rock + Draw
PaperEquals = Paper + Draw
ScissorsEquals = Scissors + Draw

# Scenarios I need to lose, X replaced by WinsOver below
RockWinsOver = Scissors + Loose      # Opponent has Rock, I choose scissors in order to loose
PaperWinsOver = Rock + Loose
ScissorsWinsOver = Paper + Loose

# Scenarios I need to win, Z replaced by LoosesTo below
RockLoosesTo = Paper + Win           # Opponent has Rock, I choose paper in order to win
PaperLoosesTo = Scissors + Win
ScissorsLoosesTo = Rock + Win

text = (open("big.in").read().strip().replace(" ", "").\
        replace("A", "Rock").
        replace("B", "Paper").
        replace("C", "Scissors").
        replace("X", "WinsOver").
        replace("Y", "Equals").
        replace("Z", "LoosesTo").
        split("\n"))

x = sum(map(eval, text))
print(x)

# 13600