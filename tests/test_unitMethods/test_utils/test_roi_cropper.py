import cv2 as cv
import VQC.app.utils as utils
from os.path import join

"""
test_roi_cropper:
    1. try on different predefined images and check results
"""

data_path = join("tests", "test_unitMethods", "data")


def test_roi_cropper():
    cropper = utils.ROICropper()
    cropper.thresh_border = 1000
    to_crop = cv.imread(join(data_path, "to_crop.png"))
    cropped = cv.imread(join(data_path, "cropped.png"))
    cropped_well = cropper.apply(to_crop)

    assert (cropped == cropped_well).all()

    # testing for second method
    cropper.set_params(
        method="color",
        low_color="##008000",
        high_color="#ffffff",
        thresh_border=100
    )
    to_crop = cv.imread(join(data_path, "template_bcg.png"))
    cropped = cropper.apply(to_crop)

    assert cropped.shape == (29, 28, 3)

    cropper.method = 123
    assert cropper.apply(to_crop) is None
