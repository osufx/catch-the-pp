import sys

from osu.Beatmap import Beatmap
from osu.ctb.difficulty import Difficulty
from ppCalc import calculatePP

if len(sys.argv) <= 1:
    beatmap = Beatmap("test.osu") #Yes... this be my test file (Will remove when project is done)
else:
    beatmap = Beatmap(sys.argv[1])

if len(sys.argv) >= 3:
    mods = int(sys.argv[2])
else:
    mods = 0
difficulty = Difficulty(beatmap, mods)

print("Stars: {}".format(difficulty.starRating))
print("PP: {}".format(calculatePP(difficulty, 1, 300, 0)))