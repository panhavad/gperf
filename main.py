import subprocess
import re
from turtle import color
import matplotlib.pyplot as plt
import datetime
import time
import signal
import configparser
import os


config = configparser.ConfigParser()
config.read_file(open(r'config.txt'))

NOW = datetime.datetime.now()
START_TIME = str(NOW)
START_TIME_NAME = NOW.strftime("%Y%m%d-%H%M%S")

TIMEOPTION = int(config.get('MAIN', 'TIMEOPTION'))
PARALLEL = 1
BIDIRFLAG = 0
SERVERFLAG = 0

MAXPLOTVIEW = int(config.get('GRAPH', 'MAXPLOTVIEW'))
CMD = config.get('MAIN', 'CMD')
COLOR = config.get('GRAPH', 'COLOR')
LINESTYLE = config.get('GRAPH', 'LINESTYLE')
MARKER = config.get('GRAPH', 'MARKER')
MARKERCOLOR = config.get('GRAPH', 'MARKERCOLOR')
MARKERSIZE = config.get('GRAPH', 'MARKERSIZE')
REPEAT = int(config.get('MAIN', 'REPEAT'))
VPLOTSIZE = int(config.get('GRAPH', 'VPLOTSIZE'))
HPLOTSIZE = int(config.get('GRAPH', 'HPLOTSIZE'))


x_vals = []
y_vals = []
# Define the signal handler function
def signal_handler(signal, frame):
    print("\nCtrl + C detected. Exiting gracefully.")
    exit(0)

def output_log():
    if not os.path.exists('logs/' + START_TIME_NAME):
        os.makedirs('logs/' + START_TIME_NAME)
    graph_history_file = "logs/" + START_TIME_NAME + "/graph-history-" + START_TIME_NAME + ".log"

    with open(graph_history_file, "w") as file:
        file.write("X values:\n")
        file.write(str(x_vals))

        file.write("\nY values:\n")
        file.write(str(y_vals))

def output_iperf_console_log(console_log_line, fresh_start):
    if not os.path.exists('logs/' + START_TIME_NAME):
        os.makedirs('logs/' + START_TIME_NAME)
    iperf_console_file = "logs/" + START_TIME_NAME + "/iperf-console-" + START_TIME_NAME + ".log"

    if fresh_start:
        with open(iperf_console_file, "w") as file:
            file.write(console_log_line + '\n')
    else:
        with open(iperf_console_file, "a") as file:
            file.write(console_log_line)

