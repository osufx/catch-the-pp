import math
from .. import constants
from . import mathhelper

class Linear(object):   #Because it made sense at the time...
    def __init__(self, points):
        self.pos = points

cdef class Bezier(object):
    cdef public list points, pos
    cdef public int order

    def __init__(self, points):
        self.points = points
        self.order = len(self.points)
        self.pos = []
        self.calc_points()

    cpdef calc_points(self):
        if len(self.pos) != 0:  #This should never happen but since im working on this I want to warn myself if I fuck up
            raise Exception("Bezier was calculated twice!")

        cdef list sub_points = []
        for i in range(len(self.points)):
            if i == len(self.points) - 1:
                sub_points.append(self.points[i])
                self.bezier(sub_points)
                sub_points.clear()
            elif len(sub_points) > 1 and self.points[i] == sub_points[-1]:
                self.bezier(sub_points)
                sub_points.clear()

            sub_points.append(self.points[i])

    cpdef bezier(self, list points):
        cdef int order = len(points)
        cdef float step = 0.25 / constants.SLIDER_QUALITY / order    #Normaly 0.0025
        cdef float i = 0
        cdef int n = order - 1

        cdef float x, y
        cdef int p

        while i < 1 + step:
            x = 0
            y = 0

            for p in range(n + 1):
                a = mathhelper.cpn(p, n) * ((1 - i) ** (n - p)) * (i ** p)
                x += a * points[p].x
                y += a * points[p].y

            point = mathhelper.Vec2(x, y)
            self.pos.append(point)
            i += step

    def point_at_distance(self, length):
        return {
            0: False,
            1: self.points[0],
        }.get(self.order, self.rec(length))

    def rec(self, length):
        return mathhelper.point_at_distance(self.pos, length)

cdef class Catmull(object):  #Yes... I cry deep down on the inside aswell
    cdef public list points, pos
    cdef public int order
    cdef public float step

    def __init__(self, points):
        self.points = points
        self.order = len(points)
        self.step = 2.5 / constants.SLIDER_QUALITY    #Normaly 0.025
        self.pos = []
        self.calc_points()

    cpdef calc_points(self):
        if len(self.pos) != 0:  #This should never happen but since im working on this I want to warn myself if I fuck up
            raise Exception("Catmull was calculated twice!")

        cdef int x
        cdef float t
        cdef object v1, v2, v3
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

    def point_at_distance(self, length):
        return {
            0: False,
            1: self.points[0],
        }.get(self.order, self.rec(length))

    def rec(self, length):
        return mathhelper.point_at_distance(self.pos, length)

cdef class Perfect(object):
    cdef public list points
    cdef float cx, cy
    cdef float radius

    def __init__(self, points):
        self.points = points
        self.cx = 0
        self.cy = 0
        self.radius = 0
        self.setup_path()

    def setup_path(self):
        self.cx, self.cy, self.radius = get_circum_circle(self.points)
        if is_left(self.points):
            self.radius *= -1

    cpdef point_at_distance(self, float length):
        cdef float radians = length / self.radius
        return rotate(self.cx, self.cy, self.points[0], radians)

cpdef object get_point(object p, float length):
    cdef float x = mathhelper.catmull([o.x for o in p], length)
    cdef float y = mathhelper.catmull([o.y for o in p], length)
    return mathhelper.Vec2(x, y)

cpdef tuple get_circum_circle(list p):
    cdef float d = 2 * (p[0].x * (p[1].y - p[2].y) + p[1].x * (p[2].y - p[0].y) + p[2].x * (p[0].y - p[1].y))

    if d == 0:
        raise Exception("Invalid circle! Unable to chose angle.")

    cdef float ux = ((pow(p[0].x, 2) + pow(p[0].y, 2)) * (p[1].y - p[2].y) + (pow(p[1].x, 2) + pow(p[1].y, 2)) * (p[2].y - p[0].y) + (pow(p[2].x, 2) + pow(p[2].y, 2)) * (p[0].y - p[1].y)) / d
    cdef float uy = ((pow(p[0].x, 2) + pow(p[0].y, 2)) * (p[2].x - p[1].x) + (pow(p[1].x, 2) + pow(p[1].y, 2)) * (p[0].x - p[2].x) + (pow(p[2].x, 2) + pow(p[2].y, 2)) * (p[1].x - p[0].x)) / d

    cdef float px = ux - p[0].x
    cdef float py = uy - p[0].y
    cdef float r = pow(pow(px, 2) + pow(py, 2), 0.5)

    return ux, uy, r

cpdef float is_left(object p):
    return ((p[1].x - p[0].x) * (p[2].y - p[0].y) - (p[1].y - p[0].y) * (p[2].x - p[0].x)) < 0

cpdef object rotate(float cx, float cy, object p, float radians):
    cdef float cos = math.cos(radians)
    cdef float sin = math.sin(radians)

    return mathhelper.Vec2((cos * (p.x - cx)) - (sin * (p.y - cy)) + cx, (sin * (p.x - cx)) + (cos * (p.y - cy)) + cy)