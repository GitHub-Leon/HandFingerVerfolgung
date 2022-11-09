import configparser

import cv2

from hand_tracking.drawing.draw_on_image import draw_polyline
from hand_tracking.hand_tracker import HandTracker
from object_tracking.object_tracker import ObjectTracker
import numpy as np


def main():
    cap = cv2.VideoCapture(0)  # capture live webcam frames
    handTracker = HandTracker()
    objectTracker = ObjectTracker()
    config = configparser.ConfigParser()

    config.read('config.ini')
    showImg = config['DEFAULT'].getboolean('showImg')
    drawPolyLine = config['DEFAULT'].getboolean('drawPolyLine')
    drawHandLandMarks = config['DEFAULT'].getboolean('drawHandLandMarks')
    drawObjectDetection = config['DEFAULT'].getboolean('drawObjectDetection')
    showDebugMessage = config['DEFAULT'].getboolean('showDebugMessages')

    test_data_points = []  # TODO: gets replaced with db prob

    while cap.isOpened:  # while we capture the video, analyse each frame
        success, image = cap.read()

        if not success:
            print("Ignoring empty frame.")
            continue

        image = handTracker.hands_finder(cv2.flip(image, 1), drawHandLandMarks)
        landmark_list = handTracker.position_finder(image, "Right")
        objectTracker.mouse_finder(landmark_list, image)
        image = objectTracker.object_finder(image, drawObjectDetection)  # flip image, to display selfie view

        # TODO: append data to local list to display landmark (gets replaced with DB)
        try:
            x, y, z = landmark_list[8][2]
            test_data_points.append((x, y))
        except IndexError:  # landmark moved out of screen
            if showDebugMessage:
                print("Landmark lost")

        # to draw polyline
        if drawPolyLine:
            draw_polyline(test_data_points, image)

        # Flip the image horizontally for a selfie-view display.
        if showImg:
            cv2.imshow("Hand- und Fingerverfolgung", image)

        cv2.waitKey(30)  # frame updates in ms

    cap.release()


if __name__ == '__main__':
    main()
