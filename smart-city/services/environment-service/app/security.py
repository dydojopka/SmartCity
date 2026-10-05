import os

from fastapi import Header, HTTPException, status


def verify_sensor_key(
    x_sensor_key: str | None = Header(default=None, alias="X-Sensor-Key"),
) -> None:
    expected = os.getenv("SENSOR_API_KEY", "demo-sensor-key")
    if not x_sensor_key or x_sensor_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный ключ датчика",
        )