import app.otherFunctions as otherFunctions
import app.otherFunctions.debug_help as dh
import pytest
import datetime
"""
fiware_response:
    1. test if fiware response is functional, by sending a message "testing"
    2. check if fiware fails if the same data is entered twice
"""


@pytest.mark.response
def test_fiware_response():
    responder = dh.fiware_responder

    assert responder is not None

    assert responder.respond(
        1, str(datetime.datetime.utcnow()), "testing") == 204

    # Exception when we try to send request to FIWARE but can't connect with
    # server
    responder.set_url("http://123.123.123.123:1026/v2/entities")

    with pytest.raises(SystemExit) as excinfo:
        responder.respond(1, str(1), "testing")

    assert "Failed to connect with FIWARE" in str(excinfo.value)

    # Exception when we send request with bad id
    responder.set_url(
        "http://localhost:1026/ngsi-ld/v1/entities/NotExistingID")

    with pytest.raises(SystemExit) as excinfo:
        responder.respond(
            1, str(datetime.datetime.utcnow()), "testing")

    assert "Failed to update entity" in str(excinfo.value)
    otherFunctions.fiware_response.id_ = "vqc1"
