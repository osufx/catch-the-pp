class HitObject(object):
    def __init__(self, x, y, time, t):
        self.x = x
        self.y = y
        self.time = time
        self.type = t

    def GetPoints(self):        #This is used to get the total amount of hitObjects
        return 1

class HitObjectSlider(object):
    def __init__(self, hitObject, sliderType, curvePoints, repeat, pixelLength):
        self.x = hitObject.x #Just no (Do this propperly or whatever...)
        self.time = hitObject.time #Just no
        self.hitObject = hitObject
        self.sliderType = sliderType
        self.curvePoints = curvePoints
        self.repeat = repeat
        self.pixelLength = pixelLength

    def GetPoints(self):        #This is used to get the total amount of hitObjects
        val = 2                     #There is always a start and an end hitobject on every slider

        val *= self.repeat          #Reverse slider
        val -= (self.repeat - 1)    #Remove the reversearrow hitobject so it doesnt count reverse points twice
        return val