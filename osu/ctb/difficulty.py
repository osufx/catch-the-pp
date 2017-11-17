import constants
from osu.MathHelper import Clamp, Sign

class DifficultyObject(object):
        """
        Object that holds strain value etc.

        Handled in Difficulty.CalculateStrainValues & Difficulty.UpdateHyperdashDistance. 
        Used in Difficulty.CalculateDifficulty
        """
        def __init__(self, hitObject, playerWidth):
            """
            Hitobject wrapper to do calculation with.

            hitObject   -- Hitobject to wrap around (basic)
            playerWidth -- Catcher width    (after determined by active mods)
            """
            self.strain = 1
            self.offset = 0
            self.lastMovement = 0
            self.hitObject = hitObject
            self.errorMargin = constants.ABSOLUTE_PLAYER_POSITIONING_ERROR
            self.playerWidth = playerWidth
            self.scaledPosition = self.hitObject.x * (constants.NORMALIZED_HITOBJECT_RADIUS / self.playerWidth)
            self.hyperdashDistance = 0
            self.hyperdash = False

        def CalculateStrain(self, last, timeRate):
            """
            Calculate strain value by refering last object. 
            (and sets offset & lastMovement info)

            last        -- Previous hitobject
            timerate    -- Timescale from enabled mods
            """
            time = (self.hitObject.time - last.hitObject.time) / timeRate
            decay = pow(constants.DECAY_BASE, time / 1000)

            self.offset = Clamp(last.scaledPosition + last.offset,
                self.scaledPosition - (constants.NORMALIZED_HITOBJECT_RADIUS - self.errorMargin),
                self.scaledPosition + (constants.NORMALIZED_HITOBJECT_RADIUS - self.errorMargin)
            ) - self.scaledPosition

            self.lastMovement = abs(self.scaledPosition - last.scaledPosition + self.offset - last.offset)

            addition = pow(self.lastMovement, 1.3) / 500

            if self.scaledPosition < last.scaledPosition:
                self.lastMovement *= -1
            
            additionBonus = 0
            sqrtTime = pow(max(time, 25), 0.5)

            if abs(self.lastMovement) > 0.1:
                if abs(last.lastMovement) > 0.1 and Sign(self.lastMovement) != Sign(last.lastMovement):
                    bonus = constants.DIRECTION_CHANGE_BONUS / sqrtTime
                    bonusFactor = min(self.errorMargin, abs(self.lastMovement)) / self.errorMargin

                    addition += bonus * bonusFactor

                    if last.hyperdashDistance <= 10:
                        additionBonus += 0.3 * bonusFactor
                
                addition += 7.5 * min(abs(self.lastMovement), constants.NORMALIZED_HITOBJECT_RADIUS * 2) / (constants.NORMALIZED_HITOBJECT_RADIUS * 6) / sqrtTime

            if last.hyperdashDistance <= 10:
                if not last.hyperdash:
                    additionBonus += 1
                else:
                    self.offset = 0
                
                addition *= 1 + additionBonus * ((10 - last.hyperdashDistance) / 10)
            
            addition *= 850 / max(time, 25)
            self.strain = last.strain * decay + addition

class Difficulty(object):
    """
    Difficulty object for calculating star rating.

    Stars: self.starRating
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

        self.DifficultyObjects = []

        #Do the calculation
        self.timeRate = self.getTimeRate()
        self.playerWidth = 305 / 1.6 * ((102.4 * (1 - 0.7 * self.AdjustDifficulty(self.beatmap.difficulty["CircleSize"], self.mods))) / 128) * 0.7

        for hitObject in self.beatmap.hitObjects:
            self.DifficultyObjects.append(DifficultyObject(hitObject, self.playerWidth * 0.4))
        
        self.UpdateHyperdashDistance()

        #Sort the list so its sorted by time (Incase it somehow isnt)
        self.DifficultyObjects.sort(key=lambda o: o.hitObject.time)

        self.CalculateStrainValues()

        self.starRating = pow(self.CalculateDifficulty(), 0.5) * constants.STAR_SCALING_FACTOR

    def AdjustDifficulty(self, diff, mods):
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

    def getTimeRate(self):
        """
        Get scaled timerate from mods. (DT / HT)

        return -- timerate
        """
        rate = 1

        if self.mods & 1 << 6 > 0:      #DT
            rate += 0.5
        elif self.mods & 1 << 8 > 0:    #HT
            rate -= 0.25
        
        return rate

    def UpdateHyperdashDistance(self):
        """
        Update hyperdashDistance value for every hitobject in the beatmap.
        """
        lastDirection = 0
        playerWidthHalf = self.playerWidth / 2
        last = playerWidthHalf

        for i in range(len(self.DifficultyObjects) - 1):
            current = self.DifficultyObjects[i]
            next = self.DifficultyObjects[i + 1]

            if next.hitObject.x > current.hitObject.x:
                direction = 1
            else:
                direction = -1
            
            timeToNext = next.hitObject.time - current.hitObject.time - 4.166667 #ms for 60fps divided by 4
            distanceToNext = abs(next.hitObject.x - current.hitObject.x) 
            if lastDirection == direction:
                distanceToNext -= last
            else:
                distanceToNext -= playerWidthHalf
            
            if timeToNext < distanceToNext:
                current.hyperdash = True
                last = playerWidthHalf
            else:
                current.hyperdashDistance = timeToNext - distanceToNext
                last = Clamp(current.hyperdashDistance, 0, playerWidthHalf)
            
            lastDirection = direction
    
    def CalculateStrainValues(self):
        """
        Calculate strain values for every hitobject.

        It does this by using distance, decay & previous hitobject strain value. 
        Timerate also effects this.
        """
        current = self.DifficultyObjects[0]

        index = 1
        while index < len(self.DifficultyObjects):
            next = self.DifficultyObjects[index]
            next.CalculateStrain(current, self.timeRate)
            current = next
            index += 1

    def CalculateDifficulty(self):
        """
        Calculates the difficulty for this beatmap. 
        This is used in the final function to calculate star rating. 
        DISCLAIMER: This is not the final star rating value.
        
        return -- difficulty
        """
        strainStep = constants.STRAIN_STEP * self.timeRate
        highestStrains = []
        interval = strainStep
        maxStrain = 0

        last = None

        for difficultyObject in self.DifficultyObjects:
            while difficultyObject.hitObject.time > interval:
                highestStrains.append(maxStrain)

                if last == None:
                    maxStrain = 0
                else:
                    decay = pow(constants.DECAY_BASE, (interval - last.hitObject.time) / 1000)
                    maxStrain = last.strain * decay
                
                interval += strainStep
            
            if difficultyObject.strain > maxStrain:
                maxStrain = difficultyObject.strain
            
            last = difficultyObject
        
        difficulty = 0
        weight = 1

        #Sort from high to low strain
        highestStrains.sort(key=int, reverse=True)

        for strain in highestStrains:
            difficulty += weight * strain
            weight *= constants.DECAY_WEIGHT
        
        return difficulty