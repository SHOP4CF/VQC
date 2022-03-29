import numpy as np
import cv2 as cv
import random
import os
import logging

from app.methods import Method

logger = logging.getLogger("app")


class Difference(Method):
    """
    Class being able to perform difference method to find defects
    """

    def __init__(
        self,
        template=None,
        er_shape=1,
        er_size=4,
        kernel_size=21,
        closing=True,
        closing_size=3,
        opening=True,
        opening_size=5,
        method="simple",
        simple_method_thresh=50,
        threshold=10000,
        path="../imgs/outcome",
        plot_boxes=False,
        area_threshold=500,
        shift=10,
        bbox_color=[255, 0, 0]
    ):
        """
        Args
            template (np.ndarray with shape (H,W,C), C=3 or 1): valid PCB that will be used to compare one that may be defected
            er_shape (int): RECT - 0, CROSS - 1, ELLIPSE - 2, shape of the kernel that will be convolved
            er_size (int): size of the kernel that will be convolved
            kernel_size (int): Kernel size to perform binaryzation, it's used in adaptiveThresholding to calculate some local threshold
            for binaryzation
            closing, opening (bool): whether to apply additional morphology operators after erosion
            opening_size, closing_size(int): size of the kernel that will be convolved during opening and closing operations
            simple_method_thresh (int): thresholding value for binaryzatin for simple method
            method (string): complex - using binaryzation, simple - just bitwiseXor
            threshold (int): what is the threshold to classify probe as defected
            path (string): where to save inference outcomes
            plot_boxes (string): Whether to return binary mask or to plot boxes indicating missing elements
            area_threshold (ing): Threshold from which we will consider box being a defect
            shift (int): Padding of plotted boxes
            bbox_color(list): color of the bounding boxes in RGB format
        """
        self.template = template
        self.er_shape = er_shape
        self.er_size = er_size
        self.kernel_size = kernel_size
        self.closing = closing
        self.closing_size = closing_size
        self.opening = opening
        self.opening_size = opening_size
        self.method = method
        self.simple_method_thresh = simple_method_thresh
        self.threshold = threshold
        self.path = path
        self.plot_boxes = plot_boxes
        self.area_threshold = area_threshold
        self.shift = shift
        self.bbox_color = bbox_color

    def set_params(
        self,
        er_shape=1,
        er_size=2,
        kernel_size=21,
        closing=True,
        closing_size=3,
        opening=True,
        opening_size=5,
        method="simple",
        simple_method_thresh=50,
        threshold=10000,
        plot_boxes=False,
        area_threshold=400,
        shift=10,
        bbox_color=[255, 0, 0]
    ):
        self.er_shape = er_shape
        self.er_size = er_size
        self.kernel_size = kernel_size
        self.method = method
        self.closing = closing
        self.closing_size = closing_size
        self.opening = opening
        self.opening_size = opening_size
        self.method = method
        self.simple_method_thresh = simple_method_thresh
        self.threshold = threshold
        self.plot_boxes = plot_boxes
        self.area_threshold = area_threshold
        self.shift = shift
        self.bbox_color = bbox_color

    # Here I added template_id as it was needed also in template_matching, maybe we could use it while saving files
    def apply(self, to_be_inspected, template_id=""):
        """
        Function that will difference and plot outcomes. It performs as follows:

        Check some expections (wrong path to save files or not defined template) -> make sure that images are
        in grayscale if not convert them -> based on method chosen it will:
        if complex: at first perform adaptiveThreshold binaryzation (it may in some extent remove influance on ilumination) then bitwiseXor
        if simple: at first it will do bitwiseXor and then some very simple thresholding.
        -> Perform morphological operations which are very important, kernel size should be selected with care and also closing and opening too.
        -> calculates sum of binaryzed and eroded image to classify it either as defected or not
        -> if image is defected save it for inference and eventually return message

        Args:
            to_be_inspected (np.ndarray with shape (H,W,C) C=3): image to be compared with a template
            template_id (int): id of the currently checked template
        Returns:
        answer about being defected or not
        img (np.ndarray with shape (H,W,C)): image after analysis
        """

        """Basically such error should never happen as before using any method we check it in Analysis.py but if someone would like to use only this method as a block
            it is needed
        """
        if self.template is None or to_be_inspected is None:
            logger.error(
                "Provide template and image to be inspected to method!")
            raise SystemExit(
                "App.methods.Difference: Method Difference couldn't find template and/or image to be inspected"
            )

        # We always want images in grayscale so if they're not already convert them
        template = (
            cv.cvtColor(self.template, cv.COLOR_BGR2GRAY)
            if len(self.template.shape) == 3
            else self.template
        )

        to_be_inspected = (
            cv.cvtColor(to_be_inspected, cv.COLOR_BGR2GRAY)
            if len(to_be_inspected.shape) == 3
            else to_be_inspected
        )

        # We support two methods 0 is more complex in case of time consumption
        if self.method == "complex":
            template = cv.adaptiveThreshold(
                template,
                255,  # maxValue: Non-zero value assigned to the pixels for which the condition is satisfied
                cv.ADAPTIVE_THRESH_GAUSSIAN_C,  # Adaptive thresholding algorithm to use
                cv.THRESH_BINARY,  # Thresholding type that must be either THRESH_BINARY or THRESH_BINARY_INV
                self.kernel_size,  # Size of a pixel neighborhood that is used to calculate a threshold value for the pixel: 3, 5, 7, and so on
                1,  # Constant subtracted from the mean or weighted mean
            )  # The bigger kernel the better binaryzation is from experiments
            to_be_inspected = cv.adaptiveThreshold(
                to_be_inspected,
                255,  # maxValue: Non-zero value assigned to the pixels for which the condition is satisfied
                cv.ADAPTIVE_THRESH_GAUSSIAN_C,  # Adaptive thresholding algorithm to use
                cv.THRESH_BINARY,  # Thresholding type that must be either THRESH_BINARY or THRESH_BINARY_INV
                self.kernel_size,  # Size of a pixel neighborhood that is used to calculate a threshold value for the pixel: 3, 5, 7, and so on
                1,  # Constant subtracted from the mean or weighted mean
            )
            bitwiseXor = cv.bitwise_xor(template, to_be_inspected)

        elif self.method == "simple":
            bitwiseXor = cv.bitwise_xor(template, to_be_inspected)
            bitwiseXor[bitwiseXor >= self.simple_method_thresh] = 255
            bitwiseXor[bitwiseXor < self.simple_method_thresh] = 0

        # anchor: position within the element
        # The default value [−1,−1] means that the anchor is at the center
        element = cv.getStructuringElement(
            self.er_shape, ksize=(self.er_size, self.er_size), anchor=(-1, -1)
        )

        # We perform some morphological operations to clean our result_img from noise
        result_img = cv.erode(bitwiseXor, element)  # First perform erosion
        if self.opening:
            result_img = cv.morphologyEx(
                result_img,
                cv.MORPH_OPEN,
                np.ones((self.opening_size, self.opening_size), np.uint8),
            )
        if self.closing:
            result_img = cv.morphologyEx(
                result_img,
                cv.MORPH_CLOSE,
                np.ones((self.closing_size, self.closing_size), np.uint8),
            )

        return self.decide(result_img, to_be_inspected)

    def decide(self, result_img, to_be_inspected):
        # We either check summing mask or generating boxes and checking their area
        if self.plot_boxes:
            contours, hierarchy = cv.findContours(
                result_img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE
            )  # It may be possible to use hierarchy later is we would like to place a few small objects that are close together inside one rectangle

            boxes = []
            for c in contours:
                x, y, w, h = cv.boundingRect(c)
                area = w * h
                # If there are some noisy very small contours we neglect them
                if area > self.area_threshold:
                    boxes.append(
                        (
                            x - self.shift,
                            y - self.shift,
                            w + 2 * self.shift,
                            h + 2 * self.shift,
                        )
                    )

            if len(boxes) > 0:
                to_be_inspected = cv.cvtColor(to_be_inspected, cv.COLOR_GRAY2BGR) if len(
                    to_be_inspected.shape) == 1 else to_be_inspected
                for box in boxes:
                    x, y, w, h = box
                    cv.rectangle(
                        to_be_inspected, (x, y), (x + w, y +
                                                  h), tuple(self.bbox_color), 3
                    )
                return (
                    "Defected",
                    to_be_inspected,
                )  # We return this as we plotted boxes here
            else:
                return "Valid", result_img
        else:
            # Based on sum of the pixels we decide defected or not if yes then we save inference to the file
            sum_ = np.sum(result_img)
            if sum_ > self.threshold:
                return "Defected", result_img
            else:
                return "Valid", result_img
