import configparser

import cv2

from database.database import Database
from hand_tracking.hand_tracker import HandTracker
from object_tracking.object_tracker import ObjectTracker


def main():
    cap = cv2.VideoCapture(0)  # capture live webcam frames
    handTracker = HandTracker()
    objectTracker = ObjectTracker()
    config = configparser.ConfigParser()
    database = Database()

    config.read('config.ini')
    showImg = config['DEFAULT'].getboolean('showImg')
    drawPolyLine = config['DEFAULT'].getboolean('drawPolyLine')
    drawHandLandMarks = config['DEFAULT'].getboolean('drawHandLandMarks')
    drawObjectDetection = config['DEFAULT'].getboolean('drawObjectDetection')
    showDebugMessage = config['DEFAULT'].getboolean('showDebugMessages')
    drawDetectedColor = config['DEFAULT'].getboolean('drawDetectedColor')

    while cap.isOpened:  # while we capture the video, analyse each frame
        success, image = cap.read()

        if not success:
            print("Ignoring empty frame.")
            continue

        image = handTracker.hands_finder(cv2.flip(image, 1), drawHandLandMarks)
        landmark_list = handTracker.position_finder(image)
        objectTracker.mouse_finder(landmark_list, image, drawDetectedColor)
        image = objectTracker.object_finder(image, drawObjectDetection)  # flip image, to display selfie view
        database.database_entry(landmark_list, objectTracker.mouse_box)  # log everything in DB

        # to draw polyline
        # if drawPolyLine:
        #     draw_polyline(test_data_points, image)

        # Flip the image horizontally for a selfie-view display.
        if showImg:
            cv2.imshow("Hand- und Fingerverfolgung", image)

        cv2.waitKey(30)  # frame updates per second

    cap.release()


if __name__ == '__main__':
    main()
