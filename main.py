import configparser

import cv2

from database.database import Database
from hand_tracking.drawing.draw_on_image import draw_polyline
from hand_tracking.hand_tracker import HandTracker
from object_tracking.object_tracker import ObjectTracker
from hand_tracking.drawing.plot import plot_data, plot_distance
from hand_tracking.hand_distance_to_camera import HandDistanceToCamera


def main():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # capture live webcam frames
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('m', 'j', 'p', 'g'))
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))
    cap.set(cv2.CAP_PROP_FPS, 30.0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


    config = configparser.ConfigParser()

    config.read('config.ini')
    showImg = config['DEFAULT'].getboolean('showImg')
    drawHandLandMarks = config['DEFAULT'].getboolean('drawHandLandMarks')
    drawObjectDetection = config['DEFAULT'].getboolean('drawObjectDetection')
    showDebugMessage = config['DEFAULT'].getboolean('showDebugMessages')
    drawDetectedColor = config['DEFAULT'].getboolean('drawDetectedColor')
    drawPictureProcessCounter = config['DEFAULT'].getboolean('drawPictureProcessCounter')

    database = Database()
    hand_distance_to_camera = HandDistanceToCamera(showDebugMessage)
    handTracker = HandTracker()
    objectTracker = ObjectTracker()


    cv2_count = 0  # only needed to draw picture process count on image when debugging

    while cap.isOpened:  # while we capture the video, analyse each frame
        success, image = cap.read()

        if not success:
            print("Ignoring empty frame.")
            continue

        image = handTracker.hands_finder(cv2.flip(image, 1), drawHandLandMarks)
        landmark_list = handTracker.position_finder(image)
        landmark_list = hand_distance_to_camera.calculate_distance(landmark_list)
        objectTracker.mouse_finder(landmark_list, image, drawDetectedColor)
        image = objectTracker.object_finder(image, drawObjectDetection)  # flip image, to display selfie view
        database.database_entry(landmark_list, objectTracker.mouse_box,
                                objectTracker.keyboard_box)  # log everything in DB

        # show number of processed picture on screen
        if drawPictureProcessCounter:
            cv2.putText(image, str(cv2_count), (50, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
            cv2_count = cv2_count + 1

        # Flip the image horizontally for a selfie-view display.
        if showImg:
            cv2.imshow("Hand- und Fingerverfolgung", image)

        cv2.waitKey(30)  # frame updates per second

    cap.release()


if __name__ == '__main__':
    main()