def run_iperf(iperf_cmd):
    output_iperf_console_log(START_TIME+'\n', 0)

    global MAXPLOTVIEW
    global BIDIRFLAG
    global SERVERFLAG

    global x_vals
    global y_vals

    rep_counter = 1
    mbits_per_sec = 0
    plt.figure(figsize=(HPLOTSIZE,VPLOTSIZE))

    plt.xlabel('Time (intervals)')
    plt.ylabel('Mbits/sec')
    plt.title('iPerf Results')
    plt.grid(True)

    plt.annotate('Start Datetime: '+START_TIME, xy = (0, 1.03), xycoords='axes fraction', fontsize=7)
    at_rep = plt.annotate("Repetition: " + str(rep_counter), xy = (1, 1.03), xycoords='axes fraction', fontsize=7)
    current_tpt = plt.annotate("Current: " + str(mbits_per_sec) + " Mbps", xy = (0.93, -0.13), xycoords='axes fraction', fontsize=10, color=COLOR)
    # at_rep = plt.annotate("Repetition: " + str(rep_counter), xy = (1, 1.03), xycoords='axes fraction', fontsize=7)
    plt.annotate("Command: " + ' '.join(iperf_cmd), xy = (0.0, -0.13), xycoords='axes fraction', fontsize=7)

    fig = plt.gcf()
    fig.show()
    while True:
        if rep_counter <= REPEAT or REPEAT == -1:
            # signal.signal(signal.SIGINT, signal_handler)
            with subprocess.Popen(iperf_cmd, stdout=subprocess.PIPE, universal_newlines=True) as proc:
                match_counter = 1
                at_rep.set_text("Repetition: " + str(rep_counter))
                for line in proc.stdout:
                    print(line, end='')
                    output_iperf_console_log(line, 0)
                    if PARALLEL > 1:
                        match = re.search(r'^\[SUM\]', line)
                        if BIDIRFLAG:
                            match = re.search(r'^\[SUM\]\[RX-C\]', line)
                    else:
                        match = re.search(r'^\[\s*\d+\]', line)
                        if BIDIRFLAG:
                            match = re.search(r'^\[SUM\]\[RX-C\]', line)
                        elif SERVERFLAG:
                            match = re.search(r'^\[SUM\]\[RX-S\]', line)
                        
                    if match:
                        # print('-->',line)
                        if 'connected' in line:
                            print('Just a connect notification!')
                            continue
                        mbits_per_sec = float(re.search(r'(\d+(\.\d+)?) Mbits/sec', line).group(1))
                        sec_gap = re.search(r'(\d+\.\d+-\d+\.\d+)', line).group(1).split('-')
                        current_tpt.set_text("Current: " + str(mbits_per_sec) + " Mbps")
                        sec_gap_check = float(sec_gap[1]) - float(sec_gap[0])
                        # print('-->', sec_gap_check)
                        if sec_gap_check < 3:
                            print('-->',mbits_per_sec)
                            x_vals.append(len(x_vals)+1)
                            y_vals.append(mbits_per_sec)
                            line = plt.plot(x_vals[-MAXPLOTVIEW:], y_vals[-MAXPLOTVIEW:], color=COLOR, linestyle=LINESTYLE, marker=MARKER, markerfacecolor=MARKERCOLOR, markersize=MARKERSIZE)
                            # print(y_vals[-MAXPLOTVIEW:])
                            plt.xlim(max(x_vals)-(MAXPLOTVIEW-1), max(x_vals))
                            # plt.ylim(0, 450)
                            plt.ylim((0, max(y_vals)*0.2+max(y_vals)))

                            fig.canvas.draw()
                            fig.canvas.flush_events()

                            l = line.pop(0)
                            l.remove()

                            output_log()
            rep_counter = rep_counter + 1
        else:
            break
    
def cmd_compose(iperf_cmd):
    iperf_cmd = iperf_cmd.split()  # Split the input into a list of command and arguments
    global TIMEOPTION
    global PARALLEL
    global BIDIRFLAG
    global SERVERFLAG

    for idx, arg in enumerate(iperf_cmd):
        # Handle cases like '-t 3'
        if re.match(r'^-t$', arg) or re.match(r'^--time$', arg):
            if idx + 1 < len(iperf_cmd):
                TIMEOPTION = int(iperf_cmd[idx + 1])
        # Handle cases like '-t3'
        if re.match(r'^-(t|--time)(\d+)$', arg):
            TIMEOPTION = int(arg[2:])
        # Handle cases like '-P 3'
        if re.match(r'^-P$', arg) or re.match(r'^--parallel$', arg):
            if idx + 1 < len(iperf_cmd):
                PARALLEL = int(iperf_cmd[idx + 1])
        # Handle cases like '-P3'
        if re.match(r'^-(P|--parallel)(\d+)$', arg):
            PARALLEL = int(arg[2:])
        # Handle cases like '--bidir'
        if re.match(r'^--bidir$', arg):
            BIDIRFLAG = 1    
        # Handle cases like '-s'
        if re.match(r'^-s$', arg):
            SERVERFLAG = 1   

    print("Time option value:", TIMEOPTION)
    print("Parallel option value:", PARALLEL)

    iperf_cmd.append('--forceflush')  # Add the --forceflush flag
    iperf_cmd.append('-fm')  # Add the --forceflush flag

    return iperf_cmd

if __name__ == '__main__':
    #iperf_input = input("Enter the iPerf command: ")
    print(CMD)
    iperf_cmd = cmd_compose(CMD)

    output_iperf_console_log(CMD,1)

    print('Starting datetime:', datetime.datetime.now())
    run_iperf(iperf_cmd)

    signal.signal(signal.SIGINT, signal_handler)
    print("Press Ctrl + C to end the program.")
    while True:
        try:
            time.sleep(5)  # Keep the program running
        except KeyboardInterrupt:
            pass  # Ignore Ctrl + C so the program keeps running
