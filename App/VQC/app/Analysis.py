import logging
import os
import cv2 as cv

from app import db  # only this class has acess to the db
from app.otherFunctions import enums, readConfig, debug_help

import app.methods as methods
import app.utils as utils


logger = logging.getLogger("app")

config_path = "configuration/configuration.yaml"


class Analysis:
    """
    This class sets up all methods and run them when called.
    """

    def __init__(self, config):
        """
        Args:
            config_path (string): path for methods and utils configuration file
        """
        self.config = config
        self.path = self.config["interface"]["path_for_outcomes"]
        if not os.path.isdir(self.path):
            os.mkdir(self.path)
            logger.warning(
                "App.Analysis: Provided path for saving inference had not existed, we created it as: {self.path} make sure that you want to save results there"
            )

        self.save_all = self.config["interface"]["save_all"]
        """
        Just sanity check if we have our db connected if yes we initialize our box generator.
        For some reasone someone may want to not use boxes, one can add it to config easily.
        """

        """box_generator is an util used only in template matching it potentially can improve its efficiency and accuracy"""
        box_generator_config = self.config["utils"]["box_generator"]
        box_generator = utils.Box_generator(
            **box_generator_config
        )  # during init we will read all previously saved boxes, and during template matching we will try to collect more boxes

        """Setting our methods and aligner"""
        methods_config = self.config["methods"]
        self.methods = {
            "difference": methods.Difference(**methods_config["difference"]),
            "template_matching": methods.TemplateMatcher(
                **methods_config["template_matching"], box_generator=box_generator
            ),
        }

        # In this dict we will store templates for later usage not to load them constantly
        self.templates_dict = {}

        aligner_config = self.config["utils"]["aligner"]
        self.Aligner = utils.Aligner(**aligner_config)

        # initialize the cropper
        cropper_config = self.config["utils"]["roi_cropper"]
        self.ROI_cropper = utils.ROI_cropper(**cropper_config)

    def set_config(self, config_path):
        """At first we again read our configs and then run set_params method in our components passing appropriate configs"""
        self.config = readConfig.read_config(
            config_path
        )  # At first we use our validator to check whether everything is okay
        methods_config = self.config["methods"]
        for name, method in self.methods.items():
            method.set_params(**methods_config[name])

        aligner_config = self.config["utils"]["aligner"]
        self.Aligner.set_params(**aligner_config)

        cropper_config = self.config["utils"]["roi_cropper"]
        self.ROI_cropper.set_params(**cropper_config)

    def get_method(self):
        return self.config["interface"]["method"]

    def analyse(self, template_path, pcb_path):
        """
        Whole inspection:
        Get template and inspected image from given paths, if files do not exists raise an exception and log message
        -> apply histogram equalization if it is defined in config
        -> apply aligner (obligatory), may also apply roi_cropper if needed
        -> run chosen method and return result
        Args:
            template_path (str): Path from which we read template image
            pcb_path (str): Patr from which we read image to be inspected
            template_id (int): id of currently checked PCB
        Return:
            result (currently str but may be int or whatever): Decion - defected or not
        """
        to_inspect_img = cv.imread(pcb_path, cv.IMREAD_GRAYSCALE)
        template_img = cv.imread(template_path, cv.IMREAD_GRAYSCALE)

        """
        Now I assume that if I see template for the first time I'll save the image in the dictonary so that
        when I see the same path again I'll just take it from the dictonary
        """
        if template_path in self.templates_dict:
            template_img = self.templates_dict[template_path]
        else:
            template_img = cv.imread(template_path, cv.IMREAD_GRAYSCALE)
            self.templates_dict[template_path] = template_img

        if to_inspect_img is None or template_img is None:
            msg = f'App.Analysis: Wrong path to: {"template:" + template_path if template_img is None else "image to be inspected: " +  pcb_path}, as imread returns None'
            debug_help.log_fiware_resp_exception(
                logger,
                msg,
                level="error",
                send_fiware=True,
                fiware_status=enums.Status.Error,
                raise_exception=True,
            )

        """
            Pipeline starts here. We perform cropping at first if set in config -> Alignement is performed always -> Histogram equalization if set -> 
            We check whether pipeline was succesfull (Basically the only thing that may go wrong is that sizes may not be equal if alignement is deleted from here)
        """
        if self.config["interface"]["using_cropped"]:
            to_inspect_img = self.ROI_cropper.apply(to_inspect_img)

        self.Aligner.template = template_img
        to_inspect_img = self.Aligner.apply(to_inspect_img, template_path)

        if self.config["interface"]["histogram_eq"]:
            to_inspect_img = cv.equalizeHist(to_inspect_img)
            template = cv.equalizeHist(template_img)

        if template.shape != to_inspect_img.shape:
            msg = """App.Analysis: Shapes of images does not match, Check if you have Aligner in your pipeline!"""
            debug_help.log_fiware_resp_exception(
                logger,
                msg,
                level="error",
                send_fiware=True,
                fiware_status=enums.Status.Error,
                raise_exception=True,
            )

        method = self.config["interface"]["method"]
        self.methods[method].template = template

        result, result_img = self.methods[method].apply(
            to_inspect_img, template_path)
        # ! pcb_path may be an absolute path, Ill take only the filename
        suffixs = pcb_path.split("/")[-1][:-4]
        path_to_visualization = f"{self.path}/{suffixs}_inspected.png"

        if self.save_all:
            cv.imwrite(
                path_to_visualization,
                result_img,
            )

        elif result == "Defected":
            cv.imwrite(
                path_to_visualization,
                result_img,
            )

        return result, path_to_visualization


analysis = None
