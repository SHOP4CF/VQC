"""
File containing all fixtures
"""
import pytest
from flask.testing import FlaskClient

from app import create_app


@pytest.fixture
def app():
    app = create_app()
    yield app


@pytest.fixture
def client(app):
    app.test_client_class = FlaskClient
    return app.test_client()
