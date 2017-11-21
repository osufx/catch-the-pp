from osu.MathHelper import Vec2, point_on_line
from helpers import curves

class HitObject(object):
    def __init__(self, x, y, time, t):
        self.x = x
        self.y = y
        self.time = time
        self.type = t

    def get_points(self):        #This is used to get the total amount of hitobjects
        return 1

class HitObjectSlider(object):
    def __init__(self, hitobject, slider_type, curve_points, repeat, pixel_length, scaled_velocity):
        self.x = hitobject.x
        self.y = hitobject.y
        self.time = hitobject.time
        self.type = hitobject.type
        self.hitobject = hitobject
        self.slider_type = slider_type
        self.curve_points = [Vec2(self.x, self.y)] + curve_points
        self.repeat = repeat
        self.pixel_length = pixel_length

        self.slider_ticks = 0
        self.scaled_velocity = scaled_velocity
        self.calculate_slider()

    def get_points(self):        #This is used to get the total amount of hitobjects
        val = 2                     #There is always a start and an end hitobject on every slider

        val *= self.repeat          #Reverse slider
        val -= (self.repeat - 1)    #Remove the reversearrow hitobject so it doesnt count reverse points twice
        return val

    def calculate_slider(self):
        print("slider_type: {}, scaled_velocity: {}".format(self.slider_type, self.scaled_velocity))    #DEBUG

        if self.slider_type == "P" and len(self.curve_points) > 3:
            self.slider_type = "B"
        elif len(self.curve_points) == 2:
            self.end = point_on_line(self.curve_points[0], self.curve_points[1], self.pixel_length)


        #Make path
        if self.slider_type == "L":     #Linear
            path = curves.Linear(self.curve_points).pos
        elif self.slider_type == "P":   #Perfect
            curve = curves.Perfect(self.curve_points)
        elif self.slider_type == "B":   #Bezier
            curve = curves.Bezier(self.curve_points, True)
            path = curve.pos
        elif self.slider_type == "C":   #Catmull
            curve = curves.Catmull(self.curve_points).pos
            path = curve.pos
        else:
            raise Exception("Slidertype not supported! ({})".format(self.slider_type))

        #Make end
        if not hasattr(self, 'end'):
            if self.slider_type == "L":     #Linear
                self.end = point_on_line(path[0], path[1], self.pixel_length)
            elif self.slider_type == "P":   #Perfect
                self.end = curve.point_at_distance(self.pixel_length)
            elif self.slider_type == "B":   #Bezier
                self.end = curve.point_at_distance(self.pixel_length)
            elif self.slider_type == "C":   #Catmull
                self.end = curve.point_at_distance(self.pixel_length)
            else:
                raise Exception("Slidertype not supported! ({})".format(self.slider_type))

        #Place slider_ticks

        #Place end_point
