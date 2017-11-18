from osu.MathHelper import Vec2, point_on_line

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
        self.x = hitobject.x #Just no (Do this propperly or whatever...)
        self.time = hitobject.time #Just no
        self.hitobject = hitobject
        self.slider_type = slider_type
        self.curve_points = curve_points
        self.repeat = repeat
        self.pixel_length = pixel_length
        self.scaled_velocity = scaled_velocity
        self.calculate_slider()

    def get_points(self):        #This is used to get the total amount of hitobjects
        val = 2                     #There is always a start and an end hitobject on every slider

        val *= self.repeat          #Reverse slider
        val -= (self.repeat - 1)    #Remove the reversearrow hitobject so it doesnt count reverse points twice
        return val

    def calculate_slider(self):
        print("slider_type: {}, scaled_velocity: {}".format(self.slider_type, self.scaled_velocity))    #DEBUG
        if self.slider_type == "L":     #Linear
            return
        elif self.slider_type == "P":   #Perfect
            return
        elif self.slider_type == "B":   #Bezier
            return
        elif self.slider_type == "C":   #Catmull
            return
        else:
            raise Exception("Slidertype not supported! ({})".format(self.slider_type))
