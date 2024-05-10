import re
import serial
import time
from loguru import logger
from csv import writer
from csv import Error as CSV_Error
from os import path, rename

from config import CSV_FILE_PATH, SERIAL_PORT, BAUD_RATE, REDIS_HOST, REDIS_PORT, REDIS_KEY
from utils.fake_utils import get_fake_random_serial
from utils.log_utils import setup_logger
from utils.redis_utils import RedisClient

setup_logger(logger, "dispatcher-logs/{time}.log", serial=True)
r = RedisClient(host=REDIS_HOST, port=REDIS_PORT, key=REDIS_KEY)

# validate_pattern = r"([+-]?\d+(\.?\d+)?)\,\s([+-]?\d+(\.?\d+)?)\,\s([+-]?\d+(\.?\d+)?)\,\s(\d{2}:\d{2}:\d{2})\,\s([+-]?\d+(\.?\d+)?)\,\s([+-]?\d+(\.?\d+)?)\,\s([+-]?\d+(\.?\d+)?)\,\s([+-]?\d+(\.?\d+)?)\,\s([+-]?\d+(\.?\d+)?)\,\s([+-]?\d+(\.?\d+)?)\,\s([+-]?\d+(\.?\d+)?)\,\s([+-]?\d+(\.?\d+)?)"
# validate_pattern = r"([+-]?(\d+)?(\.?\d+)?)\,\s([+-]?(\d+)?(\.?\d+)?)\,\s([+-]?(\d+)?(\.?\d+)?)\,(\s)?(\d{2}:\d{2}:\d{2})\,\s([+-]?(\d+)?(\.?\d+)?)\,\s([+-]?(\d+)?(\.?\d+)?)\,\s([+-]?(\d+)?(\.?\d+)?)\,\s([+-]?(\d+)?(\.?\d+)?)\,\s([+-]?(\d+)?(\.?\d+)?)\,\s([+-]?(\d+)?(\.?\d+)?)\,\s([+-]?(\d+)?(\.?\d+)?)\,\s([+-]?(\d+)?(\.?\d+)?)"
validate_pattern = r"(?i)((NaN)?([+-]?(\d+)?(\.?\d+)?)\,\s?){3}(\d{2}:\d{2}:\d{2})\,\s?((NaN)?([+-]?(\d+)?(\.?\d+)?)\,\s?){7}((NaN)?[+-]?(\d+)?(\.?\d+)?)"


def connect() -> serial:
    idle: bool = True
    ser = None
    while idle:
        try:
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        except Exception as e:
            logger.error(e)
            time.sleep(1)
        if ser:
            logger.success(f"Connected to {ser.port} ✅")
            idle = False
            return ser


def create_csv() -> None:
    logger.info("Creating " + CSV_FILE_PATH)
    try:
        if path.exists(CSV_FILE_PATH):
            new_name: str = f"{CSV_FILE_PATH.split('/')[0]}/{time.time()}-{CSV_FILE_PATH.split('/')[1]}"
            rename(CSV_FILE_PATH, new_name)
            logger.info(f"CSV file Renamed to: {new_name}")

        with open(CSV_FILE_PATH, 'w', encoding='UTF8') as f:
            wr = writer(f)

            wr.writerow(
                ['Iteration', 'Latitude', 'Longitude', 'Elevation', 'Time', 'Temperature', 'Pressure', 'Elevation',
                 'Temperature', 'Humidity', 'Pm1', 'Pm2.5', 'Pm10'])
            logger.success("Created " + CSV_FILE_PATH)

    except CSV_Error as e:
        logger.error("Failed to write csv headers:")
        logger.error(e)

    except OSError as e:
        logger.error("Failed to create CSV file:")
        logger.error(e)

    except Exception as e:
        logger.error(e)


def add_to_csv(row: list, iteration: int) -> None:
    row.insert(0, iteration)
    try:
        with open(CSV_FILE_PATH, 'a', encoding='UTF8', newline='') as f:
            wr = writer(f)
            wr.writerow(row)
            logger.success("Added data to " + CSV_FILE_PATH)

    except CSV_Error as e:
        logger.error("Failed to write csv data:")
        logger.error(e)

    except Exception as e:
        logger.error(e)


def validate_serial(data: str) -> bool:
    match = re.search(validate_pattern, data)
    if not match:
        logger.error("Invalid serial output")
    return True if match else False


def normalize_serial(data: str) -> list:
    t = data.split(",")
    k = []
    for i in t:
        if ":" in i:
            k.append(i)
        elif "-" in i:
            k.append(0)
        elif "Nan" in i:
            k.append(0)
        elif "nan" in i:
            k.append(0)
        else:
            k.append(float(i))
    return k


@logger.catch
def main() -> None:
    create_csv()

    ser = None

    iteration = 0
    while True:

        if not ser:
            ser = connect()

        logger.info(f"Iteration number: {iteration}")
        iteration += 1

        try:
            response = ser.readline().decode("utf-8").strip()
            # response = get_fake_random_serial()
            logger.log("SERIAL", response)

            if response and validate_serial(response):

                data = normalize_serial(response)

                logger.info(f"Received -> \n{data}")
                add_to_csv(data, iteration)
                try:
                    r.push_list(data)
                    logger.success(f"Pushed data to Redis")
                except Exception as e:
                    logger.error(e)

        except OSError as e:
            ser = None
            logger.error(f"Disconnected: {e}")
        except Exception as e:
            logger.error(e)


if __name__ == '__main__':
    main()
