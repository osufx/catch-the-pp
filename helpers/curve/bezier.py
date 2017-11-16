from helpers import vectors, mathhelper

class Bezier(object):
    #Array of vec2
    def __init__(self, points):
        self.points = points
        self.order = len(points)
        self.step = 0.0025 / self.order
        self.pos = []
        self.calcPoints()

    def calcPoints(self):
        if len(self.pos) != 0:  #This should never happen but since im working on this I want to warn myself if I fuck up
            raise Exception("Bezier was calculated twice!")

        i = 0
        n = self.order - 1
        while i < 1 + self.step:
            x = 0
            y = 0
            
            for p in range(n + 1):
                a = mathhelper.Cpn(p, n) * pow((1 - i), (n - p)) * pow(i, p)
                x += a * self.points[p].x
                y += a * self.points[p].y
            
            point = vectors.Vec2(x, y)
            self.pos.append(point)
            i += self.step