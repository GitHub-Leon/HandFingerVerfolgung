import math


class LandmarkDistanceToCamera:
    def __init__(self):
        self.KNOWN_DISTANCE = 750  # initialize the known distance from the camera to the object, which
        self.KNOWN_WIDTH = 60  # initialize the known object width, which in this case is the distance in mm between landmark 5 and 17
        self.focal_length_5_17 = None
        self.focal_length_0_17 = None

    def calculate_distance(self, landmarks):
        if self.focal_length_5_17 is None or self.focal_length_0_17 is None:
            self.get_pixel_distance(landmarks, True)
            return  # dont go further in the method until a reference length was found

        distance_in_pixel_5_17, distance_in_pixel_0_17 = self.get_pixel_distance(landmarks)

        distance_in_mm_5_17 = self.distance_finder(distance_in_pixel_5_17, self.focal_length_5_17)
        distance_in_mm_0_17 = self.distance_finder(distance_in_pixel_0_17, self.focal_length_0_17)

        if distance_in_mm_0_17 < self.KNOWN_DISTANCE:  # if hand is rotated in the x axis
            return distance_in_mm_0_17
        elif distance_in_mm_5_17 < self.KNOWN_DISTANCE:  # if hand is rotated on the y axis
            return distance_in_mm_5_17
        else:
            return self.KNOWN_DISTANCE

    def get_pixel_distance(self, landmarks, init_focal_length=False):
        try:
            x1 = landmarks[5][2][0]
            y1 = landmarks[5][2][1]
            x2 = landmarks[17][2][0]
            y2 = landmarks[17][2][1]
            x3 = landmarks[0][2][0]
            y3 = landmarks[0][2][1]

            # use pythagoras to calculate the distance between landmark 5 and 17 in pixel
            distance_in_pixel_5_17 = math.sqrt(math.pow(abs(x1 - x2), 2) + math.pow(abs(y1 - y2), 2))
            distance_in_pixel_0_17 = math.sqrt(math.pow(abs(x3 - x2), 2) + math.pow(abs(y3 - y2), 2))

            if init_focal_length:
                self.focal_length_5_17 = self.focal_length_finder(self.KNOWN_DISTANCE, self.KNOWN_WIDTH, distance_in_pixel_5_17)
                self.focal_length_0_17 = self.focal_length_finder(self.KNOWN_DISTANCE, self.KNOWN_WIDTH, distance_in_pixel_0_17)
            else:
                return distance_in_pixel_5_17, distance_in_pixel_0_17
        except IndexError:
            pass

    @staticmethod
    def focal_length_finder(measured_distance, real_width, width_in_rf_image):
        # finding the focal length
        focal_length = (width_in_rf_image * measured_distance) / real_width
        return focal_length

    def distance_finder(self, distance_in_pixel, focal_length):
        distance_in_mm = (self.KNOWN_WIDTH * focal_length) / distance_in_pixel
        # return the distance
        return distance_in_mm
