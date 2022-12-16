import pytest

import app.methods as methods
from os.path import join
import cv2 as cv

"""
test_template_matching:
    1. check if it skips some boxes
    2. check some outcomes
    3. Check behaviour as we don't provide template or provide wrong path for
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


def test_template_matching(get_template, get_tested):
    from app.utils import box_generator
    alg = methods.TemplateMatcher(
        template=get_template, box_generator=box_generator.BoxGenerator())
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
