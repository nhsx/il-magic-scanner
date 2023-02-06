import cv2
import numpy as np
from pathlib import Path

from .graphics import pil_to_cv2

class Detection:
    def __init__(self, yolo_bbox_list, confidence):
        self.yolo_bbox_list = yolo_bbox_list
        self.confidence = confidence

    def norm_centre_x(self):
        return self.yolo_bbox_list[0]

    def norm_centre_y(self):
        return self.yolo_bbox_list[1]

    def norm_width(self):
        return self.yolo_bbox_list[2]

    def norm_height(self):
        return self.yolo_bbox_list[3]

    def norm_min_x(self):
        return self.norm_centre_x() - self.norm_width()/2

    def norm_min_y(self):
        return self.norm_centre_y() - self.norm_height()/2

    def norm_rect(self, width_compensation=1.1):
        # This width compensation is to allow for an annoyance in the training data:
        # I hadn't noticed that where the bounding box for the name had shifted off the
        # left edge of the image, the x_min value was being set to zero.  That means 
        # the model has learned that it's OK for the left edge of the bounding box to clip
        # straight down the middle of a character.  I'll go back and retrain with a fix
        # for that (get it to recognise a clip on the left edge as "no match", basically)
        # but until I can get round to that, this will help.  It adds a little noise to 
        # the nhs number in certain circumstances, but it'll do for now.
        return {
            'x': self.norm_min_x() - (self.norm_width()/2)*(width_compensation-1),
            'y': self.norm_min_y(),
            'width': self.norm_width()*width_compensation,
            'height': self.norm_height()
        }


class Inference:
    @classmethod
    def fake(cls, class_labels):
        return FakeInference(class_labels)


    def _abs_filename(self, filename):
        return str(Path(filename).absolute())

    def __init__(self, cfg_filename, weights_filename, input_dims, class_labels):
        cfg_filename = self._abs_filename(cfg_filename)
        weights_filename = self._abs_filename(weights_filename)
        self.model = cv2.dnn.readNetFromDarknet(cfg_filename, weights_filename)
        self.model.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.model.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        self.model_layer_names = self.model.getLayerNames()
        self.model_layer_names = [self.model_layer_names[i[0] - 1] for i in self.model.getUnconnectedOutLayers()]
        self.input_dims = input_dims
        self.class_labels = class_labels

    def infer(self, full_size_pil_image, confidence_threshold=0.2):
        pil_resized_for_yolo = full_size_pil_image.resize(self.input_dims)
        cv2_image = pil_to_cv2(pil_resized_for_yolo)
        self.model.setInput(cv2.dnn.blobFromImage(cv2_image, 1/255.0, size=self.input_dims, swapRB=True, crop=False))
    
        output = self.model.forward(self.model_layer_names)

        detections = {}
        for class_label in self.class_labels: detections[class_label] = []
        for out in output:
            for det_list in out:
                scores = det_list[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                class_label = self.class_labels[class_id]
                if confidence > confidence_threshold:
                    detections[class_label].append(Detection(det_list[:4], confidence))
        return detections


class FakeInference:
    """
    Something that quacks like Inference but doesn't do any work.  Just pretends
    it's got a single perfect match for each passed class, that's the entire image.
    """
    def __init__(self, class_labels):
        self.class_labels = class_labels

    def infer(self, ignored_image, confidence_threshold=0.2):
        detections = {}
        for class_label in self.class_labels:
            detections[class_label] = [Detection([0.5,0.5,1.0,1.0], 1.0)]
        return detections
