import pytest
import cv2 as cv
import VQC.app.utils as utils
from os.path import join

"""
test_aligner:
    1. check if returned image have same shape as template (very important)
    2. check behaviour when we have not enough matches to perform alignment
    3. Check whether warning is sent as we have small amount of matches
"""

data_path = join("tests", "test_unitMethods", "data")


def test_aligner():
    aligner = utils.Aligner()

    assert aligner.apply() is None

    aligner.template = cv.imread(join(data_path, "flower.png"))
    aligned = aligner.apply(
        cv.imread(join(data_path, "flower_s.png")))

    assert aligner.template.shape[:-1] == aligned.shape

    aligner.good_match_percent = 0
    with pytest.raises(SystemExit) as excinfo:
        aligner.apply(cv.imread(join(data_path, "flower_s.png")))

        assert "Not enough" in str(excinfo.value)

    aligner.good_match_percent = 1
    aligner.max_features = 8
    aligned = aligner.apply(
        cv.imread(join(data_path, "flower_s.png")))
    assert aligner.template.shape[:-1] == aligned.shape
