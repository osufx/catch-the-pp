from ... import constants
from ...osu_parser.mathhelper import clamp, sign


cdef class DifficultyObject:
    """
    Object that holds strain value etc.

    Handled in Difficulty.calculate_strainValues & Difficulty.update_hyperdash_distance.
    Used in Difficulty.calculate_difficulty
    """
    cdef public float strain, last_movement
    cdef public float offset, player_width, scaled_position, hyperdash_distance
    cdef public object hitobject
    cdef public int error_margin, hyperdash

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

    cpdef calculate_strain(self, object last, float time_rate):
        """
        Calculate strain value by refering last object.
        (and sets offset & last_movement info)

        last        -- Previous hitobject
        time_rate    -- Timescale from enabled mods
        """
        cdef float time = (self.hitobject.time - last.hitobject.time) / time_rate
        cdef float decay = constants.DECAY_BASE ** (time / 1000)

        self.offset = clamp(last.scaled_position + last.offset,
            self.scaled_position - (constants.NORMALIZED_HITOBJECT_RADIUS - self.error_margin),
            self.scaled_position + (constants.NORMALIZED_HITOBJECT_RADIUS - self.error_margin)
        ) - self.scaled_position

        self.last_movement = abs(self.scaled_position - last.scaled_position + self.offset - last.offset)

        cdef float addition = (self.last_movement ** 1.3) / 500

        if self.scaled_position < last.scaled_position:
            self.last_movement *= -1

        cdef float addition_bonus = 0
        cdef float sqrt_time = max(time, 25) ** 0.5

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

cdef class Difficulty:
    """
    Difficulty object for calculating star rating.

    Stars: self.star_rating
    """
    cdef public object beatmap
    cdef public int mods
    cdef public list hitobjects_with_ticks, difficulty_objects
    cdef public float time_rate, player_width, star_rating


    def __init__(self, beatmap, mods):
        """
        CTB difficulty calculator params.
        Calculates the star rating for the given beatmap.

        beatmap -- Beatmap object of parsed beatmap
        mods    -- Int representation of mods selected / bitmask
        """
        self.beatmap = beatmap
        self.mods = mods

        #Difficulty modifier by mod
        cdef str diff
        for diff in self.beatmap.difficulty.keys():
            if diff == "CircleSize":
                scala = 1.3
            else:
                scala = 1.4
            self.beatmap.difficulty[diff] = self.adjust_difficulty(self.beatmap.difficulty[diff], self.mods, scala)

        cdef object hitobject
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
        self.player_width = 305 / 1.6 * ((102.4 * (1 - 0.7 * (self.beatmap.difficulty["CircleSize"] - 5) / 5)) / 128) * 0.7

        for hitobject in self.hitobjects_with_ticks:
            self.difficulty_objects.append(DifficultyObject(hitobject, self.player_width * 0.4))

        self.update_hyperdash_distance()

        #Sort the list so its sorted by time (Incase it somehow isnt)
        self.difficulty_objects.sort(key=lambda o: o.hitobject.time)

        self.calculate_strain_values()

        self.star_rating = (self.calculate_difficulty() ** 0.5) * constants.STAR_SCALING_FACTOR


    def adjust_difficulty(self, diff, mods, scala):
        """
        Scale difficulty from selected mods.

        diff    -- CircleSize
        mods    -- Int representation of mods selected / bitmask
        return  -- Scaled difficulty
        """
        if mods & 1 << 1 > 0:       #EZ
            diff = max(0, diff / 2)
        if mods & 1 << 4 > 0:       #HR
            diff = min(10, diff * scala)

        return diff

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

    cpdef update_hyperdash_distance(self):
        """
        Update hyperdash_distance value for every hitobject in the beatmap.
        """
        cdef int last_direction = 0, direction, i
        cdef float player_width_half = self.player_width / 2
        cdef float last = player_width_half

        cdef object current_object, next_object

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

    cpdef calculate_strain_values(self):
        """
        Calculate strain values for every hitobject.

        It does this by using distance, decay & previous hitobject strain value.
        Time_rate also effects this.
        """
        cdef object current_object = self.difficulty_objects[0], next_object

        cdef index = 1
        while index < len(self.difficulty_objects):
            next_object = self.difficulty_objects[index]
            next_object.calculate_strain(current_object, self.time_rate)
            current_object = next_object
            index += 1

    cpdef float calculate_difficulty(self):
        """
        Calculates the difficulty for this beatmap.
        This is used in the final function to calculate star rating.
        DISCLAIMER: This is not the final star rating value.

        return -- difficulty
        """
        cdef float strain_step = constants.STRAIN_STEP * self.time_rate
        cdef list highest_strains = []
        cdef float interval = strain_step
        cdef float max_strain = 0

        cdef object last = None, difficulty_object

        for difficulty_object in self.difficulty_objects:
            while difficulty_object.hitobject.time > interval:
                highest_strains.append(max_strain)

                if last is None:
                    max_strain = 0
                else:
                    decay = (constants.DECAY_BASE ** ((interval - last.hitobject.time) / 1000))
                    max_strain = last.strain * decay

                interval += strain_step

            if difficulty_object.strain > max_strain:
                max_strain = difficulty_object.strain

            last = difficulty_object

        cdef float difficulty = 0
        cdef float weight = 1

        #Sort from high to low strain
        highest_strains.sort(key=int, reverse=True)

        cdef float strain
        for strain in highest_strains:
            difficulty += weight * strain
            weight *= constants.DECAY_WEIGHT

        return difficulty
