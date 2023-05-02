import configparser

import cv2

from database.database import Database
from hand_tracking.hand_distance_to_camera import HandDistanceToCamera
from hand_tracking.hand_tracker import HandTracker
from object_tracking.object_tracker import ObjectTracker


def main():
    cap = cv2.VideoCapture(0)  # capture live webcam frames
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    config = configparser.ConfigParser()

    config.read('config.ini')
    showImg = config['DEFAULT'].getboolean('showImg')
    drawHandLandMarks = config['DEFAULT'].getboolean('drawHandLandMarks')
    drawObjectDetection = config['DEFAULT'].getboolean('drawObjectDetection')
    showDebugMessage = config['DEFAULT'].getboolean('showDebugMessages')
    storeInDB = config['DEFAULT'].getboolean('storeInDB')
    drawDetectedColor = config['DEFAULT'].getboolean('drawDetectedColor')
    drawPictureProcessCounter = config['DEFAULT'].getboolean('drawPictureProcessCounter')
    use_yolov3 = config['DEFAULT'].getboolean('use_yolov3')
    correctZValues = config['DEFAULT'].getboolean('correctZValues')

    database = Database(correctZValues)
    hand_distance_to_camera = HandDistanceToCamera(showDebugMessage)
    handTracker = HandTracker()
    objectTracker = ObjectTracker(use_yolov3, showDebugMessage)

    cv2_count = 0  # only needed to draw picture process count on image when debugging

    while cap.isOpened:  # while we capture the video, analyse each frame
        success, image = cap.read()

        if not success:
            if showDebugMessage:
                print("Ignoring empty frame.")
            continue

        try:
            image = handTracker.hands_finder(cv2.flip(image, 1), drawHandLandMarks)
            landmark_list = handTracker.position_finder(image)
            landmark_list = hand_distance_to_camera.calculate_distance(landmark_list)
            image = objectTracker.object_finder(image, landmark_list, drawObjectDetection, drawDetectedColor)  # flip image, to display selfie view
            if storeInDB:
                database.database_entry(landmark_list, objectTracker.mouse_box, objectTracker.keyboard_box)  # log everything in DB
        except Exception as e:
            # don't log anything, if an error occurs
            pass

        # show number of processed picture on screen
        if drawPictureProcessCounter:
            cv2.putText(image, str(cv2_count), (50, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
            cv2_count = cv2_count + 1

        # Flip the image horizontally for a selfie-view display.
        if showImg:
            cv2.imshow("Hand- und Fingerverfolgung", image)

        cv2.waitKey(1)  # waits for a key interrupt x ms

    cap.release()


if __name__ == '__main__':
    main()
