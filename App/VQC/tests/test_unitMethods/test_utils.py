import pytest
import cv2 as cv
import os

import app.utils as utils

"""
test_aligner:
    1. check if returned image have same shape as template (very important)
    2. check behaviour when we have not enough matches to perform alignment
    3. Check whether warning is sent as we have small amount of matches

test_roi_cropper:
    1. try on different predefined images and check results

box_generator:
    1. check whether initialization and reading txt with boxes works
    3. give not existing template and check behaviour
    4. Check behaviour if there is no file with boxes -> file should be created
    5. check whether updating boxes works
"""


def test_aligner():
    aligner = utils.Aligner()

    assert aligner.apply() == None

    aligner.template = cv.imread("tests/test_unitMethods/data/flower.png")
    aligned = aligner.apply(
        cv.imread("tests/test_unitMethods/data/flower_s.png"))

    assert aligner.template.shape[:-1] == aligned.shape

    aligner.good_match_percent = 0
    with pytest.raises(SystemExit) as excinfo:
        aligner.apply(cv.imread("tests/test_unitMethods/data/flower_s.png"))

    assert "Not enough" in str(excinfo.value)

    aligner.good_match_percent = 1
    aligner.max_features = 8
    aligned = aligner.apply(
        cv.imread("tests/test_unitMethods/data/flower_s.png"))
    assert aligner.template.shape[:-1] == aligned.shape


def test_roi_cropper():
    cropper = utils.ROI_cropper()
    cropper.thresh_border = 1000
    to_crop = cv.imread("tests/test_unitMethods/data/to_crop.png")
    cropped = cv.imread("tests/test_unitMethods/data/cropped.png")
    cropped_well = cropper.apply(to_crop)

    assert (cropped == cropped_well).all()

    # testing for second method
    cropper.set_params(
        method="color", low_color="##008000", high_color="#ffffff", thresh_border=100
    )
    to_crop = cv.imread("tests/test_unitMethods/data/template_bcg.png")
    cropped = cropper.apply(to_crop)

    assert cropped.shape == (29, 28, 3)

    cropper.method = 123
    assert cropper.apply(to_crop) is None


def test_box_generator():
    generator = utils.Box_generator()
    generator.set_params(path="tests/test_unitMethods/data/boxes.txt")
    assert generator.get("10")[0] == (20, 30, 40, 50)

    assert len(generator.get("1")) == 3

    assert generator.get("1123") == None

    generator = utils.Box_generator(
        path="tests/test_unitMethods/data/NotExistingBoxes.txt"
    )
    assert list(generator.boxes_dict.keys()) == []

    template_path = "tests/test_unitMethods/data/01.JPG"

    generator.update_boxes(template_path)
    assert len(generator.get("tests/test_unitMethods/data/01.JPG")) == 3

    os.remove("tests/test_unitMethods/data/NotExistingBoxes.txt")

    with pytest.raises(SystemExit) as excinfo:
        generator = utils.Box_generator(
            path="tests/test_unitMethods/data/boxes_invalid1.txt"
        )

    assert "file containing predefined boxes" in str(excinfo.value)
