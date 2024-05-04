import serial
import time
from loguru import logger
from csv import writer
from csv import Error as CSV_Error
from os import path, remove
from datetime import datetime

from utils.redis_utils import RedisClient
from utils.log_utils import setup_logger
from config import CSV_FILE_PATH, SERIAL_PORT, BAUD_RATE, REDIS_HOST, REDIS_PORT, REDIS_KEY

setup_logger(logger, "dispatcher-logs/{time}.log")
r = RedisClient(host=REDIS_HOST, port=REDIS_PORT, key=REDIS_KEY)


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
            remove(CSV_FILE_PATH)
            logger.info("Removed " + CSV_FILE_PATH)
        """
        if path.exists(CSV_FILE_PATH):
            rename(CSV_FILE_PATH, f"{datetime.timestamp(datetime.now())}-{CSV_FILE_PATH}")
            logger.info("Removed " + CSV_FILE_PATH)
        """

        """if path.exists(CSV_FILE_PATH):
            prefix = 0
            existing_path = CSV_FILE_PATH
            while True:
                if path.exists(f"{prefix}-{CSV_FILE_PATH}"):
                    existing_path = f"{prefix}-{CSV_FILE_PATH}"
                    prefix += 1
                else:
                    rename(existing_path, f"{prefix}-{CSV_FILE_PATH}")
                    logger.success(f"Existing file renamed: {prefix}-{CSV_FILE_PATH}")"""

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

            if response:
                data = response.split(",")

                logger.info(f"Received -> \n{data}")
                add_to_csv(data)
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
