"""
Catch-The-PP

https://github.com/osufx/catch-the-pp
by EmilySunpy, licensed under the GNU GPL 3 License.
"""
import math
import copy

MODULE_NAME = "ctpp"

STAR_SCALING_FACTOR = 0.145
STRAIN_STEP = 750
DECAY_WEIGHT = 0.94
DECAY_BASE = 0.2
ABSOLUTE_PLAYER_POSITIONING_ERROR = 16
NORMALIZED_HITOBJECT_RADIUS = 41
DIRECTION_CHANGE_BONUS = 12.5

SLIDER_QUALITY = 50

#HELPERS
def clamp(value, mn, mx):
    return min(max(mn, value), mx)

def sign(value):
    if value == 0:
        return 0
    elif value > 0:
        return 1
    else:
        return -1

def cpn(p, n):
    if p < 0 or p > n:
        return 0
    p = min(p, n - p)
    out = 1
    for i in range(1, p + 1):
        out = out * (n - p + i) / i

    return out

def catmull(p, t): # WARNING:   Worst math formula incomming
    return 0.5 * (
        (2 * p[1]) +
        (-p[0] + p[2]) * t +
        (2 * p[0] - 5 * p[1] + 4 * p[2] - p[3]) * pow(t, 2) +
        (-p[0] + 3 * p[1] - 3 * p[2] + p[3]) * pow(t, 3))

def point_on_line(p0, p1, length):
    full_length = pow(pow(p1.x - p0.x, 2) + pow(p1.y - p0.y, 2), 0.5)
    n = full_length - length

    if full_length == 0:
        print("full_length was forced to 1!")
        full_length = 1

    x = (n * p0.x + length * p1.x) / full_length
    y = (n * p0.y + length * p1.y) / full_length
    return Vec2(x, y)

def angle_from_points(p0, p1):
    return math.atan2(p1.y - p0.y, p1.x - p0.x)

def distance_from_points(array):
    distance = 0

    for i in range(1, len(array)):
        distance += array[i].distance(array[i - 1])

    return distance

def cart_from_pol(r, t):
    x = (r * math.cos(t))
    y = (r * math.sin(t))

    return Vec2(x, y)

def point_at_distance(array, distance, return_extra = False): #TODO: Optimize...
    i = 0
    current_distance = 0
    new_distance = 0

    if len(array) < 2:
        if return_extra:
            return [Vec2(0, 0), 0, 0]
        else:
            return Vec2(0, 0)

    if distance == 0:
        angle = angle_from_points(array[0], array[1])
        if return_extra:
            return [array[0], angle, 0]
        else:
            return array[0]

    if distance_from_points(array) <= distance:
        angle = angle_from_points(array[len(array) - 2], array[len(array) - 1])
        if return_extra:
            return [array[len(array) - 1].x,
                    array[len(array) - 1].y,
                    angle,
                    len(array) - 2]
        else:
            return array[len(array) - 1]

    for i in range(len(array) - 2):
        x = (array[i].x - array[i + 1].x)
        y = (array[i].y - array[i + 1].y)

        new_distance = (math.sqrt(x * x + y * y))
        current_distance += new_distance

        if distance <= current_distance:
            break

    current_distance -= new_distance

    if distance == current_distance:
        angle = angle_from_points(array[i], array[i + 1])
        if return_extra:
            return [array[i], angle, i]
        else:
            return array[i]
    else:
        angle = angle_from_points(array[i], array[i + 1])
        cart = cart_from_pol((distance - current_distance), angle)

        if array[i].x > array[i + 1].x:
            coord = Vec2((array[i].x - cart.x), (array[i].y - cart.y))
        else:
            coord = Vec2((array[i].x + cart.y), (array[i].y + cart.y))
    
    if return_extra:
        return [coord, angle, i]
    else:
        return coord

class Linear(object):   #Because it made sense at the time...
    def __init__(self, points):
        self.pos = points

