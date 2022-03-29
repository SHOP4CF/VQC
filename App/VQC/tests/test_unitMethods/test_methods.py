import pytest
import cv2 as cv
import numpy as np
import os
import shutil

import app.methods as methods


@pytest.fixture(scope="module")
def get_template():
    template = cv.imread("tests/test_unitMethods/data/02.png")
    yield template


@pytest.fixture(scope="module")
def get_tested():
    tested = cv.imread("tests/test_unitMethods/data/02_defected.png")
    yield tested


"""
Testing every method using some very small prepared images:
test_difference:
    1. testing whether shape of returned image match template
    2. check whether image is binaryzed inside function
    3. check outcomes using different parameters
    4. Check behaviour as we don't provide template or provide wrong path for saving

test_template_matching:
    1. check if it skips some boxes 
    2. check some outcomes 
    3. Check behaviour as we don't provide template or provide wrong path for saving

k_means:
"""


def test_difference(get_template, get_tested):
    alg = methods.Difference(template=get_template)
    alg.er_size = (
        1  # since this is not a real image then we don't need complex morphology
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


def test_template_matching(get_template, get_tested):
    from app.utils import box_generator
    alg = methods.TemplateMatcher(
        template=get_template, box_generator=box_generator.Box_generator())
    alg.template_size = 10

    # Check if we get enough amount of squares checked
    result, matches = alg.apply(get_tested)
    # assert len(matches) == np.prod(
    #     np.ceil(np.array(get_tested.shape) / alg.template_size)
    # )
    assert result == "Defected"

    # Now check if everyhing works as we give valid image
    result, matches = alg.apply(get_template)
    # assert len(matches) == np.prod(
    #     np.ceil(np.array(get_tested.shape) / alg.template_size)
    # )
    assert result == "Valid"

    # not giving template
    with pytest.raises(SystemExit) as excinfo:
        alg.template = None
        alg.apply(get_tested)

    assert "template" in str(excinfo.value)
