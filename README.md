# Graph Plot for Iperf3 - gPerf

## What is it?

Just a graph plotting live for IPERF3 result.
Behind the sense it is running provided iperf command,
With the help of Python matplotlb, able to scrab the result and display it as a graph.

Graph appearance can be configured in config.txt with CMD too.
To help easily identify the case when using multiple locations.


![ezgif com-gif-maker](https://github.com/panhavad/gperf/assets/7156904/19e5a825-9eca-41aa-a152-d54081805be1)


## Why this?

To improve the analysis process of throughput result.
Help identify the pattern in the traffic.
Easy to read and understand, store the raw console log + graph type log as an array.

## How to use it?
### Developer execution
Installation of dependencies
```
pip install -r requirement.txt
```
### Configuration
By default below is the pre-configuration in file `config.txt`
```
[MAIN]
CMD=iperf3 -c 192.168.1.18 -B 192.168.15.10 -l1400 -t3600 -u -b100m -p2222 -P4 -R
#N for number of time, -1 for INFINITY
REPEAT=-1
[GRAPH]
MAXPLOTVIEW=100
COLOR=red
LINESTYLE=solid
MARKER=o
MARKERCOLOR=red
MARKERSIZE=3
VPLOTSIZE=6
HPLOTSIZE=10
```
Mainly will have to change `CMD` to meet your iperf requirement.
`REPEAT` is the number of times to repeat the command when the time is complete.
Put an integer for the number of times to be looped, put `-1` for infinity

_NOTE: Currently only support more than 1 parallel stream._

### Developer execution
After verifying `config.txt` is correct as you want to be, then execute the below command for starting the iperf and graph
```
python main.py
```
### Logging
This program output 2 log file:

1. Raw log of actual IPERF3 `iperf_console.log`
Including the command begin use & the start datetime
Sample:
```
root@DESKTOP:# cat iperf_console.log 
iperf3 -c 192.168.1.18 -B 192.168.15.10 -l1400 -t3600 -u -b100m -p2222 -P4 -R
2023-08-16 17:08:50.612390
Connecting to host 192.168.1.18, port 2222
Reverse mode, remote host 192.168.1.18 is sending
[  5] local 192.168.15.10 port 64861 connected to 192.168.1.18 port 2222
[  7] local 192.168.15.10 port 64862 connected to 192.168.1.18 port 2222
[  9] local 192.168.15.10 port 64863 connected to 192.168.1.18 port 2222
[ 11] local 192.168.15.10 port 64864 connected to 192.168.1.18 port 2222
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-1.00   sec  9.04 MBytes  75.9 Mbits/sec  0.202 ms  652/7425 (8.8%)
[  7]   0.00-1.00   sec  9.04 MBytes  75.9 Mbits/sec  0.209 ms  652/7425 (8.8%)
[  9]   0.00-1.00   sec  9.04 MBytes  75.9 Mbits/sec  0.204 ms  651/7425 (8.8%)
[ 11]   0.00-1.00   sec  9.04 MBytes  75.8 Mbits/sec  0.206 ms  654/7425 (8.8%)
[SUM]   0.00-1.00   sec  36.2 MBytes   303 Mbits/sec  0.205 ms  2609/29700 (8.8%)
```

2. Graphing data log `graph_history.log`
This is the X and Y data output from the graph, you can reuse the save data for plotting anywhere.
```
root@DESKTOP:# cat graph_history.log
X values:
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
Y values:
[303.0, 336.0, 335.0, 316.0, 332.0, 340.0, 331.0, 359.0, 336.0, 336.0]
```
