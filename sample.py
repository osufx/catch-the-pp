import sys

import catchthepp

if len(sys.argv) <= 1:
    beatmap = catchthepp.Beatmap("test.osu") #Yes... this be my test file (Will remove when project is done)
else:
    beatmap = catchthepp.Beatmap(sys.argv[1])

if len(sys.argv) >= 3:
    mods = int(sys.argv[2])
else:
    mods = 0

difficulty = catchthepp.Difficulty(beatmap, mods)
print("Calculation:")
print("Stars: {}, PP: {}, MaxCombo: {}\n".format(difficulty.star_rating, catchthepp.calculate_pp(difficulty, 1, beatmap.max_combo, 0), beatmap.max_combo))

"""
m = {"NOMOD": 0, "EASY": 2, "HIDDEN": 8, "HARDROCK": 16, "DOUBLETIME": 64, "HALFTIME": 256, "FLASHLIGHT": 1024}
for key in m.keys():
    difficulty = Difficulty(beatmap, m[key])
    print("Mods: {}".format(key))
    print("Stars: {}".format(difficulty.star_rating))
    print("PP: {}\n".format(calculate_pp(difficulty, 1, beatmap.max_combo, 0)))
"""
