import math

def GetPP(diff, accuracy, combo, miss, mods):
    pp = pow(((5 * diff.starRating / 0.0049) - 4), 2) / 100000
    lengthBonus = 0.95 + 0.4 * min(1, combo / 3000)
    if combo > 3000:
        lengthBonus += math.log10(combo / 3000) * 0.5
    
    pp *= lengthBonus
    pp *= pow(0.97, miss)
    pp *= min(pow(combo, 0.8) / pow(diff.beatmap.objectCount, 0.8), 1)

    if diff.beatmap.difficulty["ApproachRate"] > 9:
        pp *= 1 + 0.1 * (diff.beatmap.difficulty["ApproachRate"] - 9)
    if diff.beatmap.difficulty["ApproachRate"] < 8:
        pp *= 1 + 0.025 * (8 - diff.beatmap.difficulty["ApproachRate"])

    if diff.mods & 1 << 4 > 0:    #HD
        pp *= 1.05 + 0.075 * (10 - min(10, diff.beatmap.difficulty["ApproachRate"]))
    
    if diff.mods & 1 << 4 > 0:    #FL
        pp *= 1.35 * lengthBonus
    
    pp *= pow(accuracy, 5.5)

    if diff.mods & 1 << 4 > 0:    #NF
        pp *= 0.9
    
    if diff.mods & 1 << 4 > 0:    #SO
        pp *= 0.95
    
    return pp
