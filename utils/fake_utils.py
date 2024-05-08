import datetime as dt
import random
import time


def random_float_range(min: float, max: float) -> float:
    return random.uniform(min, max)


def random_float_delta(ref: float, delta: float) -> float:
    return random_float_range(ref - delta, ref + delta)


def get_fake_random_serial() -> str:
    """
    Utility that returns a text string with random fake values of the following metrics: Latitude, Longitude, Altitude,
    Time, Temperature, Pressure, Altitude, Temperature, Humidity, Pm1, Pm2.5, Pm10
    """
    time.sleep(1)

    t: list = []

    # 1 - Latitude
    t.append(f"{random_float_delta(45.502708, 0.25):.6f}")

    # 2 - Longitude
    t.append(f"{random_float_delta(9.325446, 0.25):.6f}")

    # 3 - Altitude
    t.append(f"{random_float_delta(117.20, 3.0):.6f}")

    # 4 - Time
    now = dt.datetime.now()
    # t.append(now.timestamp())
    t.append(now.strftime('%H:%M:%S'))

    # 5 - Temperature
    t.append(f"{random_float_delta(27.81, 1.5):.6f}")

    # 6 - Pressure
    t.append(f"{random_float_delta(100270.00, 5000.0):.6f}")

    # 7 - Altitude
    t.append(f"{random_float_delta(88.21, 3.0):.6f}")

    # 8 - Temperature
    t.append(f"{random_float_delta(26.68, 1.5):.6f}")

    # 9 - Humidity
    t.append(f"{random_float_delta(29.28, 1.5):.6f}")

    # 10 - Pm1
    t.append(1)

    # 11 - Pm2.5
    t.append(2)

    # 12 - Pm10
    t.append(3)

    return ', '.join(list(map(str, t)))
