import time as tm
import matplotlib.pyplot as plt
# TODO: import numpy as np

from loguru import logger

from utils.data_utils import MultiPlotDataObject, GpsMPDO
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

            t.append(t[-1] + 1)

        else:
            # for e in d:
            #    e.update_data(None)
            logger.warning("No data found")

    except Exception as e:
        logger.error(e)


@logger.catch
def main() -> None:
    r.initial_del()

    fig = plt.figure(figsize=(14, 8))
    plt.subplots_adjust(
        left=0.05,
        bottom=0.038,
        right=1.1,
        top=0.98,
        wspace=0.4,
        hspace=0.4
    )
    gs = fig.add_gridspec(4, 9, hspace=0.2, wspace=0.55)

    # (temp_axes, pres_axes, humi_axes, part_axes), (alti_axes) = gs.subplots(sharex=False, sharey='row')
    temp_axes = fig.add_subplot(gs[0, :6])
    pres_axes = fig.add_subplot(gs[1, :6])
    humi_axes = fig.add_subplot(gs[2, :6])
    part_axes = fig.add_subplot(gs[3, :6])
    alti_axes = fig.add_subplot(gs[2:4, 6:8])
    # alti_bar_axes = fig.add_subplot(gs[2:4, 7:8])
    gps_axes = fig.add_subplot(gs[:2, 6:8])

    plt.ion()
    plt.xlim(view_section)

    temp = MultiPlotDataObject(
        ax=temp_axes,
        # colors=["red", "orange"],
        initial_values=[0, 0],
        keys=[5, 8],
        name="Temperature",
        sources=["Pressure", "Humidity"],
        xlim=view_section,
        ylim=[0, 20],
        delta=1
    )
    pres = MultiPlotDataObject(
        ax=pres_axes,
        # color="blue",
        initial_values=[0],
        keys=[6],
        name="Pressure",
        # sources=["Pressure"],
        xlim=view_section,
        ylim=[0, 20],
        delta=2500
    )
    alti = MultiPlotDataObject(
        ax=alti_axes,
        # colors=["blueviolet", "magenta"],
        initial_values=[0, 0],
        keys=[3, 7],
        name="Altitude",
        sources=["GPS", "Barometer"],
        xlim=view_section,
        ylim=[0, 20],
        delta=1
    )
    humi = MultiPlotDataObject(
        ax=humi_axes,
        # color="aqua",
        initial_values=[0],
        keys=[9],
        name="Humidity",
        # sources=["Humidity"],
        xlim=view_section,
        ylim=[0, 20],
        delta=1
    )
    part = MultiPlotDataObject(
        ax=part_axes,
        # colors=["coral", "yellow", "lime"],
        initial_values=[0, 0, 0],
        keys=[10, 11, 12],
        name="Particulate",
        sources=["Pm1", "Pm2.5", "Pm10"],
        xlim=view_section,
        ylim=[0, 20],
        delta=1
    )
    gps = GpsMPDO(
        ax=gps_axes,
        # initial_values=[0, 0],
        keys=[1, 2],
        name="GPS",
        sources=["X", "Y"],
        xlim=view_section,
        ylim=[0, 20]
    )

    data: list[MultiPlotDataObject] = [temp, pres, humi, part, alti, gps]
    time: list = [0]

    while True:
        logger.info(f"Iteration: {time[-1]}")
        update_data(data, time)

        for e in data:
            e.update_graph(xdata=time)

        plt.draw()
        plt.pause(0.2)


if __name__ == '__main__':
    main()
