import math

cpdef float clamp(float value, float mn, float mx):
    return min(max(mn, value), mx)

cpdef sign(float value):
    if value == 0:
        return 0
    elif value > 0:
        return 1
    else:
        return -1

cpdef cpn(int p, int n):
    if p < 0 or p > n:
        return 0
    p = min(p, n - p)
    out = 1
    for i in range(1, p + 1):
        out = out * (n - p + i) / i

    return out

cpdef float catmull(p, t): # WARNING:   Worst math formula incomming
    return 0.5 * (
        (2 * p[1]) +
        (-p[0] + p[2]) * t +
        (2 * p[0] - 5 * p[1] + 4 * p[2] - p[3]) * (t ** 2) +
        (-p[0] + 3 * p[1] - 3 * p[2] + p[3]) * (t ** 3))

cpdef Vec2 point_on_line(Vec2 p0, Vec2 p1, float length):
    cdef float full_length = (((p1.x - p0.x) ** 2) + ((p1.y - p0.y) ** 2)) ** 0.5
    cdef float n = full_length - length

    if full_length == 0: #Fix for something that seems unknown... (We warn if this happens)
        full_length = 1

    cdef float x = (n * p0.x + length * p1.x) / full_length
    cdef float y = (n * p0.y + length * p1.y) / full_length

    return Vec2(x, y)

cpdef float angle_from_points(Vec2 p0, Vec2 p1):
    return math.atan2(p1.y - p0.y, p1.x - p0.x)

cpdef float distance_from_points(array):
    cdef float distance = 0
    cdef int i

    for i in range(1, len(array)):
        distance += array[i].distance(array[i - 1])

    return distance

cpdef Vec2 cart_from_pol(r, t):
    cdef float x = (r * math.cos(t))
    cdef float y = (r * math.sin(t))

    return Vec2(x, y)

cpdef point_at_distance(array, float distance): #TODO: Optimize...
    cdef int i = 0
    cdef float x, y, current_distance = 0, new_distance = 0, angle
    cdef Vec2 coord, cart

    if len(array) < 2:
        return Vec2(0, 0)

    if distance == 0:
        return array[0]

    if distance_from_points(array) <= distance:
        return array[len(array) - 1]

    for i in range(len(array) - 2):
        x = (array[i].x - array[i + 1].x)
        y = (array[i].y - array[i + 1].y)

        new_distance = math.sqrt(x * x + y * y)
        current_distance += new_distance

        if distance <= current_distance:
            break

    current_distance -= new_distance

    if distance == current_distance:
        return array[i]
    else:
        angle = angle_from_points(array[i], array[i + 1])
        cart = cart_from_pol((distance - current_distance), angle)

        if array[i].x > array[i + 1].x:
            coord = Vec2((array[i].x - cart.x), (array[i].y - cart.y))
        else:
            coord = Vec2((array[i].x + cart.y), (array[i].y + cart.y))
        return coord

cdef class Vec2(object):
    cdef public float x
    cdef public float y

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __richcmp__(x, y, op):
        if op == 2:#Py_EQ
            return x.__is_equal(y)
        else:#Py_NE
            return not x.__is_equal(y)

    def __is_equal(self, other):
        return self.x == other.x and self.y == other.y

    cpdef float distance(Vec2 self, Vec2 other):
        cdef float x = self.x - other.x
        cdef float y = self.y - other.y
        return (x*x + y*y) ** 0.5  #sqrt, lol

    cpdef Vec2 calc(Vec2 self, float value, Vec2 other):   #I dont know what to call this function yet
        cdef float x = self.x + value * other.x
        cdef float y = self.y + value * other.y
        return Vec2(x, y)
