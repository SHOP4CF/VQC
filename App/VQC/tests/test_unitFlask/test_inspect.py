import pytest

"""As unit tests only those two request are possible to test"""

def test_config(client):
    assert client.get("/inspect/").status_code == 200
    assert (
        client.post("/inspect/").status_code == 400
    )  # if we send post with invalid or no data then our server should return
    # status code equal to 400

