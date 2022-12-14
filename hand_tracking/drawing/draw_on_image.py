import cv2
import numpy as np


def draw_polyline(data_points, image):
    """
    Draws a polyline through the data points on the image
    :param data_points: list of (x,y) tuples
    :param image: image/frame on which the polyline should be drawn
    """

    if len(data_points[0][2][2]) != 0:  # draws line where the index finger is
        cv2.polylines(image, [np.array(data_points[0][2][2])], 0, (255, 255, 255), 2)
