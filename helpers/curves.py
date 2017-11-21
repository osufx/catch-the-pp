from osu import MathHelper

class Linear(object):   #Because it made sense at the time...
    def __init__(self, points):
        self.pos = points

class Bezier(object):
    def __init__(self, points, use_anchorpoints = False):
        self.points = points
        self.order = len(points)
        self.step = 0.0025 / self.order
        self.pos = []
        self.anchor = use_anchorpoints
        self.calc_points()

    def calc_points(self):
        if len(self.pos) != 0:  #This should never happen but since im working on this I want to warn myself if I fuck up
            raise Exception("Bezier was calculated twice!")

        i = 0
        n = self.order - 1
        while i < 1 + self.step:
            x = 0
            y = 0

            for p in range(n + 1):
                a = MathHelper.cpn(p, n) * pow((1 - i), (n - p)) * pow(i, p)
                x += a * self.points[p].x
                y += a * self.points[p].y

            point = MathHelper.Vec2(x, y)
            self.pos.append(point)
            i += self.step
    
    def point_at_distance(self, length):
        return {
            0: False,
            1: self.points[0],
        }.get(self.order, self.rec(length))
    
    def rec(self, length):
        return MathHelper.point_at_distance(self.pos, length)

class Catmull(object):  #Yes... I cry deep down on the inside aswell
    def __init__(self, points):
        self.points = points
        self.order = len(points)
        self.step = 0.025
        self.pos = []
        self.calc_points()

    def calc_points(self):
        if len(self.pos) != 0:  #This should never happen but since im working on this I want to warn myself if I fuck up
            raise Exception("Catmull was calculated twice!")

        for x in range(self.order - 1):
            t = 0
            while t < self.step + 1:
                if x >= 1:
                    v1 = self.points[x - 1]
                else:
                    v1 = self.points[x]

                v2 = self.points[x]

                if x + 1 < self.order:
                    v3 = self.points[x + 1]
                else:
                    v3 = v2.calc(1, v2.calc(-1, v1))

                if x + 2 < self.order:
                    v4 = self.points[x + 2]
                else:
                    v4 = v3.calc(1, v3.calc(-1, v2))

                point = get_point([v1, v2, v3, v4], t)
                self.pos.append(point)
                t += self.step

def get_point(p, length):
    x = MathHelper.catmull([o.x for o in p], length)
    y = MathHelper.catmull([o.y for o in p], length)
    return MathHelper.Vec2(x, y)
