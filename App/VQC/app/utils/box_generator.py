import cv2 as cv
import os
from app.utils import Util
from app.otherFunctions import debug_help, enums
from app.methods.difference import Difference
import logging

logger = logging.getLogger("app")


class Box_generator(Util):
    """
    Class that is responsible for defining boxes that will be checked by template_matching method. It's purpose is to make template matching faster and more robust
    If we don't have to scan entire photo we progress faster, and with higher accuracy as we only compare exposed parts
    """

    def __init__(
        self,
        er_shape=0,
        er_size=1,
        closing=True,
        opening=True,
        method="simple",
        shift=5,
        low_area_thresh=200,
        path="configuration/boxes.txt",
    ):
        """
        Args:
        er_shape (int): RECT - 0, CROSS - 1, ELLIPSE - 2, shape of the kernel that will be convolved
        er_size (int): size of the kernel that will be convolved
        closing, opening (bool): whether to apply additional morphology operators after erosion
        method (int): 0 - more complex method using binaryzation, 1 - simple subtraction
        shift (int): by what amount we want extend our bounding box, I don't use it but may be usefull for very small objects
        low_area_thresh (int): as in resulting image we possibly may have some noise for which contour may be created we can filter
        them based on the area
        path (string): This is just the path for file containing all defined boxes

        """
        self.diff_config = {
            "er_shape": er_shape,
            "er_size": er_size,
            "closing": closing,
            "opening": opening,
            "method": method,
        }

        self.shift = shift
        self.low_area_thresh = low_area_thresh
        self.path = path

        """In case there is no file with boxes create it."""
        if not os.path.isfile(self.path):
            with open(self.path, "w") as f:
                pass

        self.boxes_dict = {}

        self.read_boxes()
        # During initialization we read all previously created boxes. It would be easier if we could store them in db
        # as reading would not be needed only updating

    def set_params(
        self,
        er_shape=0,
        er_size=1,
        closing=True,
        opening=True,
        method="simple",
        shift=5,
        low_area_thresh=200,
        path="boxes.txt",
    ):
        self.diff_config = {
            "er_shape": er_shape,
            "er_size": er_size,
            "closing": closing,
            "opening": opening,
            "method": method,
        }
        self.shift = shift
        self.low_area_thresh = low_area_thresh
        self.path = path
        self.read_boxes(init=False)

    # Here we update our txt but again it would be easier to use db for this if possible
    def read_boxes(self, init=True):
        """Function opens txt file with boxes read them all and saves in dictonary for later usage

        Args:
            init (bool, optional): [We read boxes either during initialization of this class or during updating configs. During init we are sure that
            ours dictonary is empty but during updating config we may duplicate some boxes so we always check it before appending]. Defaults to True.
        """
        with open(self.path, "r") as f:
            for line in f.readlines():
                try:
                    template, *coordinates = line.split(" ")
                    x, y, w, h = [int(x) for x in coordinates]
                except ValueError:
                    msg = f"app.utils.box_generator.read_boxes: Something is wrong with the {self.path} file containing predefined boxes each line should have following structure: template_id x y w h but current line is {line}"
                    debug_help.log_fiware_resp_exception(
                        logger,
                        msg,
                        level="error",
                        send_fiware=True,
                        fiware_status=enums.Status.Error,
                        raise_exception=True,
                    )

                if template not in self.boxes_dict:
                    self.boxes_dict[template] = []

                if init:
                    self.boxes_dict[template].append((x, y, w, h))
                else:
                    if (x, y, w, h) not in self.boxes_dict[template]:
                        self.boxes_dict[template].append((x, y, w, h))

    def update_boxes(self, template_path):
        """
        This method is used to update boxes for given template
        Args:
            templates (array of dicts): all templates from db
        """
        # If there is no anti template then we can't do anything
        if os.path.isfile(template_path[:-4] + "anti.jpg"):
            with open(self.path, "a") as f:
                if template_path not in self.boxes_dict:
                    t = cv.equalizeHist(
                        cv.imread(template_path,
                                  cv.IMREAD_GRAYSCALE)
                    )
                    anti_t = cv.equalizeHist(
                        cv.imread(
                            template_path[:-4] + "anti.jpg",
                            cv.IMREAD_GRAYSCALE,
                        )
                    )
                    boxes = self.apply(t, anti_t)

                    self.boxes_dict[template_path] = boxes

                    for box in boxes:
                        x, y, w, h = box
                        f.write(f"{template_path} {x} {y} {w} {h}\n")

    def get(self, template_path):
        # This function just returns boxes
        """
        Args:
            template_path (string): template of which we want boxes

        Returns:
            self.boxes_dict[template_path] (array of tuples) where every element is tuple (x,y,w,h)
            or None when there is no such template in our boxes_dict.
        Unfortunately to generate new boxes array on the fly when template_matching requires new and it is not here we would
        need a db object inside that class I don't know if it should be given to it. But such thing happen only as we add new template
        during work of our server.
        """
        if template_path in self.boxes_dict:
            return self.boxes_dict[template_path]
        else:
            self.update_boxes(template_path)
            if template_path in self.boxes_dict:
                return self.boxes_dict[template_path]
            else:
                return None

    def apply(self, temp, anti_temp):
        """
        Here we apply difference method based on its result we calculate contours and based on them we prepare bounding boxes
        all functions are implemented in opencv

        Args:
            temp (np.ndarray with shape (H,W,C)): image with all components on
            anti_temp (np.ndarray with shape (H,W,C)): image with no components on

        Returns:
            boxes (array of tuples): array of all tuples, where x and y are top left corners of the box and w, h are widht and height
        """
        diff_method = Difference(template=temp, **self.diff_config)
        diff_img = diff_method.apply(anti_temp)[
            1
        ]  # index 0 is decision index 1 is image

        contours, hierarchy = cv.findContours(
            diff_img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE
        )  # It may be possible to use hierarchy later is we would like to place a few small objects that are close together inside one rectangle

        boxes = []
        for c in contours:
            x, y, w, h = cv.boundingRect(c)
            area = w * h
            if (
                area > self.low_area_thresh
            ):  # If there are some noisy very small contours we neglect them
                boxes.append(
                    (
                        x - self.shift,
                        y - self.shift,
                        w + 2 * self.shift,
                        h + 2 * self.shift,
                    )
                )

        return boxes
