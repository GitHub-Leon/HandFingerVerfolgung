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

        # image = handTracker.hands_finder(cv2.flip(image, 1), drawHandLandMarks)
        # landmark_list = handTracker.position_finder(image, "Right")
        # objectTracker.mouse_finder(landmark_list)
        # image = objectTracker.object_finder(image, drawObjectDetection)  # flip image, to display selfie view
        #
        # # TODO: append data to local list to display landmark (gets replaced with DB)
        # try:
        #     x, y, z = landmark_list[8][2]
        #     test_data_points.append((x, y))
        # except IndexError:  # landmark moved out of screen
        #     if showDebugMessage:
        #         print("Landmark lost")
        #
        # # to draw polyline
        # if drawPolyLine:
        #     draw_polyline(test_data_points, image)

        cv2.imshow("Hand- und Fingerverfolgungqwrqwr", image.copy())
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        cv2.imshow("Hand", hsv.copy())
        # lower_yellow = np.array([20, 0, 0])
        # upper_yellow = np.array([25, 255, 255])
        lower_color = np.array([170, 80, 80])
        upper_color = np.array([190, 255, 255])
        mask_color = cv2.inRange(hsv, lower_color, upper_color)
        res_color = cv2.bitwise_and(image, image, mask=mask_color)
        points = cv2.findNonZero(mask_color)

        if points is not None:
            if (len(points > 1)):
                avg = np.mean(points, axis=0)
                cv2.rectangle(image, (int(avg[0][0] - 10), int(avg[0][1] - 10)), (int(avg[0][0] + 10), int(avg[0][1] + 10)), [100, 100, 100], 2)


        cv2.imshow("mask", mask_color)
        # # define kernel size
        # kernel = np.ones((7, 7), np.uint8)
        # # Remove unnecessary noise from mask
        # mask_color = cv2.morphologyEx(mask_color, cv2.MORPH_CLOSE, kernel)
        # mask_color = cv2.morphologyEx(mask_color, cv2.MORPH_OPEN, kernel)


        gray_yellow = cv2.cvtColor(res_color, cv2.COLOR_BGR2GRAY)
        _, thresh_yellow = cv2.threshold(gray_yellow, 10, 255, cv2.THRESH_BINARY)
        contours_yellow, hierarhy3 = cv2.findContours(thresh_yellow, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(image, contours_yellow, -1, (0, 0, 255), 2)

        # Flip the image horizontally for a selfie-view display.
        if showImg:
            cv2.imshow("Hand- und Fingerverfolgung", image)

        cv2.waitKey(30)  # frame updates in ms

    cap.release()


if __name__ == '__main__':
    main()
