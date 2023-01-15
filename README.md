# Project: Hand and Finger Tracking during Computer Work

This project aims to track the hand and finger movements of a user while they work at a computer. The code captures live webcam frames, detects the hand and finger landmarks, calculates the distance of the hand to the camera, and tracks object detection (currently just a mouse and keyboard). The detected information is logged in a database.

## Installation

1. Install python 3.8 from the official website:<br>
   https://www.python.org/downloads/

2. Clone the repository to your local machine:<br>
   ```bash
   git clone https://github.com/GitHub-Leon/hand-finger-tracking.git
   ```

3. Go to the file<br>
   ```bash
   cd hand-finger-tracking
   ```
   
4. Install the required packages listed in [requirements.txt](https://github.com/GitHub-Leon/HandFingerVerfolgung/blob/master/requirements.txt):
   ```bash
   pip install -r requirements.txt
   ```

5. Install the necessary libraries and versions for YOLOv5 with GPU usage
   ```bash
    pip install torch==1.13.1+cu117 torchvision==0.14.1+cu117 torchaudio===0.13.1 -f https://download.pytorch.org/whl/torch_stable.html
   ```
## Configuration

You can configure the following options in the [config.ini](https://github.com/GitHub-Leon/HandFingerVerfolgung/blob/master/config.ini) file:
- `showImg`: set to `True` to display the webcam frames with the detected hand and finger landmarks and object detection. Set to `False` to disable this display.
- `drawHandLandMarks`: set to `True` to draw the detected hand and finger landmarks on the webcam frames. Set to `False` to disable this.
- `drawObjectDetection`: set to `True` to draw bounding boxes around the detected mouse and keyboard on the webcam frames. Set to `False` to disable this.
- `showDebugMessages`: set to `True` to display debug messages during runtime. Set to `False` to disable this.
- `drawDetectedColor`: set to `True` to draw a circle around the dominant color detected in the bounding boxes of the detected mouse and keyboard. Set to `False` to disable this.
- `storeInDB`: set to `True` to store the data in the database. Set to `False` to not save it.
- `drawPictureProcessCounter`: set to `True` to draw the number of processed frames on the webcam frames. Set to `False` to disable this.
- 'correctZValues': set to `True` to correct the Z Values of the landmarks depending on the settings in database.py. Set to `False` to disable this. 
- `use_yolov3`: set to `True` to use the YOLOv3 object detector. Set to `False` to use YOLOv5.

## Usage

1. Run the script:<br>
   ```bash
   python main.py
   ```
2. The webcam frames will be captured and the hand and finger landmarks, object detection, and distances will be calculated and displayed (if enabled in the configuration). The detected information will also be logged in the database.

