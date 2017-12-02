import turtle
import time
from osu_parser.beatmap import Beatmap

beatmap = Beatmap("test.osu")

wn = turtle.Screen()
tur = turtle.Turtle()
tur.penup()
tur.speed(2)

for hitobject in beatmap.hitobjects:
    #if hitobject.time < 36300 or hitobject.time > 37600:
        #continue
    tur.goto(hitobject.x, -hitobject.y)
    tur.pendown()
    tur.pencolor("red")
    if 2 & hitobject.type:
        tur.dot(6)
        #for point in hitobject.path:
            #tur.goto(point.x, -point.y)
            #time.sleep(0.1)
        print("time: {}, x: {}, y: {}, type: sliderStart, duration: {}".format(hitobject.time, hitobject.x, hitobject.y, hitobject.duration))
        
        i = 0
        for tick in hitobject.ticks:
            tur.goto(tick.x, -tick.y)
            print("time: {}, x: {}, y: {}, type: tick, num: {}".format(tick.time, tick.x, tick.y, i))
            time.sleep(0.5)
            i += 1
            tur.dot(6, "black")
        
        tur.goto(hitobject.end.x, -hitobject.end.y)
        tur.pencolor("green")
        tur.dot(6)
    else:
        tur.pencolor("blue")
        tur.dot(6)
        print("time: {}, x: {}, y: {}, type: hitCircle".format(hitobject.time, hitobject.x, hitobject.y))
    tur.penup()

wn.exitonclick()