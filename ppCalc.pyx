import math

cpdef calculate_pp(diff, accuracy, combo, miss):
    """
    Calculate pp for gameplay

    diff        -- Difficulty object
    accuracy    -- Accuracy of the play             (Float 0-1)
    combo       -- MaxCombo achived during the play (Int)
    miss        -- Amount of misses during the play (Int)
    return      -- Total pp for gameplay
    """
    cdef float pp = (((5 * diff.star_rating / 0.0049) - 4) ** 2) / 100000
    cdef float length_bonus = 0.95 + 0.4 * min(1, combo / 3000)
    if combo > 3000:
        length_bonus += math.log10(combo / 3000) * 0.5

    pp *= length_bonus
    pp *= (0.97 ** miss)
    pp *= min((combo ** 0.8) / (diff.beatmap.max_combo ** 0.8), 1)

    if diff.beatmap.difficulty["ApproachRate"] > 9:
        pp *= 1 + 0.1 * (diff.beatmap.difficulty["ApproachRate"] - 9)
    if diff.beatmap.difficulty["ApproachRate"] < 8:
        pp *= 1 + 0.025 * (8 - diff.beatmap.difficulty["ApproachRate"])

    if diff.mods & 1 << 3 > 0:    #HD
        pp *= 1.05 + 0.075 * (10 - min(10, diff.beatmap.difficulty["ApproachRate"]))

    if diff.mods & 1 << 10 > 0:    #FL
        pp *= 1.35 * length_bonus

    pp *= (accuracy ** 5.5)

    if diff.mods & 1 << 0 > 0:    #NF
        pp *= 0.9

    if diff.mods & 1 << 12 > 0:    #SO
        pp *= 0.95

    return pp
