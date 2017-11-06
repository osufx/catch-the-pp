def Clamp(value, mn, mx):
    return min(max(mn, value), mx)

def Sign(value):
    if value == 0:
        return 0
    elif value > 0:
        return 1
    else:
        return -1

class Vec2(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
