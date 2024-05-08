# MakiaSat Land Station Software 💻
This software makes it possible to save and display data, transmitted by CanSat, received from an antenna via the serial port in real time.

## Requirements

The following dependencies must be installed to use the code:
- [`Redis`](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/)
- [`Pyrhon >= 3.11`](https://docs.anaconda.com/free/miniconda/miniconda-install/)

You can install all the python libraries you need using the command:
```
pip install -r requirements.txt
```

## Usage

First of all, it is neessary that redis is running
```
redis-server
```
To start the data collection program, simply run
```
python main.py
```
Open another shell to plot the data
```
python worker.py
```

## Documentation
> [!CAUTION]
> Sorry, documentation is planned ...

## How does it works ?

The dispatcher handles receiving the data its saving and adding it to a queue hosted on a redis database that is iterated by a worker that parses the data in order to display it in real time in an animated graph

```mermaid
graph
S(Serila Port)
A([Dispatcher])
B([Worker])
c[(Redis Queue)]
D[data.csv]

B --> P[Real time plot dashboard]
S --> A
A <--> c
B <--> c
A --> D

```
