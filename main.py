import cv2
import mediapipe as mp
import numpy as np


def main():
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_hands = mp.solutions.hands

    cap = cv2.VideoCapture(0)  # instantiate video capturing class

    _, frame = cap.read()  # determine what width and height each frame will have
    h, w, c = frame.shape

    datapoints = []
    hands_data = []


    with mp_hands.Hands() as hands:
        while cap.isOpened():  # checks if capturing is initialized already
            success, image = cap.read()  # grabs, decodes and returns the next video frame
            if not success:
                print("Ignoring empty frame.")
                continue

            image.flags.writeable = False  # temporarily disabled for performance
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # changed order of colors from BGR to RGB
            results = hands.process(image)

            # Draw the hand annotations on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if results.multi_hand_landmarks:
                hand_landmarks_list = []
                hands_type = []

                for hand in results.multi_handedness:
                    hand_type = hand.classification[0].label
                    hands_type.append(hand_type)

                for hand_landmarks in results.multi_hand_landmarks:
                    hand_landmarks_list.append(hand_landmarks)

                # iterate over all stored hand landmarks with hand type data
                for hand_landmarks, hand_type in zip(hand_landmarks_list, hands_type):
                    mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())

                    if hand_type == 'Left':
                        x = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * w)
                        y = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * h)
                        datapoints.append((x, y))

                    # draw polyline
                    drawPolyline(datapoints, image)

            # Flip the image horizontally for a selfie-view display.
            cv2.imshow('Hand- und Fingerverfolgung', cv2.flip(image, 1))
            if cv2.waitKey(5) & 0xFF == 27:
                break
    cap.release()


def drawPolyline(datapoints, image):
    """
    Draws a polyline through the data points on the image
    :param datapoints: list of (x,y) tuples
    :param image: image/frame on which the polyline should be drawn
    """
    if len(datapoints) != 0:  # draws line where the index finger is
        cv2.polylines(image, [np.array(datapoints)], 0, (255, 255, 255), 2)


if __name__ == '__main__':
    main()
