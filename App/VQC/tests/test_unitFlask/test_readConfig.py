import pytest

from app.otherFunctions import readConfig

"""
Just try to raise both exceptions in readConfig function to make sure they work properly
"""


def test_readConfig():

    with pytest.raises(SystemExit) as excinfo:
        readConfig.read_config("not_existing_config.yaml")

    assert "incorrect configuration path" in str(excinfo.value)

    with pytest.raises(SystemExit) as excinfo:
        readConfig.read_config("tests/test_unitFlask/config_invalid.yaml")

    assert "readConfig: " in str(excinfo)

