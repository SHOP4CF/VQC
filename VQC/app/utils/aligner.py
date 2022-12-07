import logging
import cv2 as cv
import numpy as np

from VQC.app.utils import Util
from VQC.app.otherFunctions import debug_help, enums

logger = logging.getLogger("app")


class Aligner(Util):
    """
            Class being able to perfectly warp image that we want to check to
            the template image
    """

    def __init__(self,
                 template: np.ndarray = None,
                 max_features: int = 500,
                 good_match_percent: float = 0.15
                 ) -> None:
        """
            Args:
                 template (np.ndarray with shape (H,W,C), C=3 or 1): valid PCB
                    that will be used to compare one that may be defected

                 max_features, good_match_percent (int), (float): attributes
                    needed for feature extractor max_feature is maximal amount
                    of features

                 that extractor will get, good_match_percent is how many of
                    those found we want to keep, some key points may be poor,
                    and we should reject them.
        """
        self.template = template
        self.max_features = max_features
        self.good_match_percent = good_match_percent
        self.keypoints_dict: dict = (
            {}
        )
        # inside this dictionary we store key points not to calculate them
        # more than once for a template

    def set_params(self,
                   max_features: int = 500,
                   good_match_percent: float = 0.15
                   ) -> None:
        self.max_features = max_features
        self.good_match_percent = good_match_percent

    def apply(self, img: np.ndarray = None, template_id: int = 1):
        """
            Function performing alignment: given template we try to align img
            to it.

            Args:
                img (np.ndarray with shape (H,W,C), C=3 or 1): image to be
                    warped

                template_id (int): id of current template, needed to get
                    key points stored in dict
            Returns:
                aligned (np.ndarray with shape same as given template):
                    aligned images

        """
        if self.template is not None and img is not None:
            # Some papers claim that after using some kind of blurring
            # (Gaussian) the alignment outcomes was better.

            # We must have greyscale images
            to_align = (
                cv.cvtColor(img, cv.COLOR_BGR2GRAY) if len(
                    img.shape) == 3 else img
            )
            template_gray = (
                cv.cvtColor(self.template, cv.COLOR_BGR2GRAY)
                if len(self.template.shape) == 3
                else self.template
            )

            # Detect features and compute descriptors.
            orb = cv.ORB_create(self.max_features)
            keypoints1, descriptors1 = orb.detectAndCompute(to_align, None)

            if template_id in self.keypoints_dict:
                keypoints2, descriptors2 = self.keypoints_dict[template_id]
            else:
                keypoints2, descriptors2 = orb.detectAndCompute(
                    template_gray, None)
                self.keypoints_dict[template_id] = (keypoints2, descriptors2)

            # Match features
            matcher = cv.DescriptorMatcher_create(
                cv.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING
            )
            matches = matcher.match(descriptors1, descriptors2, None)

            # Sort matches by score
            list(matches).sort(key=lambda x: x.distance, reverse=False)

            # remove bad matches and log is something is wrong
            num_good_matches = int(len(matches) * self.good_match_percent)
            if num_good_matches < 4:
                msg = "App.Utils.Aligner: Not enough keypoints to perform " \
                      "alignment! either change max_feature or " \
                      "good_match_percent parameter! "
                debug_help.log_fiware_resp_exception(
                    logger,
                    msg,
                    level="error",
                    send_fiware=True,
                    fiware_status=enums.Status.Error,
                    raise_exception=True,
                )

            elif num_good_matches < 10:
                logger.warning(
                    f"App.Utils.Aligner --> Found only {num_good_matches}"
                    f" good matches in aligner performance may be poor "
                    f"consider changing configuration!"
                )

            matches = matches[:num_good_matches]

            # Extract location of good matches
            points1 = np.zeros((len(matches), 2), dtype=np.float32)
            points2 = np.zeros((len(matches), 2), dtype=np.float32)

            for i, match in enumerate(matches):
                points1[i, :] = keypoints1[match.queryIdx].pt
                points2[i, :] = keypoints2[match.trainIdx].pt

            # find homography matrix
            h, _ = cv.findHomography(points1, points2, cv.RANSAC)

            # use homography
            height, width = self.template.shape[0], self.template.shape[1]
            aligned = cv.warpPerspective(to_align, h, (width, height))

            return aligned
        else:
            logger.error(
                "App.Utils.Aligner: Before applying warping you need to pass "
                "template and pass img to apply function. "
            )
            return None
