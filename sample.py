import sys

from osu.Beatmap import Beatmap
from starCalc import DifficultyCTB
from ppCalc import GetPP

if len(sys.argv) <= 1:
    beatmap = Beatmap("test.osu") #Yes... this be my test file (Will remove when project is done)
else:
    beatmap = Beatmap(sys.argv[1])

if len(sys.argv) >= 3:
    mods = int(sys.argv[2])
else:
    mods = 0
calc = DifficultyCTB(beatmap, mods)

print("Stars: {}".format(calc.GetStars()))
print("PP: {}".format(GetPP(calc, 1, 300, 0, 0)))