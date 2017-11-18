from osu.HitObject import *
from osu.MathHelper import Vec2

class Beatmap(object):
    """
    Beatmap object for beatmap parsing and handling
    """

    def __init__(self, file_name):
        """
        file_name -- Directory for beatmap file (.osu)
        """
        self.file_name = file_name
        self.header = -1
        self.difficulty = {}
        self.hitobjects = []
        self.parse_beatmap()
        self.object_count = self.get_object_count()
    
    def parse_beatmap(self):
        """
        Parses beatmap file line by line by passing each line into parse_line.
        """
        with open(self.file_name) as file_stream:
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
            else:
                self.header = -1
            return

        if self.header == -1: #We return if we are reading under a header we dont care about
            return

        if self.header == 0:
            self.handle_difficulty_propperty(line)
        elif self.header == 1:
            #Cry more
            #print("NOT IMPLEMENTED: (TimingPoint) " + line)
            a = 1 #Placeholder
        elif self.header == 2:
            self.handle_hitobject(line)
    
    def handle_difficulty_propperty(self, propperty):
        """
        Puts the [Difficulty] propperty into the difficulty dict.
        """
        prop = propperty.split(":")
        self.difficulty[prop[0]] = float(prop[1])

    def handle_hitobject(self, line):
        """
        Puts every hitobject into the hitobjects array.

        Creates hitobjects, hitobject_sliders or skip depending on the given data.
        We skip everything that is not important for us for our use case (Spinners)
        """
        split_object = line.split(",")
        hitobject = HitObject(int(split_object[0]), int(split_object[1]), int(split_object[2]), int(split_object[3]))

        if not (1 & hitobject.type > 0 or 2 & hitobject.type > 0):  #We only want sliders and circles as spinners are random bannanas etc.
            return

        if 2 & hitobject.type:  #Slider
            curve_split = split_object[5].split("|")
            curve_points = []
            for i in range(1, len(curve_split)):
                vector_split = curve_split[i].split(":")
                vector = Vec2(int(vector_split[0]), int(vector_split[1]))
                curve_points.append(vector)
            hitobject = HitObjectSlider(hitobject, curve_split[0], curve_points, int(split_object[6]), float(split_object[7]))

        self.hitobjects.append(hitobject)

    def get_object_count(self):
        """
        Get the total hitobject count for the parsed beatmap (Normal hitobjects, sliders & sliderticks)

        return -- total hitobjects for parsed beatmap
        """
        count = 0
        for hitobject in self.hitobjects:
            count += hitobject.get_points()
        return count
