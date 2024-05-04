import time as tm
import matplotlib.pyplot as plt
from utils.data_utils import DataObject, PlottableDataObject, MultiPlotDataObject
from utils.redis_utils import RedisClient
import numpy as np
from loguru import logger

start = tm.time()
r = RedisClient(host='localhost', port=6379, key="cansat")
view_section: list[int] = [0, 50]


def update_data(d: list[DataObject], t: list) -> None:
    res = r.pop_list()
    if res:
        for e in d:
            e.update_data(res)

    else:
        for e in d:
            e.update_data(None)

    t.append(t[-1] + 1)

    if len(t) > 50:
        global view_section
        view_section = [view_section[0] + 1, view_section[1] + 1]
        plt.xlim(view_section)


def log_data(time: list[int], data: list[PlottableDataObject]) -> None:
    logger.info(f"Iteration: {time[-1]}")
    logger.info(time)
    for e in data:
        logger.info(f"{e.name}: {e.value}")


def main() -> None:
    r.initial_del()

    fig = plt.figure(figsize=(14, 8))
    gs = fig.add_gridspec(4, 4, hspace=0.2)

    # (temp_axes, pres_axes, humi_axes, part_axes), (alti_axes) = gs.subplots(sharex=False, sharey='row')
    temp_axes = fig.add_subplot(gs[0, :3])
    pres_axes = fig.add_subplot(gs[1, :3])
    humi_axes = fig.add_subplot(gs[2, :3])
    part_axes = fig.add_subplot(gs[3, :3])
    alti_axes = fig.add_subplot(gs[:4, 3])

    plt.ion()
    plt.xlim(view_section)

    temp = MultiPlotDataObject(name="Temperature", keys=[4, 7], initial_values=[0, 0], sources=["Pippo", "Pluto"],
                               ax=temp_axes, ylim=[0, 20], xlim=view_section, colors=["red", "orange"])
    pres = PlottableDataObject(name="Pressure", key=5, initial_value=0, ax=pres_axes, ylim=[0, 20], xlim=view_section,
                               color="blue")
    """alti = MultiPlotDataObject(name="Altitude", keys=[2, 6], initial_values=[0, 0], sources=["Pippo", "Pluto"],
                               ax=alti_axes, ylim=[0, 20], xlim=view_section, colors=["blueviolet", "magenta"])"""
    humi = PlottableDataObject(name="Humidity", key=8, initial_value=0, ax=humi_axes, ylim=[0, 20], xlim=view_section,
                               color="aqua")
    part = MultiPlotDataObject(name="Particulate", keys=[9, 10, 11], initial_values=[0, 0, 0],
                               sources=["Pippo", "Pluto", "Topolino"], ax=part_axes, ylim=[0, 20],
                               xlim=view_section, colors=["coral", "yellow", "lime"])

    data: list[PlottableDataObject] = [temp, pres, humi, part]
    time: list = [0]

    while True:
        update_data(data, time)

        log_data(time, data)

        for e in data:
            e.update_graph(xdata=time)

        plt.draw()
        plt.pause(1)


if __name__ == '__main__':
    main()
