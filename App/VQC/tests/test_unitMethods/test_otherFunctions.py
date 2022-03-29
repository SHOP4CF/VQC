import app.otherFunctions as otherFunctions
import pytest
import datetime


def test_fiware_response():
    assert otherFunctions.fiware_response.respond(
        1, str(datetime.datetime.utcnow()), "testing") == 204

    # Exception when we send request with bad id
    otherFunctions.fiware_response.final_url = f"http://localhost:1026/ngsi-ld/v1/entities/NotExistingID"

    with pytest.raises(SystemExit) as excinfo:
        otherFunctions.fiware_response.respond(
            1, str(datetime.datetime.utcnow()), "testing")

    assert "Failed to update entity" in str(excinfo.value)
    otherFunctions.fiware_response.id_ = "vqc1"
    # Exception when we try to send request to FIWARE but can't connect with server
    # otherFunctions.fiware_response.url = "http://123.123.123.123:1026/v2/entities"

    # with pytest.raises(SystemExit) as excinfo:
    #     otherFunctions.fiware_response.respond(1, 1, "testing")

    # assert "Failed to connect with FIWARE" in str(excinfo.value)
