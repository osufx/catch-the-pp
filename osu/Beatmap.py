from osu.HitObject import *
from osu.MathHelper import Vec2

import json

class Beatmap(object):
    def __init__(self, fileName):
        self.fileName = fileName
        self.header = -1
        self.difficultyJson = ""
        self.difficulty = {}
        self.hitObjects = []
        self.ParseBeatmap()
        self.objectCount = self.GetObjectCount()
    
    def ParseBeatmap(self):
        with open(self.fileName) as fileStream:
            for line in fileStream:
                self.ParseLine(line.replace("\n", ""))
        self.ParseDifficulty()

    def ParseLine(self, line):
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
        prop = propperty.split(":")
        self.difficultyJson += '"{}":{},'.format(prop[0], prop[1])
    
    def ParseDifficulty(self):
        self.difficultyJson = "{" + self.difficultyJson[:-1] + "}"
        self.difficulty = json.loads(self.difficultyJson)

    def HandleHitObject(self, line):
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
        count = 0
        for hitObject in self.hitObjects:
            count += hitObject.GetPoints()
        return count