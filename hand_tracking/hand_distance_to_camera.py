import math


class HandDistanceToCamera:
    def __init__(self, showDebugMessage):
        self.showDebugMessage = showDebugMessage
        self.KNOWN_DISTANCE = 750  # initialize the known distance from the camera to the hand, which in this case is 75cm (750mm)
        self.KNOWN_WIDTH_5_17 = 60  # initialize the known object width, which in this case is the distance in mm between landmark 5 and 17
        self.KNOWN_WIDTH_0_17 = 100  # initialize the known object width, which in this case is the distance in mm between landmark 0 and 17
        self.left_focal_length_5_17 = None
        self.left_focal_length_0_17 = None
        self.right_focal_length_5_17 = None
        self.right_focal_length_0_17 = None

    def calculate_distance(self, landmarks):
        """
        Calculates the distance from the camera to the object based on the landmarks.
        :param landmarks: landmark list, which is returned by hand_tracker.position_finder # ['Right', 3, (537, 239, -0.07019183784723282), 75]
        """

        # 0 = 0, 1 = 5, 2 = 17
        right = []
        left = []

        left_distance = self.KNOWN_DISTANCE
        right_distance = self.KNOWN_DISTANCE

        # get relevant landmarks for calculation
        for landmark in landmarks:
            if landmark[0] == 'Right':
                if landmark[1] == 0 or landmark[1] == 5 or landmark[1] == 17:  # we get them in the right order already, so appending is enough (no insert necessary)
                    right.append(landmark)
            if landmark[0] == 'Left':
                if landmark[1] == 0 or landmark[1] == 5 or landmark[1] == 17:
                    left.append(landmark)

        # check if the focal lengths have been initialized, if not, get the pixel distance for reference
        if len(left) == 3:
            if self.left_focal_length_5_17 is None or self.left_focal_length_0_17 is None:
                self.get_pixel_distance(left, 'Left', True)
                if self.showDebugMessage:
                    print("Left hand calibrated")

            # get the pixel distances for landmarks 5 and 17, and landmarks 0 and 17
            distance_in_pixel_left_5_17, distance_in_pixel_left_0_17 = self.get_pixel_distance(left, 'Left')

            # calculate the distance in millimeters for landmarks 5 and 17, and landmarks 0 and 17
            distance_in_mm_left_5_17 = self.distance_finder(distance_in_pixel_left_5_17, self.left_focal_length_5_17, self.KNOWN_WIDTH_5_17)
            distance_in_mm_left_0_17 = self.distance_finder(distance_in_pixel_left_0_17, self.left_focal_length_0_17, self.KNOWN_WIDTH_0_17)

            if distance_in_mm_left_0_17 < self.KNOWN_DISTANCE:  # if hand is rotated in the x axis
                left_distance = distance_in_mm_left_0_17
            elif distance_in_mm_left_5_17 < self.KNOWN_DISTANCE:  # if hand is rotated on the y axis
                left_distance = distance_in_mm_left_5_17

        if len(right) == 3:
            if self.right_focal_length_5_17 is None or self.right_focal_length_0_17 is None:
                self.get_pixel_distance(right, 'Right', True)
                if self.showDebugMessage:
                    print("Right hand calibrated")

            # get the pixel distances for landmarks 5 and 17, and landmarks 0 and 17
            distance_in_pixel_right_5_17, distance_in_pixel_right_0_17 = self.get_pixel_distance(right, 'Right')

            # calculate the distance in millimeters for landmarks 5 and 17, and landmarks 0 and 17
            distance_in_mm_right_5_17 = self.distance_finder(distance_in_pixel_right_5_17, self.right_focal_length_5_17, self.KNOWN_WIDTH_5_17)
            distance_in_mm_right_0_17 = self.distance_finder(distance_in_pixel_right_0_17, self.right_focal_length_0_17, self.KNOWN_WIDTH_0_17)

            if distance_in_mm_right_0_17 < self.KNOWN_DISTANCE:  # if hand is rotated in the x axis
                right_distance = distance_in_mm_right_0_17
            elif distance_in_mm_right_5_17 < self.KNOWN_DISTANCE:  # if hand is rotated on the y axis
                right_distance = distance_in_mm_right_5_17

        for landmark in landmarks:
            if landmark[0] == 'Left':
                landmark.insert(3, left_distance)
            elif landmark[0] == 'Right':
                landmark.insert(3, right_distance)

        return landmarks

    def get_pixel_distance(self, landmarks, hand=None, init_focal_length=False):
        """
        Gets the pixel distance between two landmarks.
        :param hand: 'Left' or 'Right'
        :param landmarks: landmark list, which is returned by hand_tracker.position_finder
        :param init_focal_length: set to True, if you want to save the current distance of the landmarks as a reference
        """

        # try:
        # get the x and y coordinates of the landmarks
        x1 = landmarks[1][2][0]  # x coordinate of landmark 5
        y1 = landmarks[1][2][1]  # y coordinate of landmark 5
        x2 = landmarks[2][2][0]  # x coordinate of landmark 17
        y2 = landmarks[2][2][1]  # y coordinate of landmark 17
        x3 = landmarks[0][2][0]  # x coordinate of landmark 0
        y3 = landmarks[0][2][1]  # y coordinate of landmark 0

        # use pythagoras to calculate the distance between landmark 5 and 17, and 0 and 17 in pixels
        distance_in_pixel_5_17 = math.sqrt(math.pow(abs(x1 - x2), 2) + math.pow(abs(y1 - y2), 2))
        distance_in_pixel_0_17 = math.sqrt(math.pow(abs(x3 - x2), 2) + math.pow(abs(y3 - y2), 2))

        if init_focal_length:
            if hand == 'Left':
                # initialize focal length for distance between landmark 5 and 17
                self.left_focal_length_5_17 = self.focal_length_finder(self.KNOWN_DISTANCE, self.KNOWN_WIDTH_5_17,
                                                                       distance_in_pixel_5_17)
                # initialize focal length for distance between landmark 0 and 17
                self.left_focal_length_0_17 = self.focal_length_finder(self.KNOWN_DISTANCE, self.KNOWN_WIDTH_0_17,
                                                                       distance_in_pixel_0_17)
            elif hand == 'Right':
                # initialize focal length for distance between landmark 5 and 17
                self.right_focal_length_5_17 = self.focal_length_finder(self.KNOWN_DISTANCE, self.KNOWN_WIDTH_5_17,
                                                                        distance_in_pixel_5_17)
                # initialize focal length for distance between landmark 0 and 17
                self.right_focal_length_0_17 = self.focal_length_finder(self.KNOWN_DISTANCE, self.KNOWN_WIDTH_0_17,
                                                                        distance_in_pixel_0_17)
        else:
            # return pixel distances between landmark 5 and 17, and 0 and 17
            return distance_in_pixel_5_17, distance_in_pixel_0_17
        # except IndexError:
        #     pass

    @staticmethod
    def focal_length_finder(measured_distance, real_width, width_in_rf_image):
        # finding the focal length
        focal_length = (width_in_rf_image * measured_distance) / real_width
        return focal_length

    @staticmethod
    def distance_finder(distance_in_pixel, focal_length, known_width):
        # calculate distance in millimeters
        distance_in_mm = (known_width * focal_length) / distance_in_pixel
        # return the distance
        return distance_in_mm
