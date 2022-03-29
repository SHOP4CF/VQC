import pytest
import json
import os

"""With this test we test pipeline with few scenarios:
   1. Upload new config -> send post at /inspect/ with pcb data -> get outcomes from /inspect/ -> jest wheter inspections went well
   2. Same as first but for different config
   3. sending wrong config path
   4. sending query with path to no existing image we expect exception
   5. sending query with not existing template we expect exception 
   6. sending query with fron json data we again expect exception
"""


def test_pipeline_no_db(client):
    from app import Analysis

    assert Analysis.analysis.methods["template_matching"].box_generator
    assert len(
        Analysis.analysis.methods["template_matching"].box_generator.get("../imgs/template/01.jpg")) == 3

    pcb = """{
        "data": [
            {"pcb_path": "../imgs/control/01_01.jpg",
              "value": "../imgs/template/01.jpg"
             }]
    }"""

    resp = client.post("/config/", data="tests/test_integration/config.yaml")
    assert resp.status_code == 200

    resp = client.post(
        "/inspect/", data=pcb, buffered=True
    )  # This buffered attribute is very important so that everything works as normal server is running
    assert resp.status_code == 200

    outcomes = client.get("/inspect/").data.decode("utf-8").replace("'", "")
    outcomes = json.loads(outcomes)[0]
    assert outcomes["result"] == "Defected"
    assert outcomes["fiware_response"] == 204
    assert outcomes["method"] == "difference"

    # Testing other configuration
    resp = client.post("/config/", data="tests/test_integration/config1.yaml")
    assert resp.status_code == 200
    resp = client.post(
        "/inspect/", data=pcb, buffered=True
    )  # This buffered attribute is very important so that everything works as normal server is running
    assert resp.status_code == 200

    outcomes = client.get("/inspect/").data.decode("utf-8").replace("'", "")
    outcomes = json.loads(outcomes)[0]
    assert outcomes["result"] == "Defected"
    assert True == os.path.isdir(Analysis.analysis.path)
    assert outcomes["fiware_response"] == 204
    assert outcomes["method"] == "template_matching"

    # sending bad config path
    resp = client.post("/config/", data="tests/integration/asdgasfdg")
    assert resp.status_code == 400

    # Error in Aligner
    Analysis.analysis.Aligner.good_match_percent = 0
    with pytest.raises(SystemExit) as excinfo:
        resp = client.post("/inspect/", data=pcb, buffered=True)

    assert "Not enough keypoints to perform alignement!" in str(excinfo.value)

    # Somehow sizes doesn't match
    pcb = """{
        "data": [
            {"pcb_path":  "../imgs/control/04_05.jpg",
              "value": "../imgs/template/01.jpg"
             }]
    }"""

    Analysis.analysis.Aligner.apply = lambda x, y: x
    with pytest.raises(SystemExit) as excinfo:
        resp = client.post("/inspect/", data=pcb, buffered=True)

    assert "Shapes of images does not match" in str(excinfo.value)

    # Sending wrong path to img to be inspected
    pcb = """{
        "data": [
            {"pcb_path": "../imgs/control/NotExisting.jpg",
              "value": "../imgs/template/01.jpg"
             }]
    }"""

    with pytest.raises(SystemExit) as excinfo:
        resp = client.post("/inspect/", data=pcb, buffered=True)

    assert "imread returns None" in str(excinfo.value)
    # Sending not existing template
    pcb = """{
        "data": [
            {"pcb_path":  "../imgs/control/01_01.jpg",
               "value": "asasdasd"
             }]
    }"""

    with pytest.raises(SystemExit) as excinfo:
        resp = client.post("/inspect/", data=pcb, buffered=True)

    assert "imread returns None" in str(excinfo.value)
    # Sending godd JSON format but bad parameters
    pcb = """{
        "data": [
            {"wrong_KEY":  "../imgs/control/01_01.jpg",
               "value": "asasdasd"
             }]
    }"""

    with pytest.raises(SystemExit) as excinfo:
        resp = client.post("/inspect/", data=pcb, buffered=True)

    assert "Not able to find needed values in data dict" in str(
        excinfo.value)


