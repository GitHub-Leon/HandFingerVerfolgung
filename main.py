import cv2

from handTracking.handTracker import HandTracker


def main():
    cap = cv2.VideoCapture(0)  # capture live webcam frames
    tracker = HandTracker()

    while cap.isOpened:
        success, image = cap.read()

        if not success:
            print("Ignoring empty frame.")
            continue

        image = tracker.handsFinder(image)
        landmark_list = tracker.positionFinder(image)

        # Flip the image horizontally for a selfie-view display.
        cv2.imshow("Hand- und Fingerverfolgung", cv2.flip(image, 1))
        cv2.waitKey(30)  # updates in ms

    cap.release()


if __name__ == '__main__':
    main()
