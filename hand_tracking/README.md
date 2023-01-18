# Hand Tracker and Hand Distance to Camera
This repository contains two Python scripts that perform hand tracking and calculate the distance of a hand from the camera, respectively.
There is also a folder called `drawing` which contains helper methods for plotting a landmark position onto a graph using `matplotlib`.

## Requirements
The following packages are required to run the scripts:

- `cv2`
- `mediapipe`
- `math`
- `matplotlib`
- `numpy`

### hand_tracker.py
This script contains a HandTracker class that can be used to detect and track hand landmarks in an image. It has the following methods:

`__init__(self, mode=False, max_hands=2, detection_con=0.5, model_complexity=1, track_con=0.5)` <br>
This method initializes the HandTracker object with the specified parameters.

- `mode`: a boolean value indicating whether the hand tracker should run in real-time mode or not.
- `max_hands`: the maximum number of hands that can be detected in an image.
- `detection_con`: the detection confidence threshold.
- `model_complexity`: the complexity of the model used for hand detection.
- `track_con`: the tracking confidence threshold.

`hands_finder(self, image, draw=True)`<br>
This method processes the specified image to detect and track hand landmarks. It returns the image with the hand landmarks drawn on it if the draw flag is set to True.

`position_finder(self, image, label="None")`<br>
This method returns a list of hand landmarks for the specified image, with each landmark represented as a tuple of the form (landmark_id, x, y). The label parameter can be used to specify which hand's landmarks to return, with allowed values being "Right" or "Left". If the label parameter is set to "None", landmarks for both hands are returned.

### hand_distance_to_camera.py
This script contains a HandDistanceToCamera class that can be used to calculate the distance of a hand from the camera. It has the following methods:

`__init__(self, showDebugMessage)`<br>
This method initializes the HandDistanceToCamera object with the specified showDebugMessage flag, which determines whether debug messages should be printed or not.

`distance_to_camera(self, knownWidth, focalLength, perWidth)`<br>
This method calculates and returns the distance of an object from the camera, given the object's knownWidth, the camera's focalLength, and the object's width perWidth as it appears in the image.
