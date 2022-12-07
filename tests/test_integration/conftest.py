"""
File containing all fixtures
"""
import pytest
from flask.testing import FlaskClient
from os.path import join

from VQC.app import create_app


@pytest.fixture
def app():
    app = create_app(join("tests", "config", "configuration.yaml"))
    yield app


@pytest.fixture
def client(app):
    app.test_client_class = FlaskClient
    return app.test_client()
