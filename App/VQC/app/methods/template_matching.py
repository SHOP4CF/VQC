import numpy as np
import cv2 as cv
from app.methods import Method
import random
import os
import logging


logger = logging.getLogger("app")


class TemplateMatcher(Method):
    """
    Class being able to perform Template matching method to find defects
    """

    def __init__(
        self,
        template=None,
        matching_method=3,
        template_size=150,
        min_difference=0.999,
        box_generator=None,
        bbox_color=[255, 0, 0]
    ):
        """
        Args
            template (np.ndarray with shape (H,W,C), C=3): valid PCB that will be used to compare one that may be defected
            size (tuple): size of the plot with outcomes
            matching_method (int): method from open cv library that will be used to perform matching
            template_size (int): size of the window that will be convolved
            min_difference (float): minimal score (similarity) when current window will be considered as defected
            box_generator (Box_generator class): object that will be returning defined boxes with rectangles to be checked
            if this object is none Template matching will perform sliding windows method
            path (string): where to save inference outcomes
        """
        self.template = template
        self.matching_method = matching_method
        self.template_size = template_size
        self.min_difference = min_difference
        self.box_generator = box_generator
        self.bbox_color = bbox_color

    def set_params(
        self,
        matching_method=3,
        template_size=150,
        min_difference=0.99,
        bbox_color=[255, 0, 0]
    ):
        self.matching_method = matching_method
        self.template_size = template_size
        self.min_difference = min_difference
        self.bbox_color = bbox_color

    def apply(self, to_be_inspected, template_id=""):
        """
        Function that peform matching. It performs as follows:

        Check some expections (wrong path to save files or not defined template) -> get boxes for box_generator if it is not None
        -> make sure that images are in grayscale if not convert them -> create some local variables needed for analysis
        -> it creates txt file in which it will save coordinates of boxes (probably will be removed) -> based on existance of predefined boxes:
        If exist: perform template_matching for all defined boxes
        If not exist: log warning that boxes could not be found and peform template matching using sliding window
        -> if some defected parts were found (boxes_to_plot) then draw rectangles on image and then save that image for inference
        and return message whether probe was defected or not

        Args:
            to_be_inspected (np.ndarray with shape (H,W,C) C=3): image to be compared with a template
            template_id (int): id of the template to be analysed needed to get appropriate boxes
        Returns:
            answer about being defected or not
            to_be_inspected (np.ndarray with shape (H,W,C)): image after inference
        """
        if self.template is None or to_be_inspected is None:
            logger.error(
                "Provide template and image to be inspected to method!")
            raise SystemExit(
                "App.methods.template_matching: couldn't find template and/or image to be inspected"
            )

        # Getting boxes from generator
        boxes = self.box_generator.get(template_id)

        # We always want images in grayscale so if they're not already convert them
        self.template = (
            cv.cvtColor(self.template, cv.COLOR_BGR2GRAY)
            if len(self.template.shape) == 3
            else self.template
        )
        to_be_inspected = (
            cv.cvtColor(to_be_inspected, cv.COLOR_BGR2GRAY)
            if len(to_be_inspected.shape) == 3
            else to_be_inspected
        )
        # This array will contain all performed matchings and their scores, may be usefull
        matching = []

        defects = 0  # to count how many defect we have
        boxes_to_plot = []  # To store boxes to be plotted after inspection
        """Template matching will be working even if the anti template is not defined but warining will be logged.
        For now we we save either boxes in txt format and image
        """
        # We open file to save inference to txt files probably will be deleted

        if boxes:
            for box in boxes:
                defects += self.match_templates(
                    to_be_inspected, box, matching, boxes_to_plot
                )  # This function returns either 0 or 1 and based on that
                # we sum our defects
        else:
            logger.warning(
                "App.methods.template_matching: Couldn't find predefined boxes will be performing template matching on constant windows it may result in worse results!"
            )
            for y in range(
                0, self.template.shape[0], self.template_size
            ):  # get every possible square
                for x in range(0, self.template.shape[1], self.template_size):
                    defects += self.match_templates(
                        to_be_inspected,
                        [x, y, self.template_size, self.template_size],
                        matching,
                        boxes_to_plot,
                    )

        for box in boxes_to_plot:
            to_be_inspected = cv.cvtColor(
                to_be_inspected, cv.COLOR_GRAY2BGR) if len(to_be_inspected.shape) == 1 else to_be_inspected

            x, y, w, h, sim = box
            cv.rectangle(to_be_inspected, (x, y),
                         (x + w, y + h), self.bbox_color, 3)
            cv.putText(
                to_be_inspected,
                str(np.round(sim, 2)),  # Text string to be drawn.
                (x + w // 4, y + h // 2),  # Bottom-left corner.
                cv.FONT_HERSHEY_SIMPLEX,  # Font type, see HersheyFonts.
                # Font scale factor that is multiplied by the font-specific base size.
                2,
                self.bbox_color,  # Text color.
                2,  # Thickness of the lines used to draw a text.
                cv.LINE_AA,  # Line type.
            )

        if defects > 0:
            return "Defected", to_be_inspected
        else:
            return "Valid", to_be_inspected

    def match_templates(self, to_be_inspected, box, matching, boxes):
        """
        This is just helper function for more readability it just crops two segments perform template matching and based on similarity
        it either returns 1 -> defected part or 0 -> okay part
        """
        x, y, w, h = box

        temp = self.template[
            y: y + h + 1, x: x + w + 1
        ]  # first coordinate is y (height) axis second is x (width) axis
        deff = to_be_inspected[y: y + h + 1, x: x + w + 1]  # crop image
        match = cv.matchTemplate(
            deff, temp, self.matching_method
        )  # check how similar they're

        # As ersults are saved in nested 2dimensional array
        match = match[0][0]
        matching.append(match)

        # Save rectangles coordinates in file
        if match < self.min_difference:
            boxes.append((x, y, w, h, match))
            return 1
        else:
            return 0
