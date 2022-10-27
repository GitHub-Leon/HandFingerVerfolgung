import cv2

from hand_tracking.drawing.draw_on_image import draw_polyline
from hand_tracking.hand_tracker import HandTracker
from object_tracking.object_tracker import ObjectTracker


def main():
    cap = cv2.VideoCapture(0)  # capture live webcam frames
    handTracker = HandTracker()
    objectTracker = ObjectTracker()

    test_data_points = []  # TODO: gets replaced with db prob

    while cap.isOpened:  # while we capture the video, analyse each frame
        success, image = cap.read()

        if not success:
            print("Ignoring empty frame.")
            continue

        image = objectTracker.object_finder(cv2.flip(image, 1))  # flip image, to display selfie view
        image = handTracker.hands_finder(image)
        landmark_list = handTracker.position_finder(image, "Right")


        # TODO: append data to local list to display landmark (gets replaced with DB)
        # try:
        #     test_data_points.append(landmark_list[8][2])
        # except IndexError:  # landmark moved out of screen
        #     print("Landmark lost")

        # to draw polyline TODO: option to enable it
        # draw_polyline(test_data_points, image)

        # Flip the image horizontally for a selfie-view display.
        cv2.imshow("Hand- und Fingerverfolgung", image)
        cv2.waitKey(30)  # frame updates in ms

    cap.release()


if __name__ == '__main__':
    main()
