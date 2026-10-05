from fastapi.testclient import TestClient
import pytest

from app.database import Base, engine
from app.main import app


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


def test_create_reading_success(client: TestClient, monkeypatch):
    monkeypatch.setenv("SENSOR_API_KEY", "test-sensor-key")

    sensors = client.get("/sensors").json()
    assert len(sensors) >= 1
    sensor_id = sensors[0]["id"]

    response = client.post(
        "/sensors/data",
        headers={"X-Sensor-Key": "test-sensor-key"},
        json={"sensor_id": sensor_id, "value": 21.5, "unit": "C"},
    )

    assert response.status_code == 201
    assert response.json()["sensor_id"] == sensor_id
    assert float(response.json()["value"]) == 21.5


def test_create_reading_invalid_key(client: TestClient, monkeypatch):
    monkeypatch.setenv("SENSOR_API_KEY", "test-sensor-key")

    sensors = client.get("/sensors").json()
    sensor_id = sensors[0]["id"]

    response = client.post(
        "/sensors/data",
        headers={"X-Sensor-Key": "wrong-key"},
        json={"sensor_id": sensor_id, "value": 21.5},
    )

    assert response.status_code == 401


def test_create_reading_unknown_sensor(client: TestClient, monkeypatch):
    monkeypatch.setenv("SENSOR_API_KEY", "test-sensor-key")

    response = client.post(
        "/sensors/data",
        headers={"X-Sensor-Key": "test-sensor-key"},
        json={"sensor_id": 9999, "value": 21.5},
    )

    assert response.status_code == 404