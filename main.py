import cv2

from hand_tracking.drawing.draw_on_image import draw_polyline
from hand_tracking.hand_tracker import HandTracker


def main():
    cap = cv2.VideoCapture(0)  # capture live webcam frames
    tracker = HandTracker()

    test_data_points = []  # TODO: gets replaced with db prob

    while cap.isOpened:  # while we capture the video, analyse each frame
        success, image = cap.read()

        if not success:
            print("Ignoring empty frame.")
            continue

        image = tracker.hands_finder(image)
        landmark_list = tracker.position_finder(image, "Right")

        # TODO: append data to local list to display landmark (gets replaced with DB)
        try:
            test_data_points.append(landmark_list[8][2])
        except IndexError:  # landmark moved out of screen
            print("Landmark lost")

        # to draw polyline
        draw_polyline(test_data_points, image)

        # Flip the image horizontally for a selfie-view display.
        cv2.imshow("Hand- und Fingerverfolgung", cv2.flip(image, 1))
        cv2.waitKey(30)  # frame updates in ms

    cap.release()


if __name__ == '__main__':
    main()