# @pytest.mark.db
# def test_pipeline_db(client):
#     from app import Analysis

#     assert Analysis.analysis.methods["template_matching"].box_generator
#     assert len(
#         Analysis.analysis.methods["template_matching"].box_generator.get(1)) == 3

#     pcb = """{
#         "data": [
#             {"pcb_path": {"value": "../imgs/control/01_01.jpg"},
#               "template": {"value": 1}
#              }]
#     }"""

#     resp = client.post("/config/", data="tests/test_integration/config.yaml")
#     assert resp.status_code == 200

#     resp = client.post(
#         "/inspect/", data=pcb, buffered=True
#     )  # This buffered attribute is very important so that everything works as normal server is running
#     assert resp.status_code == 200

#     outcomes = client.get("/inspect/").data.decode("utf-8").replace("'", "")
#     outcomes = json.loads(outcomes)[0]
#     assert outcomes["result"] == "Defected"
#     assert outcomes["fiware_response"] == 204
#     assert outcomes["method"] == "difference"

#     # Testing other configuration
#     resp = client.post("/config/", data="tests/test_integration/config1.yaml")
#     assert resp.status_code == 200
#     resp = client.post(
#         "/inspect/", data=pcb, buffered=True
#     )  # This buffered attribute is very important so that everything works as normal server is running
#     assert resp.status_code == 200

#     outcomes = client.get("/inspect/").data.decode("utf-8").replace("'", "")
#     outcomes = json.loads(outcomes)[0]
#     assert outcomes["result"] == "Defected"
#     assert True == os.path.isdir(Analysis.analysis.path)
#     assert outcomes["fiware_response"] == 204
#     assert outcomes["method"] == "template_matching"

#     # sending bad config path
#     resp = client.post("/config/", data="tests/integration/asdgasfdg")
#     assert resp.status_code == 400

#     # Error in Aligner
#     Analysis.analysis.Aligner.good_match_percent = 0
#     with pytest.raises(SystemExit) as excinfo:
#         resp = client.post("/inspect/", data=pcb, buffered=True)

#     assert "Something went wrong" in str(excinfo.value)

#     # Somehow sizes doesn't match
#     pcb = """{
#         "data": [
#             {"pcb_path": {"value": "../imgs/control/04_05.jpg"},
#               "template": {"value": 1}
#              }]
#     }"""

#     Analysis.analysis.Aligner.apply = lambda x, y: x
#     with pytest.raises(SystemExit) as excinfo:
#         resp = client.post("/inspect/", data=pcb, buffered=True)

#     assert "Shapes of images does not match" in str(excinfo.value)

#     # Sending wrong path to img to be inspected
#     pcb = """{
#         "data": [
#             {"pcb_path": {"value": "../imgs/control/NotExisting.jpg"},
#               "template": {"value": 1}
#              }]
#     }"""

#     with pytest.raises(SystemExit) as excinfo:
#         resp = client.post("/inspect/", data=pcb, buffered=True)

#     assert "imread returns None" in str(excinfo.value)
#     # Sending not existing template
#     pcb = """{
#         "data": [
#             {"pcb_path": {"value": "../imgs/control/01_01.jpg"},
#               "template": {"value": 0}
#              }]
#     }"""

#     with pytest.raises(SystemExit) as excinfo:
#         resp = client.post("/inspect/", data=pcb, buffered=True)

#     assert "imread returns None" in str(excinfo.value)
#     # Sending godd JSON format but bad parameters
#     pcb = """{
#         "data": [
#             {"asdasdf": {"value": "../imgs/control/NotExisting.jpg"},
#               "adfads": {"value": 0}
#              }]
#     }"""

#     with pytest.raises(SystemExit) as excinfo:
#         resp = client.post("/inspect/", data=pcb, buffered=True)

#     assert "Not be able to find needed values in data dict" in str(
#         excinfo.value)
