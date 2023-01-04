import torch
import cv2
import numpy as np
import pyautogui
import pandas as pd
from torchvision.ops import nms


class ObjectTracker:
    """
    Class to initialise a object tracker. Can be used to find the image coordinates of keyboard and mouse
    """

    def __init__(self, use_yolov3, detection_con=0.3, detection_threshold=0.2):
        self.use_yolov3 = use_yolov3
        self.detection_con = detection_con
        self.detection_threshold = detection_threshold
        if self.use_yolov3:
            self.net = cv2.dnn.readNet('object_tracking/yolo-coco/yolov3.weights', 'object_tracking/yolo-coco/yolov3.cfg')
            self.classes = self.load_classes_yolov3()  # classes specified in coco.names
        else:
            self.yolov5_model = torch.hub.load('ultralytics/yolov5', 'yolov5n')  # device='cpu' # TODO
           # self.yolov5_model = torch.hub.load('ultralytics/yolov5', 'custom', path='object_tracking/custom_model/best.pt')
            self.init_model()
            self.classes = self.load_classes_yolov5()  # classes specified in coco.names

        self.colors = np.random.uniform(0, 255, size=(100, 3))  # color for bounding boxes
        self.font = cv2.FONT_HERSHEY_PLAIN  # font for bounding boxes
        self.saved_pos = pyautogui.position()  # (x, y) tuple with cursor coords
        self.replacement_threshold = 0.9  # new keyboard box area shouldn't be less than 0.9x of old box area size

        self.keyboard_box = []  # stores list of keyboard. Format: [label, confidence, (x, y, w, h)]
        self.mouse_box = []

    def init_model(self):
        self.yolov5_model.conf = self.detection_con  # NMS confidence threshold
        self.yolov5_model.iou = self.detection_threshold  # NMS IoU threshold
        self.yolov5_model.agnostic = False  # NMS class-agnostic
        self.yolov5_model.multi_label = False  # NMS multiple labels per box
        self.yolov5_model.classes = None  # (optional list) filter by class, i.e. = [0, 15, 16] for COCO persons, cats and dogs, [64, 66] for mouse and keyboard
        self.yolov5_model.max_det = 1000  # maximum number of detections per image #TODO
        self.yolov5_model.amp = False  # Automatic Mixed Precision (AMP) inference #TODO

    @staticmethod
    def load_classes_yolov3():
        """
        load the COCO class labels our YOLO model was trained on
        :return: list of classes
        """

        classes = []
        with open('object_tracking/yolo-coco/coco.names', 'r') as file:
            classes = file.read().splitlines()

        return classes

    @staticmethod
    def load_classes_yolov5():
        """
        load the COCO class labels our YOLO model was trained on
        :return: list of classes
        """

        classes = []
        with open('object_tracking/custom_model/coco.names', 'r') as file:
            classes = file.read().splitlines()

        return classes

    def object_finder(self, image, landmarks, draw=True, drawDetectedColor=False):
        """
        function to process an image to get hand landmarks and draw them onto the image
        :param image: image which should be processed for hand detection
        :param draw: optional flag, if landmarks need to be drawn on image
        :return: image (with optionally drawn landmarks)
        """

        height, width, _ = image.shape

        boxes = []
        confidences = []
        class_ids = []

        if self.use_yolov3:
            blob = cv2.dnn.blobFromImage(image, 1 / 255, (416, 416), (0, 0, 0), swapRB=True, crop=False)
            self.net.setInput(blob)
            output_layers_names = self.net.getUnconnectedOutLayersNames()
            layerOutputs = self.net.forward(output_layers_names)

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
        else:
            results = self.yolov5_model(image)
            results.print()
            results = results.pandas().xyxy[0]
            # Extract the bounding boxes, confidence scores, and class labels from the results
            results[['xmin', 'ymin', 'xmax', 'ymax']] = results[['xmin', 'ymin', 'xmax', 'ymax']].apply(pd.to_numeric)
            for xmin, ymin, xmax, ymax in results[['xmin', 'ymin', 'xmax', 'ymax']].values:
                boxes.append([int(xmin), int(ymin), int(xmax - xmin), int(ymax - ymin)])

            results['confidence'] = results['confidence'].apply(pd.to_numeric)
            for confidence in results['confidence']:
                confidences.append(confidence)

            results['class'] = results['class'].apply(pd.to_numeric)
            for class_id in results['class']:
                class_ids.append(class_id)


            if len(boxes) > 0:
                indexes = nms(torch.tensor(boxes, dtype=torch.float), torch.tensor(confidences, dtype=torch.float), 0.4).numpy()
                # indexes = np.arange(len(boxes))
            else:
                indexes = []

        if len(indexes) > 0:
            self.check_for_boxes(indexes, boxes, confidences, class_ids)

        self.mouse_finder(landmarks, image, drawDetectedColor)

        # draw devices
        for device in self.keyboard_box:
            x, y, w, h = device[2]
            label = device[0]
            confidence = device[1]
            color = self.colors[x % 100]

            if draw:  # only draw boxes when option is enabled (Default)
                cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
                cv2.putText(image, label + " " + str(confidence), (x, y + 20), self.font, 2, color, 2)

        for device in self.mouse_box:
            x, y, w, h = device[2]
            label = device[0]
            confidence = device[1]

            if draw:  # only draw boxes when option is enabled (Default)
                cv2.rectangle(image, (x, y), (x + w, y + h), self.colors[60], 2)
                cv2.putText(image, label + " " + str(confidence), (x, y+h + 20), self.font, 2, self.colors[60], 2)

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

                    if (x > dx * 1.2 or x < dx * 0.8 or y > dy * 1.2 or y < dy * 0.8) or device[1] < confidence:  # check if detected keyboard is way off currently saved one or if the confidence is higher than the saved one
                        if (dw * dh * self.replacement_threshold) < (w * h) < (dw * dh * ((1 - self.replacement_threshold) + 1)):  # if the new box is far smaller than allowed, dont update it (possibility of false detection)
                            self.keyboard_box.remove(device)
                            self.keyboard_box.append([label, confidence, (x, y, w, h)])
                        break

            for device in self.mouse_box:
                if device[0] == label:
                    self.mouse_box.remove(device)
                    self.mouse_box.append([label, confidence, (x, y, w, h)])

            if len(self.keyboard_box) == 0 and label == "keyboard":
                self.keyboard_box.append([label, confidence, (x, y, w, h)])
            if not self.use_yolov3 and len(self.mouse_box) == 0 and label == 'mouse':
                self.mouse_box.append([label, confidence, (x, y, w, h)])


    def mouse_finder(self, landmarks, image, drawDetectedColor):
        """
        This function gets the current cursor position and updates self.mouse_box with new landmark coords when moved
        If it finds a color point, which indicates our mouse, it uses this instead
        :param image: Image that gets processed to search color points
        :param landmarks: list of hand landmarks to get finger position
        """

        if self.use_yolov3:
            # defined upper and lower bounds on the color spectrum for the color we are searching for
            lower_color = np.array([170, 80, 80])
            upper_color = np.array([190, 255, 255])

            # converts the image to mask the colors defined above and get all the points of the color
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            mask_color = cv2.inRange(hsv, lower_color, upper_color)
            points = cv2.findNonZero(mask_color)

            if drawDetectedColor:  # draws the contours of the detected color
                res_color = cv2.bitwise_and(image, image, mask=mask_color)
                gray_color = cv2.cvtColor(res_color, cv2.COLOR_BGR2GRAY)
                _, thresh_color = cv2.threshold(gray_color, 10, 255, cv2.THRESH_BINARY)
                contours_color, hierarchy1 = cv2.findContours(thresh_color, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                cv2.drawContours(image, contours_color, -1, (0, 0, 255), 2)

            if points is not None and len(points) > 50:  # threshold for other color points on screen
                avg = np.mean(points, axis=0)  # get position of avg point
                self.mouse_box.clear()
                self.mouse_box.append(['mouse', 0, (int(avg[0][0] - 30), int(avg[0][1] + 60), int(avg[0][0] + 30)-int(avg[0][0] - 30), int(avg[0][1] - 10)-int(avg[0][1] + 60))])
            else:
                current_pos = pyautogui.position()

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
                        y_1 = min(mmy, imy)
                        x_2 = max(mtx, mmx)
                        y_2 = max(ity, mty, tty)

                        self.mouse_box.clear()
                        self.mouse_box.append(['mouse', 0, (x_1, y_1, x_2 - x_1, y_2 - y_1)])
        else:
            current_pos = pyautogui.position()

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
                    y_1 = min(mmy, imy)
                    x_2 = max(mtx, mmx)
                    y_2 = max(ity, mty, tty)

                    self.mouse_box.clear()
                    self.mouse_box.append(['mouse', 0, (x_1, y_1, x_2-x_1, y_2-y_1)])
