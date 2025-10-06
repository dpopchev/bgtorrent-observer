import pytest
from fastapi.testclient import TestClient

from bgtorrent_observer.app import app


@pytest.fixture
def clinet():
    return TestClient(app)

def test_get_status_code(client: TestClient):
    assert client.get("/").status_code == 200
