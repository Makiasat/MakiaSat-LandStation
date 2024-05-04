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

    fig, (temp_axes, pres_axes, alti_axes, humi_axes, part_axes) = plt.subplots(nrows=5, ncols=1, sharex=True,
                                                                                sharey=False, figsize=(10, 6))
    plt.ion()
    plt.xlim(view_section)

    temp = MultiPlotDataObject(name="Temperature", keys=[4, 7], initial_values=[0, 0], sources=["Pippo", "Pluto"],
                               ax=temp_axes, ylim=[0, 20], colors=["red", "orange"])
    pres = PlottableDataObject(name="Pressure", key=5, initial_value=0, ax=pres_axes, ylim=[0, 20], color="blue")
    alti = MultiPlotDataObject(name="Altitude", keys=[2, 6], initial_values=[0, 0], sources=["Pippo", "Pluto"],
                               ax=alti_axes, ylim=[0, 20], colors=["blueviolet", "magenta"])
    humi = PlottableDataObject(name="Humidity", key=8, initial_value=0, ax=humi_axes, ylim=[0, 20], color="aqua")
    part = MultiPlotDataObject(name="Particulate", keys=[9, 10, 11], initial_values=[0, 0, 0],
                               sources=["Pippo", "Pluto", "Topolino"], ax=part_axes, ylim=[0, 20],
                               colors=["coral", "yellow", "lime"])

    data: list[PlottableDataObject] = [temp, pres, alti, humi, part]
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
