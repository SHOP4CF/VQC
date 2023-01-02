import pytest
import os

import app.utils as utils

"""
box_generator:
    1. check whether initialization and reading txt with boxes works
    3. give not existing template and check behaviour
    4. Check behaviour if there is no file with boxes -> file should be created
    5. check whether updating boxes works
"""

data_path = os.path.join("tests", "test_unitMethods", "data")


def test_box_generator():
    generator = utils.BoxGenerator()
    generator.set_params(path=os.path.join(data_path, "boxes.txt"))
    assert generator.get("10")[0] == (20, 30, 40, 50)

    assert len(generator.get("1")) == 3

    assert generator.get("1123") is None

    generator = utils.BoxGenerator(
        path=os.path.join(data_path, "NotExistingBoxes.txt")
    )
    assert list(generator.boxes_dict.keys()) == []

    template_path = os.path.join(data_path, "01.jpg")

    generator.update_boxes(template_path)
    assert len(generator.get(os.path.join(data_path, "01.jpg"))) == 3

    os.remove(os.path.join(data_path, "NotExistingBoxes.txt"))

    with pytest.raises(SystemExit) as excinfo:
        generator = utils.BoxGenerator(
            path=os.path.join(data_path, "boxes_invalid1.txt")
        )

        assert "file containing predefined boxes" in str(excinfo.value)