class Bezier(object):
    def __init__(self, points):
        self.points = points
        self.order = len(self.points)
        self.pos = []
        self.calc_points()

    def calc_points(self):
        if len(self.pos) != 0:  #This should never happen but since im working on this I want to warn myself if I fuck up
            raise Exception("Bezier was calculated twice!")

        sub_points = []
        for i in range(len(self.points)):
            if i == len(self.points) - 1:
                sub_points.append(self.points[i])
                self.bezier(sub_points)
                sub_points.clear()
            elif len(sub_points) > 1 and self.points[i] == sub_points[-1]:
                self.bezier(sub_points)
                sub_points.clear()
            
            sub_points.append(self.points[i])

    def bezier(self, points):
        order = len(points)
        step = 0.25 / SLIDER_QUALITY / order #Normaly 0.0025
        i = 0
        n = order - 1
        while i < 1 + step:
            x = 0
            y = 0

            for p in range(n + 1):
                a = cpn(p, n) * pow((1 - i), (n - p)) * pow(i, p)
                x += a * points[p].x
                y += a * points[p].y

            point = Vec2(x, y)
            self.pos.append(point)
            i += step

    def point_at_distance(self, length):
        return {
            0: False,
            1: self.points[0],
        }.get(self.order, self.rec(length))

    def rec(self, length):
        return point_at_distance(self.pos, length)

class Catmull(object):  #Yes... I cry deep down on the inside aswell
    def __init__(self, points):
        self.points = points
        self.order = len(points)
        self.step = 2.5 / SLIDER_QUALITY   #Normaly 0.025
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

    def point_at_distance(self, length):
        return {
            0: False,
            1: self.points[0],
        }.get(self.order, self.rec(length))

    def rec(self, length):
        return point_at_distance(self.pos, length)

class Perfect(object):
    def __init__(self, points):
        self.points = points
        self.setup_path()
    
    def setup_path(self):
        self.cx, self.cy, self.radius = get_circum_circle(self.points)
        if is_left(self.points):
            self.radius *= -1
    
    def point_at_distance(self, length):
        radians = length / self.radius
        return rotate(self.cx, self.cy, self.points[0], radians)

def get_point(p, length):
    x = catmull([o.x for o in p], length)
    y = catmull([o.y for o in p], length)
    return Vec2(x, y)

def get_circum_circle(p):
    d = 2 * (p[0].x * (p[1].y - p[2].y) + p[1].x * (p[2].y - p[0].y) + p[2].x * (p[0].y - p[1].y))

    if d == 0:
        raise Exception("Invalid circle! Unable to chose angle.")

    ux = ((pow(p[0].x, 2) + pow(p[0].y, 2)) * (p[1].y - p[2].y) + (pow(p[1].x, 2) + pow(p[1].y, 2)) * (p[2].y - p[0].y) + (pow(p[2].x, 2) + pow(p[2].y, 2)) * (p[0].y - p[1].y)) / d
    uy = ((pow(p[0].x, 2) + pow(p[0].y, 2)) * (p[2].x - p[1].x) + (pow(p[1].x, 2) + pow(p[1].y, 2)) * (p[0].x - p[2].x) + (pow(p[2].x, 2) + pow(p[2].y, 2)) * (p[1].x - p[0].x)) / d

    px = ux - p[0].x
    py = uy - p[0].y
    r = pow(pow(px, 2) + pow(py, 2), 0.5)

    return ux, uy, r

def is_left(p):
    return ((p[1].x - p[0].x) * (p[2].y - p[0].y) - (p[1].y - p[0].y) * (p[2].x - p[0].x)) < 0

def rotate(cx, cy, p, radians):
    cos = math.cos(radians)
    sin = math.sin(radians)

    return Vec2((cos * (p.x - cx)) - (sin * (p.y - cy)) + cx, (sin * (p.x - cx)) + (cos * (p.y - cy)) + cy)

