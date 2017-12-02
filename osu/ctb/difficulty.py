import constants
from osu_parser.mathhelper import clamp, sign

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
        self.error_margin = constants.ABSOLUTE_PLAYER_POSITIONING_ERROR
        self.player_width = player_width
        self.scaled_position = self.hitobject.x * (constants.NORMALIZED_HITOBJECT_RADIUS / self.player_width)
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
        decay = pow(constants.DECAY_BASE, time / 1000)

        self.offset = clamp(last.scaled_position + last.offset,
            self.scaled_position - (constants.NORMALIZED_HITOBJECT_RADIUS - self.error_margin),
            self.scaled_position + (constants.NORMALIZED_HITOBJECT_RADIUS - self.error_margin)
        ) - self.scaled_position

        self.last_movement = abs(self.scaled_position - last.scaled_position + self.offset - last.offset)

        addition = pow(self.last_movement, 1.3) / 500

        if self.scaled_position < last.scaled_position:
            self.last_movement *= -1

        addition_bonus = 0
        sqrt_time = pow(max(time, 25), 0.5)

        if abs(self.last_movement) > 0.1:
            if abs(last.last_movement) > 0.1 and sign(self.last_movement) != sign(last.last_movement):
                bonus = constants.DIRECTION_CHANGE_BONUS / sqrt_time
                bonus_factor = min(self.error_margin, abs(self.last_movement)) / self.error_margin

                addition += bonus * bonus_factor

                if last.hyperdash_distance <= 10:
                    addition_bonus += 0.3 * bonus_factor

            addition += 7.5 * min(abs(self.last_movement), constants.NORMALIZED_HITOBJECT_RADIUS * 2) / (constants.NORMALIZED_HITOBJECT_RADIUS * 6) / sqrt_time

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
                self.hitobjects_with_ticks.append(hitobject.end)

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

        self.star_rating = pow(self.calculate_difficulty(), 0.5) * constants.STAR_SCALING_FACTOR

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
            current_object = self.difficulty_objects[i]
            next_object = self.difficulty_objects[i + 1]

            if next_object.hitobject.x > current_object.hitobject.x:
                direction = 1
            else:
                direction = -1

            time_to_next = next_object.hitobject.time - current_object.hitobject.time - 4.166667 #ms for 60fps divided by 4
            distance_to_next = abs(next_object.hitobject.x - current_object.hitobject.x)
            if last_direction == direction:
                distance_to_next -= last
            else:
                distance_to_next -= player_width_half

            if time_to_next < distance_to_next:
                current_object.hyperdash = True
                last = player_width_half
            else:
                current_object.hyperdash_distance = time_to_next - distance_to_next
                last = clamp(current_object.hyperdash_distance, 0, player_width_half)

            last_direction = direction

    def calculate_strain_values(self):
        """
        Calculate strain values for every hitobject.

        It does this by using distance, decay & previous hitobject strain value.
        Time_rate also effects this.
        """
        current_object = self.difficulty_objects[0]

        index = 1
        while index < len(self.difficulty_objects):
            next_object = self.difficulty_objects[index]
            next_object.calculate_strain(current_object, self.time_rate)
            current_object = next_object
            index += 1

    def calculate_difficulty(self):
        """
        Calculates the difficulty for this beatmap.
        This is used in the final function to calculate star rating.
        DISCLAIMER: This is not the final star rating value.

        return -- difficulty
        """
        strain_step = constants.STRAIN_STEP * self.time_rate
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
                    decay = pow(constants.DECAY_BASE, (interval - last.hitobject.time) / 1000)
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
            weight *= constants.DECAY_WEIGHT

        return difficulty
