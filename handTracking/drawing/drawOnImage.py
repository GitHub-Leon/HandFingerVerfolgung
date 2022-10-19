import cv2
import numpy as np


def drawPolyline(datapoints, image):
    """
    Draws a polyline through the data points on the image
    :param datapoints: list of (x,y) tuples
    :param image: image/frame on which the polyline should be drawn
    """
    if len(datapoints) != 0:  # draws line where the index finger is
        cv2.polylines(image, [np.array(datapoints)], 0, (255, 255, 255), 2)
