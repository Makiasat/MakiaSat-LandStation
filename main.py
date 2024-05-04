import serial
import time
from redis import Redis
from loguru import logger
from csv import writer
from csv import Error as CSV_Error
from os import path, rename
from datetime import datetime

from utils.redis_utils import RedisClient

from pickle import dumps

CSV_FILE_PATH = 'data/data.csv'
SERIAL_PORT = '/dev/cu.usbmodem1101'
BAUD_RATE = 9600

r = RedisClient(host="localhost", port=6379, key="cansat")


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
            rename(CSV_FILE_PATH, f"{datetime.timestamp(datetime.now())}-{CSV_FILE_PATH}")
            logger.info("Removed " + CSV_FILE_PATH)

        with open(CSV_FILE_PATH, 'w', encoding='UTF8') as f:
            wr = writer(f)

            wr.writerow(
                ['Latitudine', 'Longitudine', 'Altitudine', 'Tempo', 'Temperatura', 'Pressione', 'Altitudine',
                 'Temperatura', 'Umidita', 'Pm1', 'Pm2.5', 'Pm10', ])
            logger.success("Created " + CSV_FILE_PATH)

    except CSV_Error as e:
        logger.error("Failed to write csv headers:")
        logger.error(e)

    except OSError as e:
        logger.error("Failed to create CSV file:")
        logger.error(e)

    except Exception as e:
        logger.error(e)


def add_to_csv(row: list) -> None:
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


def main() -> None:
    create_csv()

    ser = None
    while True:

        if not ser:
            ser = connect()

        try:
            response = ser.readline().decode("utf-8").strip()

            if response:
                data = response.split(",")

                logger.info(f"Received --> {data}")
                add_to_csv(data)
                r.push_list(data)

        except OSError as e:
            ser = None
            logger.error(f"Disconnected: {e}")
        except Exception as e:
            logger.error(e)


if __name__ == '__main__':
    main()
