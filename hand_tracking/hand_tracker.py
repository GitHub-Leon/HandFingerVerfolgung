import cv2
import mediapipe as mp

# Import mediapipe hands module and hand drawing module
class HandTracker:
    """
    Class to initialise a hand tracker. Can be used to find the image coordinates of certain hand landmarks
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
        self.results = []

    def hands_finder(self, image, draw=True):
        """
        function to process an image to get hand landmarks and draw them onto the image
        :param image: image which should be processed for hand detection
        :param draw: optional flag, if landmarks need to be drawn on image
        :return: image (with optionally drawn landmarks)
        """
        # Temporarily disable writeable flag for performance
        image.flags.writeable = False
        # Change order of colors from BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # Detect hands in the image
        self.results = self.hands.process(image)
        # Enable writeable flag
        image.flags.writeable = True
        # Change order of colors back to BGR
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        # Draw hand landmarks on image if desired
        if draw and self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style())

        return image

    def position_finder(self, image, label="None"):
        """
        function to find image coordinates of a certain hand
        :param image: used to get width and height
        :param label: "Right" or "Left" allowed, if both hands should be returned, default value "None" must be applied
        :return: landmark list of hand in form [landmark_id, x, y]
        """
        # Initialize empty list to store hand landmarks
        return_landmark_list = []
        if self.results.multi_hand_landmarks:
            # Get image dimensions
            h, w, _ = image.shape
            # Initialize lists to store hand landmarks and hand types
            hand_landmarks_list = []
            hands_type = []

            # Iterate over detected hands and store their types
            for hand in self.results.multi_handedness:
                hand_type = hand.classification[0].label
                hands_type.append(hand_type)

            # Iterate over detected hands and store their landmarks
            for hand_landmarks in self.results.multi_hand_landmarks:
                hand_landmarks_list.append(hand_landmarks)

            # Iterate over stored hand landmarks and hand types
            for hand_landmarks, hand_type in zip(hand_landmarks_list, hands_type):
                # If hand type matches the specified label or label is set to "None"
                if hand_type == label or label == "None":
                    # Iterate over landmarks and store their image coordinates
                    for landmark_id, lm in enumerate(hand_landmarks.landmark):
                        cx, cy, z = int(lm.x * w), int(lm.y * h), lm.z
                        return_landmark_list.append([hand_type, landmark_id, (cx, cy, z)])

        return return_landmark_list
