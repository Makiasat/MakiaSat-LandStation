from matplotlib import pyplot as plt


class DataObject:
    def __init__(self, name: str, key: int, initial_value: float = None):
        self.name: str = name
        self.key: int = key
        self.value: list[float] = [initial_value]

    def __str__(self) -> str:
        return f'{self.name} - {self.key} - {self.value}'

    def __int__(self) -> int:
        return self.key

    def update_data(self, new_data: list[float] = None) -> None:
        if new_data:
            self.value.append(new_data[self.key])
        else:
            self.value.append(0)


class PlottableDataObject(DataObject):
    def __init__(self,
                 ax: plt.axes,
                 name: str,
                 key: int,
                 xlim: list[int],
                 ylim: list[int] = None,
                 initial_value: float = None,
                 color: str = None
                 ):
        super().__init__(name, key, initial_value)

        self.ax: plt.axes = ax

        if ylim:
            self.ylim: list[int] = ylim
            self.ax.set_ylim(self.ylim)

        self.xlim: list[int] = xlim
        self.ax.set_xlim(self.xlim)

        self.ax.set_ylabel(self.name)
        self.line, = self.ax.plot(self.value)

        if color:
            self.line.set_color(color)

    def update_graph(self, xdata: list) -> None:
        self.line.set_ydata(self.value)
        self.line.set_xdata(xdata)

        if len(self.value) > 50:
            self.xlim = [self.xlim[0] + 1, self.xlim[1] + 1]
            self.ax.set_xlim(self.xlim)


class MultiPlotDataObject:
    def __init__(self,
                 ax: plt.axes,
                 name: str,
                 keys: list[int],
                 xlim: list[int],
                 ylim: list[int] = None,
                 sources: list[str] = None,
                 initial_values: list[float] = None,
                 colors: list[str] = None):

        self.name: str = name
        self.keys: list[int] = keys

        self.value: list[list[float]] = []
        if initial_values:
            for e in initial_values:
                self.value.append([e])
        else:
            for e in keys:
                self.value.append([])

        self.ax: plt.axes = ax
        if ylim:
            self.ylim: list[int] = ylim
            self.ax.set_ylim(self.ylim)

        self.xlim: list[int] = xlim
        self.ax.set_xlim(self.xlim)

        self.ax.set_ylabel(self.name)

        self.lines: list = []
        if sources:
            for i, e in enumerate(self.value):
                self.lines.append(self.ax.plot(e, label=sources[i])[0])
                # TODO: Label not working -> https://matplotlib.org/stable/users/explain/axes/axes_intro.html#axes-labelling-and-annotation
        else:
            for e in self.value:
                self.lines.append(self.ax.plot(e)[0])

        if colors:
            self.colors: list[str] = colors
            for i, e in enumerate(self.colors):
                self.lines[i].set_color(e)

    def __str__(self) -> str:
        return f'{self.name} - {self.keys} - {self.value}'

    def __int__(self) -> list[int]:
        return self.keys

    def update_data(self, new_data: list[float] = None) -> None:
        if new_data:
            for i, e in enumerate(self.value):
                e.append(new_data[self.keys[i]])
        else:
            for e in self.value:
                e.append(0)

        if len(self.value[0]) > 50:
            self.xlim = [self.xlim[0] + 1, self.xlim[1] + 1]
            self.ax.set_xlim(self.xlim)

        self.ax.set_ylim()

    def update_graph(self, xdata: list) -> None:
        for i, e in enumerate(self.lines):
            e.set_ydata(self.value[i])
            e.set_xdata(xdata)
