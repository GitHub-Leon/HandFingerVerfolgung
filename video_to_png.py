import os

import cv2

"""
This script is used to convert a video into single frames to use them for annotation when training a custom model
"""


# Create the output folder if it doesn't exist
if not os.path.exists("object_tracking/custom_model/training_frames"):
    os.makedirs("object_tracking/custom_model/training_frames")

# Open the video file
video = cv2.VideoCapture("Vid_2.MOV")

# Find the number of frames in the video
total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

# Go through all the frames in the video
for frame_number in range(total_frames):
    # Read the current frame
    success, frame = video.read()

    # Check if the frame was read successfully
    if not success:
        break

    # Save the current frame as a PNG file in the output folder
    if frame_number % 10 == 0:  # only save every 10th frame, to not have to scan 1.8k/min similar frames (if 30fps)
        cv2.imwrite("object_tracking/training_frames/vid_2_frame_{}.png".format(frame_number + 1), frame)

# Release the video capture object
video.release()
