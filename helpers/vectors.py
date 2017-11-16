class Vec2(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return pow(x*x + y*y, 0.5) #sqrt, lol