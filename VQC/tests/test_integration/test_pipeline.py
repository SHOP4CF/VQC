import pytest
import json
from app import Analysis
from os.path import join, isdir

"""
we test pipeline with few scenarios:
   1. Upload new config
        -> send post at /inspect/ with pcb data
        -> get outcomes from /inspect/
        -> jest whether inspections went well
   2. Same as first but for different config
   3. sending wrong config path
   4. sending query with path to no existing image we expect exception
   5. sending query with not existing template we expect exception
   6. sending query with from json data we again expect exception
"""

integration_path = join("tests", "test_integration")


def get_pcb(pcb_path: str, value: str) -> str:
    # get the json with the data specified
    return f'{{"data": [{{"pcb_path": "{pcb_path}","value": "{value}"}}]}}'


def config_test(client, config: str, code: int):
    # test the configs
    resp = client.post("/config/", data=join(integration_path, config))
    assert resp.status_code == code


def pcb_test(client, pcb: str, status_code: int = 400):
    # test the pcb jsons
    resp = client.post("/inspect/", data=pcb, buffered=True)
    # This buffered attribute is very important so that everything works as
    # normal server is running
    assert resp.status_code == status_code


def bad_pcb_test(client, pcb: str, result: str):
    with pytest.raises(SystemExit) as excinfo:
        pcb_test(client, pcb)

    assert result in str(excinfo.value)


def outcome_test(client, result: str, fiware_response: int,
                 method: str, dir_exist: bool = False) -> None:
    outcomes = client.get("/inspect/").data.decode("utf-8").replace("'", "")
    outcomes = json.loads(outcomes)[0]
    assert outcomes["result"] == result
    if dir_exist:
        assert isdir(Analysis.analysis.path) is True
    assert outcomes["fiware_response"] == fiware_response
    assert outcomes["method"] == method


def test_config_pipeline(client):
    assert Analysis.analysis.methods["template_matching"].box_generator
    assert len(
        Analysis.analysis.methods["template_matching"].box_generator
        .get("./imgs/template/01.JPG")) == 3

    pcb = get_pcb("./imgs/control/01_01.jpg", "./imgs/template/01.JPG")

    config_test(client, "config.yaml", 200)
    pcb_test(client, pcb, 200)
    outcome_test(client, "Defected", 204, "difference")

    # Testing other configuration
    config_test(client, "config1.yaml", 200)
    pcb_test(client, pcb, 200)
    outcome_test(client, "Defected", 204, "template_matching", True)

    # sending bad config path
    config_test(client, "asdgasfdg", 400)


def test_bad_data_pipeline(client):
    pcb = get_pcb("./imgs/control/01_01.jpg", "./imgs/template/01.JPG")

    # Error in Aligner
    Analysis.analysis.Aligner.good_match_percent = 0
    bad_pcb_test(client, pcb, "Not enough keypoints to perform alignment!")

    # Somehow sizes doesn't match
    pcb = get_pcb("./imgs/control/04_05.jpg", "./imgs/template/01.JPG")
    Analysis.analysis.Aligner.apply = lambda x, y: x
    bad_pcb_test(client, pcb, "Shapes of images does not match")

    # Sending wrong path to img to be inspected
    pcb = get_pcb("./imgs/control/NotExisting.jpg", "./imgs/template/01.JPG")
    bad_pcb_test(client, pcb, "imread returns None")

    # Sending not existing template
    pcb = get_pcb("./imgs/control/01_01.jpg", "asasdasd")
    bad_pcb_test(client, pcb, "imread returns None")

    # Sending good JSON format but bad parameters
    pcb_path = "./imgs/control/01_01.jpg"
    pcb = f'{{"data": [{{"wrong_KEY":  "{pcb_path}","value": "asasdasd"}}]}}'
    bad_pcb_test(client, pcb, "Not able to find needed values in data dict")
