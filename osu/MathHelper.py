def Clamp(value, mn, mx):
    return min(max(mn, value), mx)

def Sign(value):
    if value == 0:
        return 0
    elif value > 0:
        return 1
    else:
        return -1

def Cpn(p, n):
    if p < 0 or p > n:
        return 0
    p = min(p, n - p)
    out = 1
    for i in range(1, p + 1):
        out = out * (n - p + i) / i
    
    return out

def Catmull(p, t): # WARNING:   Worst math formula incomming
    return 0.5 * ( (2 * p[1]) + (-p[0] + p[2]) * t + (2 * p[0] - 5 * p[1] + 4 * p[2] - p[3]) * pow(t, 2) + (-p[0] + 3 * p[1] - 3 * p[2] + p[3]) * pow(t, 3) )

class Vec2(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return pow(x*x + y*y, 0.5) #sqrt, lol
    
    def calc(self, value, other):
        x = self.x + value * other.x
        y = self.y + value * other.y
        return Vec2(x, y)