import pytest
from flask import Flask

from src.app import add_header

@pytest.fixture
def test_app():
    test_app = Flask(__name__)
    test_app.after_request_funcs.setdefault(None, []).append(add_header)

