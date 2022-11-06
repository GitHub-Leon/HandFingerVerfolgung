import cv2
import numpy as np
import win32api


class ObjectTracker:
    """
    Class to initialise a object tracker. Can be used to find the image coordinates of keyboard and mouse
    """

    def __init__(self, detection_con=0.1, detection_threshold=0.2):
        self.detection_con = detection_con
        self.detection_threshold = detection_threshold
        self.net = cv2.dnn.readNet('object_tracking/yolo-coco/yolov3.weights', 'object_tracking/yolo-coco/yolov3.cfg')
        self.classes = self.load_classes()  # classes specified in coco.names
        self.colors = np.random.uniform(0, 255, size=(100, 3))  # color for bounding boxes
        self.font = cv2.FONT_HERSHEY_PLAIN  # font for bounding boxes
        self.saved_pos = win32api.GetCursorPos()  # (x, y) tuple with cursor coords
        self.replacement_threshold = 0.9  # new keyboard box area shouldn't be less than 0.9x of old box area size

        self.keyboard_box = []  # stores list of keyboard. Format: [label, confidence, (x, y, w, h)]
        self.mouse_box = [(0, 0), (0, 0)]

    @staticmethod
    def load_classes():
        """
        load the COCO class labels our YOLO model was trained on
        :return: list of classes
        """

        classes = []
        with open('object_tracking/yolo-coco/coco.names', 'r') as file:
            classes = file.read().splitlines()

        return classes

    def object_finder(self, image, draw=True):
        """
        function to process an image to get hand landmarks and draw them onto the image
        :param image: image which should be processed for hand detection
        :param draw: optional flag, if landmarks need to be drawn on image
        :return: image (with optionally drawn landmarks)
        """

        height, width, _ = image.shape

        blob = cv2.dnn.blobFromImage(image, 1 / 255, (416, 416), (0, 0, 0), swapRB=True, crop=False)
        self.net.setInput(blob)
        output_layers_names = self.net.getUnconnectedOutLayersNames()
        layerOutputs = self.net.forward(output_layers_names)

        boxes = []
        confidences = []
        class_ids = []

        for output in layerOutputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > self.detection_con:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append((float(confidence)))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, self.detection_threshold, 0.4)

        if len(indexes) > 0:
            self.check_for_boxes(indexes, boxes, confidences, class_ids)

        for device in self.keyboard_box:
            x, y, w, h = device[2]
            label = device[0]
            confidence = device[1]
            color = self.colors[x % 100]

            if draw:  # only draw boxes when option is enabled (Default)
                cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
                cv2.putText(image, label + " " + confidence, (x, y + 20), self.font, 2, color, 2)

        x_1, y_1 = self.mouse_box[0]
        x_2, y_2 = self.mouse_box[1]

        if draw and self.mouse_box[0][0] != 0:  # only draw, if mouse isn't at default values
            cv2.rectangle(image, (x_1, y_1), (x_2, y_2), self.colors[60], 2)
            cv2.putText(image, "mouse", (x_1, y_2), self.font, 2, self.colors[60], 2)

        return image

    def check_for_boxes(self, indexes, boxes, confidences, class_ids):
        """
        Checks the boxes of each recognized pattern, and checks if the stored one has a lower confidence level and
        replaces it afterwards
        :param indexes: a NMSBox with boxes, confidences regarding a certain threshold
        :param boxes: list of boxes found
        :param confidences: list of confidences
        """

        for index in indexes.flatten():
            x, y, w, h = boxes[index]
            label = str(self.classes[class_ids[index]])
            confidence = str(round(confidences[index], 2))

            for device in self.keyboard_box:
                if device[0] == label:
                    dx, dy, dw, dh = device[2]

                    if (x > dx*1.2 or x < dx*0.8 or y > dy*1.2 or y < dy*0.8) or device[1] < confidence:  # check if detected keyboard is way off currently saved one or if the confidence is higher than the saved one
                        if (dw * dh * self.replacement_threshold) < (w * h) < (dw * dh * ((1 - self.replacement_threshold) + 1)):  # if the new box is far smaller than allowed, dont update it (possibility of false detection)
                            self.keyboard_box.remove(device)
                            self.keyboard_box.append([label, confidence, (x, y, w, h)])
                        break

            if len(self.keyboard_box) == 0 and label == "keyboard":
                self.keyboard_box.append([label, confidence, (x, y, w, h)])

    def mouse_finder(self, landmarks):
        """
        This function gets the current cursor position and updates self.mouse_box with new landmark coords when moved
        :param landmarks: list of hand landmarks to get finger position
        """

        current_pos = win32api.GetCursorPos()
        if self.saved_pos != current_pos:
            self.saved_pos = current_pos

            if len(landmarks) != 0:
                itx, ity, _ = landmarks[8][2]  # index finger tip coords
                imx, imy, _ = landmarks[5][2]  # index finger mcp coords
                mtx, mty, _ = landmarks[12][2]  # middle finger tip coords
                mmx, mmy, _ = landmarks[9][2]  # middle finger mcp coords
                ttx, tty, _ = landmarks[4][2]  # thumb tip coords

                # get outer coords to define a clean rectangle for the mouse
                x_1 = min(itx, imx, ttx)
                y_1 = max(ity, mty, tty)
                x_2 = max(mtx, mmx)
                y_2 = min(mmy, imy)

                self.mouse_box = [(x_1, y_1), (x_2, y_2)]
