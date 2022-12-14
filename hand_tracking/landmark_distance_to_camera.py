import math


class LandmarkDistanceToCamera:
    def __init__(self):
        self.KNOWN_DISTANCE = 750  # initialize the known distance from the camera to the object, which
        self.KNOWN_WIDTH = 60  # initialize the known object width, which in this case is the distance in mm between landmark 5 and 17
        self.focal_length = None

        self.min_area = None  # Area, between landmarks 0, 5 and 17
        self.min_area_threshold = 0.1  # threshold, in this case 10%, below init area to be allowed

        self.last_distance = None

    def calculate_distance(self, landmarks):
        if self.focal_length is None:
            self.get_pixel_distance(landmarks, True)
            return  # dont go further in the method until a reference length was found

        distance_in_pixel, area = self.get_pixel_distance(landmarks)

        if area >= self.min_area:  # only return current distance, if the area is bigger than the min area
            distance_in_mm = self.distance_finder(distance_in_pixel)
            self.last_distance = distance_in_mm
            return distance_in_mm
        else:
            return self.last_distance

    def get_pixel_distance(self, landmarks, init_focal_length=False):
        try:
            x1 = landmarks[5][2][0]
            y1 = landmarks[5][2][1]
            x2 = landmarks[17][2][0]
            y2 = landmarks[17][2][1]
            _x3 = landmarks[0][2][0]
            _y3 = landmarks[0][2][1]

            distance_5_17 = math.sqrt(math.pow(abs(x1 - x2), 2) + math.pow(abs(y1 - y2), 2))
            distance_17_0 = math.sqrt(math.pow(abs(_x3 - x2), 2) + math.pow(abs(_x3 - y2), 2))
            area = distance_5_17 * distance_17_0 / 2

            # use pythagoras to calculate the distance between landmark 5 and 17 in pixel
            distance_in_pixel = math.sqrt(math.pow(abs(x1 - x2), 2) + math.pow(abs(y1 - y2), 2))

            if init_focal_length:
                self.focal_length = self.focal_fength_finder(self.KNOWN_DISTANCE, self.KNOWN_WIDTH, distance_in_pixel)
                self.min_area = area * (1 - self.min_area_threshold)
            else:
                return distance_in_pixel, area
        except IndexError:
            pass

    def focal_fength_finder(self, measured_distance, real_width, width_in_rf_image):
        # finding the focal length
        focal_length = (width_in_rf_image * measured_distance) / real_width
        return focal_length

    def distance_finder(self, distance_in_pixel):
        distance_in_mm = (self.KNOWN_WIDTH * self.focal_length) / distance_in_pixel
        # return the distance
        return distance_in_mm
