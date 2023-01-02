import pytest
import cv2 as cv
import numpy as np
import app.methods as methods
from os.path import join

"""
test_difference:
    1. testing whether shape of returned image match template
    2. check whether image is binaryzed inside function
    3. check outcomes using different parameters
    4. Check behaviour as we don't provide template or provide wrong path for
       saving
"""

data_path = join("tests", "test_unitMethods", "data")


@pytest.fixture(scope="module")
def get_template():
    template = cv.imread(join(data_path, "02.png"))
    yield template


@pytest.fixture(scope="module")
def get_tested():
    tested = cv.imread(join(data_path, "02_defected.png"))
    yield tested


def test_difference(get_template, get_tested):
    alg = methods.Difference(template=get_template)
    alg.er_size = (
        1  # this is not a real image, so we don't need complex morphology
    )
    alg.threshold = 100

    # Test with both morphologies
    result, img = alg.apply(get_template)
    assert img.shape == get_tested.shape[:-1]
    assert (np.unique(img) == np.array([0])).all()
    assert result == "Valid"

    # Test with boxes method
    alg.plot_boxes = True
    result, img = alg.apply(get_tested)
    assert result == "Defected"

    result, img = alg.apply(get_template)
    assert result == "Valid"

    alg.plot_boxes = False
    # test with only opening
    alg.opening = False
    result, img = alg.apply(get_tested)
    assert result == "Defected"

    # test with no morphology
    alg.closing = False
    result, img = alg.apply(get_tested)
    assert result == "Defected"

    # test with complex subtraction
    alg.method = "complex"
    result, img = alg.apply(get_tested)
    assert result == "Defected"

    # test with feeding grayscale image
    alg.template = cv.cvtColor(alg.template, cv.COLOR_BGR2GRAY)
    result, img = alg.apply(cv.cvtColor(get_tested, cv.COLOR_BGR2GRAY))
    assert result == "Defected"

    # Test if giving no template raises error
    with pytest.raises(SystemExit) as excinfo:
        alg.template = None
        alg.apply(get_tested)

    assert "template" in str(excinfo.value)
