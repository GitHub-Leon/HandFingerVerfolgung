import cv2
import numpy as np


class ObjectTracker:
    def __init__(self, detection_con=0.2, detection_threshold=0.2):
        self.detection_con = detection_con
        self.detection_threshold = detection_threshold
        self.net = cv2.dnn.readNet('object_tracking/yolo-coco/yolov3.weights', 'object_tracking/yolo-coco/yolov3.cfg')
        self.classes = self.load_classes()  # classes specified in coco.names
        self.colors = np.random.uniform(0, 255, size=(100, 3))  # color for bounding boxes
        self.font = cv2.FONT_HERSHEY_PLAIN  # font for bounding boxes

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

        if draw:  # only draw boxes when option is enabled (Default)
            if len(indexes) > 0:
                for i in indexes.flatten():
                    x, y, w, h = boxes[i]
                    label = str(self.classes[class_ids[i]])
                    confidence = str(round(confidences[i], 2))
                    color = self.colors[i]
                    cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(image, label + " " + confidence, (x, y + 20), self.font, 2, (255, 255, 255), 2)

        return image
