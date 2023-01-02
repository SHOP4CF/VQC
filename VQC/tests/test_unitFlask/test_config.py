from os.path import join

"""Just test whether our config page responds correctly """


def test_config(client):
    assert client.get("/config/").status_code == 200
    assert client.post("/config/",
                       data=join("tests", "config",
                                 "configuration.yaml")).status_code == 200
    assert client.post("/config/", data="12352135wf").status_code == 400
