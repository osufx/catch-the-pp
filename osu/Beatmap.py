from osu.HitObject import *
from osu.MathHelper import Vec2

import json

class Beatmap(object):
    """
    Beatmap object for beatmap parsing and handling
    """

    def __init__(self, fileName):
        """
        fileName -- Directory for beatmap file (.osu)
        """
        self.fileName = fileName
        self.header = -1
        self.difficulty = {}
        self.hitObjects = []
        self.ParseBeatmap()
        self.objectCount = self.GetObjectCount()
    
    def ParseBeatmap(self):
        """
        Parses beatmap file line by line by passing each line into ParseLine.
        """
        with open(self.fileName) as fileStream:
            for line in fileStream:
                self.ParseLine(line.replace("\n", ""))

    def ParseLine(self, line):
        """
        Parse a beatmapfile line.

        Handles lines that are required for our use case (Difficulty, TimingPoints & HitObjects), 
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
            self.HandleDifficultyPropperty(line)
        elif self.header == 1:
            #Cry more
            #print("NOT IMPLEMENTED: (TimingPoint) " + line)
            a = 1 #Placeholder
        elif self.header == 2:
            self.HandleHitObject(line)
    
    def HandleDifficultyPropperty(self, propperty):
        """
        Puts the [Difficulty] propperty into the difficulty dict.
        """
        prop = propperty.split(":")
        self.difficulty[prop[0]] = float(prop[1])

    def HandleHitObject(self, line):
        """
        Puts every hitobject into the hitObjects array.

        Creates HitObjects, HitObjectSliders or skip depending on the given data.
        We skip everything that is not important for us for our use case (Spinners)
        """
        splitObject = line.split(",")
        hitObject = HitObject(int(splitObject[0]), int(splitObject[1]), int(splitObject[2]), int(splitObject[3]))

        if not (1 & hitObject.type > 0 or 2 & hitObject.type > 0):  #We only want sliders and circles as spinners are random bannanas etc.
            return
        
        if 2 & hitObject.type:  #Slider
            curveSplit = splitObject[6].split("|")
            curvePoints = []
            for i in range(1, len(curveSplit)):
                vectorSplit = curveSplit[i].split(":")
                vector = Vec2(int(vectorSplit[0]), int(vectorSplit[1]))
                curvePoints.append(vector)
            hitObject = HitObjectSlider(hitObject, curveSplit[0], curvePoints, int(splitObject[6]), float(splitObject[7]))

        self.hitObjects.append(hitObject)

    def GetObjectCount(self):
        """
        Get the total hitobject count for the parsed beatmap (Normal hitobjects, sliders & sliderticks)

        return -- total hitobjects for parsed beatmap
        """
        count = 0
        for hitObject in self.hitObjects:
            count += hitObject.GetPoints()
        return count