class Vec2(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def distance(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return pow(x*x + y*y, 0.5)  #sqrt, lol

    def calc(self, value, other):   #I dont know what to call this function yet
        x = self.x + value * other.x
        y = self.y + value * other.y
        return Vec2(x, y)

#HITOBJECTS
class SliderTick(object):
    def __init__(self, x, y, time):
        self.x = x
        self.y = y
        self.time = time

class HitObject(object):
    def __init__(self, x, y, time, object_type, slider_type = None, curve_points = None, repeat = 1, pixel_length = 0, timing_point = None, difficulty = None, tick_distance = 1):
        """
        HitObject params for normal hitobject and sliders

        x -- x position
        y -- y position
        time -- timestamp
        object_type -- type of object (bitmask)

        [+] IF SLIDER
        slider_type -- type of slider (L, P, B, C)
        curve_points -- points in the curve path
        repeat -- amount of repeats for the slider (+1)
        pixel_length -- length of the slider
        timing_point -- ref of current timing point for the timestamp
        difficulty -- ref of beatmap difficulty
        tick_distance -- distance betwin each slidertick
        """
        self.x = x
        self.y = y
        self.time = time
        self.type = object_type

        #isSlider?
        if 2 & self.type:
            self.slider_type = slider_type
            self.curve_points = [Vec2(self.x, self.y)] + curve_points
            self.repeat = repeat
            self.pixel_length = pixel_length

            #For slider tick calculations
            self.timing_point = timing_point
            self.difficulty = difficulty
            self.tick_distance = tick_distance
            self.duration = self.timing_point["raw_bpm"] * (pixel_length / (self.difficulty["SliderMultiplier"] * self.timing_point["spm"])) / 100 * self.repeat

            self.ticks = []
            self.end_ticks = []

            self.calc_slider()
    
    def calc_slider(self, calc_path = False):
        #Fix broken objects
        if self.slider_type == "P" and len(self.curve_points) > 3:
            self.slider_type = "B"
        elif len(self.curve_points) == 2:
            self.slider_type = "L"

        #Make curve
        if self.slider_type == "P":     #Perfect
            try:
                curve = Perfect(self.curve_points)
            except:
                curve = Bezier(self.curve_points)
        elif self.slider_type == "B":   #Bezier
            curve = Bezier(self.curve_points)
        elif self.slider_type == "C":   #Catmull
            curve = Catmull(self.curve_points)

        #Quickest to skip this
        if calc_path: #Make path if requested (For drawing visual for testing)
            if self.slider_type == "L":     #Linear
                self.path = Linear(self.curve_points).pos
            elif self.slider_type == "P":   #Perfect
                self.path = []
                l = 0
                step = 5
                while l <= self.pixel_length:
                    self.path.append(curve.point_at_distance(l))
                    l += step
            elif self.slider_type == "B":   #Bezier
                self.path = curve.pos
            elif self.slider_type == "C":   #Catmull
                self.path = curve.pos
            else:
                raise Exception("Slidertype not supported! ({})".format(self.slider_type))

        #Set slider ticks
        current_distance = self.tick_distance
        time_add = self.duration * (self.tick_distance / (self.pixel_length * self.repeat))

        while current_distance < self.pixel_length - self.tick_distance / 8:
            if self.slider_type == "L":     #Linear
                point = point_on_line(self.curve_points[0], self.curve_points[1], current_distance)
            else:   #Perfect, Bezier & Catmull uses the same function
                point = curve.point_at_distance(current_distance)

            self.ticks.append(SliderTick(point.x, point.y, self.time + time_add * (len(self.ticks) + 1)))
            current_distance += self.tick_distance

        if self.repeat == 1:
            if self.slider_type == "L":     #Linear
                point = point_on_line(self.curve_points[0], self.curve_points[1], self.pixel_length)
            else:   #Perfect, Bezier & Catmull uses the same function
                point = curve.point_at_distance(self.pixel_length)

            self.end_ticks.append(SliderTick(point.x, point.y, self.time + self.duration))

        #Adds slider_ends / repeat_points
        repeat_id = 1
        repeat_bonus_ticks = []
        while repeat_id < self.repeat:
            dist = (1 & repeat_id) * self.pixel_length
            time_offset = (self.duration / self.repeat) * repeat_id

            if self.slider_type == "L":     #Linear
                point = point_on_line(self.curve_points[0], self.curve_points[1], dist)
            else:   #Perfect, Bezier & Catmull uses the same function
                point = curve.point_at_distance(dist)

            self.end_ticks.append(SliderTick(point.x, point.y, self.time + time_offset))

            #Adds the ticks that already exists on the slider back (but reversed)
            repeat_ticks = copy.deepcopy(self.ticks)

            if 1 & repeat_id: #We have to reverse the timing normalizer
                #repeat_ticks = list(reversed(repeat_ticks))
                normalize_time_value = self.time + (self.duration / self.repeat)
            else:
                normalize_time_value = self.time

            #Correct timing
            for tick in repeat_ticks:
                tick.time = self.time + time_offset + abs(tick.time - normalize_time_value)

            repeat_bonus_ticks += repeat_ticks

            repeat_id += 1

        self.ticks += repeat_bonus_ticks

    def get_combo(self):
        """
        Returns the combo given by this object
        1 if normal hitobject, 2+ if slider (adds sliderticks)
        """
        if 2 & self.type:   #Slider
            val = 1                     #Start of the slider
            val += len(self.ticks)      #The amount of sliderticks
            val += self.repeat          #Reverse slider
        else:   #Normal
            val = 1                     #Itself...

        return val

#BEATMAP
class Beatmap(object):
    """
    Beatmap object for beatmap parsing and handling
    """

    def __init__(self, file_name):
        """
        file_name -- Directory for beatmap file (.osu)
        """
        self.file_name = file_name
        self.version = -1   #Unknown by default
        self.header = -1
        self.difficulty = {}
        self.timing_points = {
            "raw_bpm": {},  #Raw bpm modifier code
            "raw_spm": {}, #Raw speed modifier code
            "bpm": {},  #Beats pr minute
            "spm": {}   #Speed modifier
        }
        self.slider_point_distance = 1  #Changes after [Difficulty] is fully parsed
        self.hitobjects = []
        self.max_combo = 0
        self.parse_beatmap()

        if "ApproachRate" not in self.difficulty.keys():    #Fix old osu version
            self.difficulty["ApproachRate"] = self.difficulty["OverallDifficulty"]
    
    def parse_beatmap(self):
        """
        Parses beatmap file line by line by passing each line into parse_line.
        """
        with open(self.file_name, encoding="utf8") as file_stream:
            self.version = int(''.join(list(filter(str.isdigit, file_stream.readline()))))  #Set version
            for line in file_stream:
                self.parse_line(line.replace("\n", ""))

    def parse_line(self, line):
        """
        Parse a beatmapfile line.

        Handles lines that are required for our use case (Difficulty, TimingPoints & hitobjects), 
        everything else is skipped.
        """
        if len(line) < 1:
            return

        if line.startswith("["):
            if line == "[Difficulty]":
                self.header = 0
            elif line == "[TimingPoints]":
                self.header = 1
            elif line == "[HitObjects]":
                self.header = 2
                self.slider_point_distance = (100 * self.difficulty["SliderMultiplier"]) / self.difficulty["SliderTickRate"]
            else:
                self.header = -1
            return

        if self.header == -1: #We return if we are reading under a header we dont care about
            return

        if self.header == 0:
            self.handle_difficulty_propperty(line)
        elif self.header == 1:
            self.handle_timing_point(line)
        elif self.header == 2:
            self.handle_hitobject(line)
    
    def handle_difficulty_propperty(self, propperty):
        """
        Puts the [Difficulty] propperty into the difficulty dict.
        """
        prop = propperty.split(":")
        self.difficulty[prop[0]] = float(prop[1])

    def handle_timing_point(self, timing_point):
        """
        Formats timing points used for slider velocity changes,
        and store them into self.timing_points dict.
        """
        timing_point_split = timing_point.split(",")
        timing_point_time = int(float(timing_point_split[0])) #Fixes some special mappers special needs
        timing_point_focus = timing_point_split[1]

        if timing_point_focus.startswith("-"):  #If not then its not a slider velocity modifier
            self.timing_points["spm"][timing_point_time] = -100 / float(timing_point_focus) #Convert to normalized value and store
            self.timing_points["raw_spm"][timing_point_time] = float(timing_point_focus)
        else:
            self.timing_points["bpm"][timing_point_time] = 60000 / float(timing_point_focus)#^
            self.timing_points["raw_bpm"][timing_point_time] = float(timing_point_focus)
            #Trash
            self.timing_points["spm"][timing_point_time] = 1
            self.timing_points["raw_spm"][timing_point_time] = -100

    def handle_hitobject(self, line):
        """
        Puts every hitobject into the hitobjects array.

        Creates hitobjects, hitobject_sliders or skip depending on the given data.
        We skip everything that is not important for us for our use case (Spinners)
        """
        split_object = line.split(",")
        time = int(split_object[2])
        object_type = int(split_object[3])

        if not (1 & object_type > 0 or 2 & object_type > 0):  #We only want sliders and circles as spinners are random bannanas etc.
            return

        if 2 & object_type:  #Slider
            repeat = int(split_object[6])
            pixel_length = float(split_object[7])

            time_point = self.get_timing_point_all(time)

            tick_distance = (100 * self.difficulty["SliderMultiplier"]) / self.difficulty["SliderTickRate"]
            if self.version >= 8:
                tick_distance /= (clamp(-time_point["raw_spm"], 10, 1000) / 100)

            curve_split = split_object[5].split("|")
            curve_points = []
            for i in range(1, len(curve_split)):
                vector_split = curve_split[i].split(":")
                vector = Vec2(int(vector_split[0]), int(vector_split[1]))
                curve_points.append(vector)

            slider_type = curve_split[0]
            if self.version <= 6 and len(curve_points) >= 2:
                if slider_type == "L":
                    slider_type = "B"

                if len(curve_points) == 2:
                    if (int(split_object[0]) == curve_points[0].x and int(split_object[1]) == curve_points[0].y) or (curve_points[0].x == curve_points[1].x and curve_points[0].y == curve_points[1].y):
                        del curve_points[0]
                        slider_type = "L"

            hitobject = HitObject(int(split_object[0]), int(split_object[1]), time, object_type, slider_type, curve_points, repeat, pixel_length, time_point, self.difficulty, tick_distance)
        else:
            hitobject = HitObject(int(split_object[0]), int(split_object[1]), time, object_type)

        self.hitobjects.append(hitobject)
        self.max_combo += hitobject.get_combo()

    def get_timing_point_all(self, time):
        """
        Returns a object of all current timing types

        time -- timestamp
        return -- {"raw_bpm": Float, "raw_spm": Float, "bpm": Float, "spm": Float}
        """
        types = {
            "raw_bpm": 60000.0,
            "raw_spm": -100.0,
            "bpm": 100.0,
            "spm": 1.0
        }   #Will return the default value if timing point were not found
        for t in types.keys():
            r = self.get_timing_point(time, t)
            if r != None:
                types[t] = r

        return types

    def get_timing_point(self, time, timing_type):
        """
        Returns latest timing point by timestamp (Current)

        time -- timestamp
        timing_type -- mpb, bmp or spm
        return -- self.timing_points object
        """
        r = None
        try:
            for key in sorted(self.timing_points[timing_type].keys(), key=lambda k: k):
                if key <= time:
                    r = self.timing_points[timing_type][key]
                else:
                    break
        except Exception as e:
            print(e)
        return r

    def get_object_count(self):
        """
        Get the total hitobject count for the parsed beatmap (Normal hitobjects, sliders & sliderticks)

        return -- total hitobjects for parsed beatmap
        """
        count = 0
        for hitobject in self.hitobjects:
            count += hitobject.get_points()
        return count

#ENTRY
class DifficultyObject(object):
    """
    Object that holds strain value etc.

    Handled in Difficulty.calculate_strainValues & Difficulty.update_hyperdash_distance.
    Used in Difficulty.calculate_difficulty
    """
    def __init__(self, hitobject, player_width):
        """
        Hitobject wrapper to do calculation with.

        hitobject   -- Hitobject to wrap around (basic)
        player_width -- Catcher width    (after determined by active mods)
        """
        self.strain = 1
        self.offset = 0
        self.last_movement = 0
        self.hitobject = hitobject
        self.error_margin = ABSOLUTE_PLAYER_POSITIONING_ERROR
        self.player_width = player_width
        self.scaled_position = self.hitobject.x * (NORMALIZED_HITOBJECT_RADIUS / self.player_width)
        self.hyperdash_distance = 0
        self.hyperdash = False

    def calculate_strain(self, last, time_rate):
        """
        Calculate strain value by refering last object.
        (and sets offset & last_movement info)

        last        -- Previous hitobject
        time_rate    -- Timescale from enabled mods
        """
        time = (self.hitobject.time - last.hitobject.time) / time_rate
        decay = pow(DECAY_BASE, time / 1000)

        self.offset = clamp(last.scaled_position + last.offset,
            self.scaled_position - (NORMALIZED_HITOBJECT_RADIUS - self.error_margin),
            self.scaled_position + (NORMALIZED_HITOBJECT_RADIUS - self.error_margin)
        ) - self.scaled_position

        self.last_movement = abs(self.scaled_position - last.scaled_position + self.offset - last.offset)

        addition = pow(self.last_movement, 1.3) / 500

        if self.scaled_position < last.scaled_position:
            self.last_movement *= -1

        addition_bonus = 0
        sqrt_time = pow(max(time, 25), 0.5)

        if abs(self.last_movement) > 0.1:
            if abs(last.last_movement) > 0.1 and sign(self.last_movement) != sign(last.last_movement):
                bonus = DIRECTION_CHANGE_BONUS / sqrt_time
                bonus_factor = min(self.error_margin, abs(self.last_movement)) / self.error_margin

                addition += bonus * bonus_factor

                if last.hyperdash_distance <= 10:
                    addition_bonus += 0.3 * bonus_factor

            addition += 7.5 * min(abs(self.last_movement), NORMALIZED_HITOBJECT_RADIUS * 2) / (NORMALIZED_HITOBJECT_RADIUS * 6) / sqrt_time

        if last.hyperdash_distance <= 10:
            if not last.hyperdash:
                addition_bonus += 1
            else:
                self.offset = 0

            addition *= 1 + addition_bonus * ((10 - last.hyperdash_distance) / 10)

        addition *= 850 / max(time, 25)
        self.strain = last.strain * decay + addition

class Difficulty(object):
    """
    Difficulty object for calculating star rating.

    Stars: self.star_rating
    """

    def __init__(self, beatmap, mods):
        """
        CTB difficulty calculator params.
        Calculates the star rating for the given beatmap.

        beatmap -- Beatmap object of parsed beatmap
        mods    -- Int representation of mods selected / bitmask
        """
        self.beatmap = beatmap
        self.mods = mods

        self.hitobjects_with_ticks = []
        for hitobject in self.beatmap.hitobjects:
            self.hitobjects_with_ticks.append(hitobject)
            if 2 & hitobject.type:
                for tick in hitobject.ticks:
                    self.hitobjects_with_ticks.append(tick)
                for end_tick in hitobject.end_ticks:
                    self.hitobjects_with_ticks.append(end_tick)

        self.difficulty_objects = []

        #Do the calculation
        self.time_rate = self.get_time_rate()
        self.player_width = 305 / 1.6 * ((102.4 * (1 - 0.7 * self.adjust_difficulty(self.beatmap.difficulty["CircleSize"], self.mods))) / 128) * 0.7

        for hitobject in self.hitobjects_with_ticks:
            self.difficulty_objects.append(DifficultyObject(hitobject, self.player_width * 0.4))

        self.update_hyperdash_distance()

        #Sort the list so its sorted by time (Incase it somehow isnt)
        self.difficulty_objects.sort(key=lambda o: o.hitobject.time)

        self.calculate_strain_values()

        self.star_rating = pow(self.calculate_difficulty(), 0.5) * STAR_SCALING_FACTOR

    def adjust_difficulty(self, diff, mods):
        """
        Scale difficulty from selected mods.

        diff    -- CircleSize
        mods    -- Int representation of mods selected / bitmask
        return  -- Scaled difficulty
        """
        if mods & 1 << 1 > 0:       #EZ
            diff = max(0, diff / 2)
        if mods & 1 << 4 > 0:       #HR
            diff = min(10, diff * 1.3)

        return (diff - 5) / 5

    def get_time_rate(self):
        """
        Get scaled time_rate from mods. (DT / HT)

        return -- time_rate
        """
        rate = 1

        if self.mods & 1 << 6 > 0:      #DT
            rate += 0.5
        elif self.mods & 1 << 8 > 0:    #HT
            rate -= 0.25

        return rate

    def update_hyperdash_distance(self):
        """
        Update hyperdash_distance value for every hitobject in the beatmap.
        """
        last_direction = 0
        player_width_half = self.player_width / 2
        last = player_width_half

        for i in range(len(self.difficulty_objects) - 1):
            current = self.difficulty_objects[i]
            next = self.difficulty_objects[i + 1]

            if next.hitobject.x > current.hitobject.x:
                direction = 1
            else:
                direction = -1

            time_to_next = next.hitobject.time - current.hitobject.time - 4.166667 #ms for 60fps divided by 4
            distance_to_next = abs(next.hitobject.x - current.hitobject.x)
            if last_direction == direction:
                distance_to_next -= last
            else:
                distance_to_next -= player_width_half

            if time_to_next < distance_to_next:
                current.hyperdash = True
                last = player_width_half
            else:
                current.hyperdash_distance = time_to_next - distance_to_next
                last = clamp(current.hyperdash_distance, 0, player_width_half)

            last_direction = direction

    def calculate_strain_values(self):
        """
        Calculate strain values for every hitobject.

        It does this by using distance, decay & previous hitobject strain value.
        Time_rate also effects this.
        """
        current = self.difficulty_objects[0]

        index = 1
        while index < len(self.difficulty_objects):
            next = self.difficulty_objects[index]
            next.calculate_strain(current, self.time_rate)
            current = next
            index += 1

    def calculate_difficulty(self):
        """
        Calculates the difficulty for this beatmap.
        This is used in the final function to calculate star rating.
        DISCLAIMER: This is not the final star rating value.

        return -- difficulty
        """
        strain_step = STRAIN_STEP * self.time_rate
        highest_strains = []
        interval = strain_step
        max_strain = 0

        last = None

        for difficulty_object in self.difficulty_objects:
            while difficulty_object.hitobject.time > interval:
                highest_strains.append(max_strain)

                if last == None:
                    max_strain = 0
                else:
                    decay = pow(DECAY_BASE, (interval - last.hitobject.time) / 1000)
                    max_strain = last.strain * decay

                interval += strain_step

            if difficulty_object.strain > max_strain:
                max_strain = difficulty_object.strain

            last = difficulty_object

        difficulty = 0
        weight = 1

        #Sort from high to low strain
        highest_strains.sort(key=int, reverse=True)

        for strain in highest_strains:
            difficulty += weight * strain
            weight *= DECAY_WEIGHT

        return difficulty

def calculate_pp(diff, accuracy, combo, miss):
    """
    Calculate pp for gameplay

    diff        -- Difficulty object
    accuracy    -- Accuracy of the play             (Float 0-1)
    combo       -- MaxCombo achived during the play (Int)
    miss        -- Amount of misses during the play (Int)
    return      -- Total pp for gameplay
    """
    pp = pow(((5 * diff.star_rating / 0.0049) - 4), 2) / 100000
    length_bonus = 0.95 + 0.4 * min(1, combo / 3000)
    if combo > 3000:
        length_bonus += math.log10(combo / 3000) * 0.5

    pp *= length_bonus
    pp *= pow(0.97, miss)
    pp *= min(pow(combo, 0.8) / pow(diff.beatmap.max_combo, 0.8), 1)

    if diff.beatmap.difficulty["ApproachRate"] > 9:
        pp *= 1 + 0.1 * (diff.beatmap.difficulty["ApproachRate"] - 9)
    if diff.beatmap.difficulty["ApproachRate"] < 8:
        pp *= 1 + 0.025 * (8 - diff.beatmap.difficulty["ApproachRate"])

    if diff.mods & 1 << 3 > 0:    #HD
        pp *= 1.05 + 0.075 * (10 - min(10, diff.beatmap.difficulty["ApproachRate"]))

    if diff.mods & 1 << 10 > 0:    #FL
        pp *= 1.35 * length_bonus

    pp *= pow(accuracy, 5.5)

    if diff.mods & 1 << 0 > 0:    #NF
        pp *= 0.9

    if diff.mods & 1 << 12 > 0:    #SO
        pp *= 0.95

    return pp
