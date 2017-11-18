from osu import MathHelper

#Yes... I cry deep down on the inside aswell
class Catmull(object):
    def __init__(self, points):
        self.points = points
        self.order = len(points)
        self.step = 0.025
        self.pos = []
        self.calcPoints()

    def calcPoints(self):
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

                point = getPoint([v1, v2, v3, v4], t)
                self.pos.append(point)
                t += self.step

def getPoint(p, length):
    x = MathHelper.catmull([o.x for o in p], length)
    y = MathHelper.catmull([o.y for o in p], length)
    return MathHelper.Vec2(x, y)