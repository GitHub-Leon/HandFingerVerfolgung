import cv2
import mediapipe as mp

from handTracking.drawing.drawOnImage import drawPolyline


class HandTracker:
    """
    Class to initialise a hand tracker. Can be used to find the image coords of certain hand landmarks
    """

    def __init__(self, mode=False, max_hands=2, detection_con=0.5, model_complexity=1, track_con=0.5):
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.model_complexity = model_complexity
        self.track_con = track_con
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(self.mode, self.max_hands, self.model_complexity, self.detection_con,
                                         self.track_con)
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.data_points = []
        self.results = []

    def handsFinder(self, image, draw=True):
        """
        function to process an image to get hand landmarks and draw them onto the image
        :param image: image which should be processed for hand detection
        :param draw: optional flag, if something needs to be drawn onto the image
        :return: image with drawn landmarks (and optionally something else)
        """
        image.flags.writeable = False  # temporarily disabled for performance
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # changed order of colors from BGR to RGB
        self.results = self.hands.process(image)

        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if self.results.multi_hand_landmarks:
            h, w, _ = image.shape
            hand_landmarks_list = []
            hands_type = []

            for hand in self.results.multi_handedness:
                hand_type = hand.classification[0].label
                hands_type.append(hand_type)

            for hand_landmarks in self.results.multi_hand_landmarks:
                hand_landmarks_list.append(hand_landmarks)

            # iterate over all stored hand landmarks with hand type data
            for hand_landmarks, hand_type in zip(hand_landmarks_list, hands_type):
                self.mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style())

                if hand_type == 'Left':
                    x = int(hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].x * w)
                    y = int(hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].y * h)
                    self.data_points.append((x, y))

                # draw polyline
                if draw:
                    drawPolyline(self.data_points, image)

        return image

    def positionFinder(self, image, hand_no=0):
        """
        function to find image coords of a certain hand
        :param image: used to get width and height
        :param hand_no:
        :return: landmark list of hand
        """
        landmark_list = []
        if self.results.multi_hand_landmarks:
            Hand = self.results.multi_hand_landmarks[hand_no]

            for id, lm in enumerate(Hand.landmark):
                h, w, c = image.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                landmark_list.append([id, cx, cy])

        return landmark_list
