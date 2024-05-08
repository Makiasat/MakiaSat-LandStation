import time as tm
import matplotlib.pyplot as plt
# TODO: import numpy as np

from loguru import logger

from utils.data_utils import MultiPlotDataObject
from utils.redis_utils import RedisClient
from utils.log_utils import setup_logger
from config import VIEW_SECTION, REDIS_HOST, REDIS_PORT, REDIS_KEY

start = tm.time()
setup_logger(logger, "worker-logs/{time}.log")
r = RedisClient(host=REDIS_HOST, port=REDIS_PORT, key=REDIS_KEY)
view_section: list[int] = VIEW_SECTION


def update_data(d: list[MultiPlotDataObject], t: list) -> None:
    logger.info("Getting data from redis")
    res = r.pop_list()
    try:
        if res:
            for e in d:
                e.update_data(res)
            logger.success(f"Data retrieved ->\n {res}")

        else:
            for e in d:
                e.update_data(None)
            logger.warning("No data found")

        t.append(t[-1] + 1)

    except Exception as e:
        logger.error(e)


@logger.catch
def main() -> None:
    r.initial_del()

    fig = plt.figure(figsize=(14, 8))
    gs = fig.add_gridspec(4, 4, hspace=0.2, wspace=0.4)

    # (temp_axes, pres_axes, humi_axes, part_axes), (alti_axes) = gs.subplots(sharex=False, sharey='row')
    temp_axes = fig.add_subplot(gs[0, :3])
    pres_axes = fig.add_subplot(gs[1, :3])
    humi_axes = fig.add_subplot(gs[2, :3])
    part_axes = fig.add_subplot(gs[3, :3])
    alti_axes = fig.add_subplot(gs[:4, 3])

    plt.ion()
    plt.xlim(view_section)

    temp = MultiPlotDataObject(
        ax=temp_axes,
        # colors=["red", "orange"],
        initial_values=[0, 0],
        keys=[4, 7],
        name="Temperature",
        sources=["Pressure", "Humidity"],
        xlim=view_section,
        ylim=[0, 20]
    )
    pres = MultiPlotDataObject(
        ax=pres_axes,
        # color="blue",
        initial_values=[0],
        keys=[5],
        name="Pressure",
        # sources=["Pressure"],
        xlim=view_section,
        ylim=[0, 20]
    )
    alti = MultiPlotDataObject(
        ax=alti_axes,
        # colors=["blueviolet", "magenta"],
        initial_values=[0, 0],
        keys=[2, 6],
        name="Altitude",
        sources=["GPS", "Barometer"],
        xlim=view_section,
        ylim=[0, 20]
    )
    humi = MultiPlotDataObject(
        ax=humi_axes,
        # color="aqua",
        initial_values=[0],
        keys=[8],
        name="Humidity",
        # sources=["Humidity"],
        xlim=view_section,
        ylim=[0, 20]
    )
    part = MultiPlotDataObject(
        ax=part_axes,
        # colors=["coral", "yellow", "lime"],
        initial_values=[0, 0, 0],
        keys=[9, 10, 11],
        name="Particulate",
        sources=["Pm1", "Pm2.5", "Pm10"],
        xlim=view_section,
        ylim=[0, 20]
    )

    data: list[MultiPlotDataObject] = [temp, pres, humi, part, alti]
    time: list = [0]

    while True:
        logger.info(f"Iteration: {time[-1]}")
        update_data(data, time)

        for e in data:
            e.update_graph(xdata=time)

        plt.draw()
        plt.pause(1)


if __name__ == '__main__':
    main()