import json

import app.otherFunctions as otherFunctions

"""
arcvi_response:
    1. test if arcvi enters the data into the json file correctly
"""


def test_arcvi_response():
    test_path_to_image = "path_to_resource"
    test_result = "2"
    test_company = "GreenDay"

    result = otherFunctions.arcvi_response.generate_data(
        test_path_to_image,
        test_result,
        test_company)
    print(json.dumps(result))
    assert result["workParameters"]["value"]["images"][0]["path"] is \
           test_path_to_image
    assert result["workParameters"]["value"]["outcomes"][0]["name"] is \
           test_result
    assert test_company in result["id"]
