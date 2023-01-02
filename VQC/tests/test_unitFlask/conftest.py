"""
File containing all fixtures it is very usefull to define flask app and client
here, all tests defined in that folder have access to it
"""
import pytest
from app import create_app
from os.path import join


@pytest.fixture
def app():
    app = create_app(join("tests", "config", "configuration.yaml"))
    yield app


@pytest.fixture
def client(app):
    return app.test_client(join("tests", "config", "configuration.yaml"))
