import subprocess
import re
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import datetime
import time
import signal
import configparser

config = configparser.ConfigParser()
config.read_file(open(r'config.txt'))

TIMEOPTION = 10
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
    graph_history_file = "graph_history.log"

    with open(graph_history_file, "w") as file:
        file.write("X values:\n")
        file.write(str(x_vals))

        file.write("\nY values:\n")
        file.write(str(y_vals))

def output_iperf_console_log(console_log_line, fresh_start):
    iperf_console_file = "iperf_console.log"

    if fresh_start:
        with open(iperf_console_file, "w") as file:
            file.write(console_log_line + '\n')
    else:
        with open(iperf_console_file, "a") as file:
            file.write(console_log_line)

def run_iperf(iperf_cmd):
    start_time = str(datetime.datetime.now())
    output_iperf_console_log(start_time+'\n', 0)

    global MAXPLOTVIEW
    global x_vals
    global y_vals

    rep_counter = 1
    plt.figure(figsize=(HPLOTSIZE,VPLOTSIZE))

    plt.xlabel('Time (intervals)')
    plt.ylabel('Mbits/sec')
    plt.title('iPerf Results')
    plt.grid(True)

    plt.annotate('Start Datetime:', xy = (0, 1.03), xycoords='axes fraction', fontsize=7)
    plt.annotate(start_time, xy = (0, 1), xycoords='axes fraction', fontsize=7)
    at_rep = plt.annotate(rep_counter, xy = (0.9, 1.03), xycoords='axes fraction', fontsize=7)

    fig = plt.gcf()
    fig.show()
    while True:
        # print(rep_counter)
        if rep_counter <= REPEAT  or REPEAT == -1:
            signal.signal(signal.SIGINT, signal_handler)
            with subprocess.Popen(iperf_cmd, stdout=subprocess.PIPE, universal_newlines=True) as proc:
                match_counter = 1
                at_rep.set_text(rep_counter)
                for line in proc.stdout:
                    print(line, end='')
                    output_iperf_console_log(line, 0)
                    match = re.search(r'\[SUM\].*? (\d+(\.\d+)?) Mbits/sec', line)
                    if match:
                        if match_counter <= TIMEOPTION:
                            # print(match_counter)
                            mbits_per_sec = float(match.group(1))
                            x_vals.append(len(x_vals)+1)
                            y_vals.append(mbits_per_sec)
                            line = plt.plot(x_vals[-MAXPLOTVIEW:], y_vals[-MAXPLOTVIEW:], color=COLOR, linestyle=LINESTYLE, marker=MARKER, markerfacecolor=MARKERCOLOR, markersize=MARKERSIZE)

                            # print(y_vals[-MAXPLOTVIEW:])
                            plt.xlim(max(x_vals)-(MAXPLOTVIEW-1), max(x_vals))
                            plt.ylim((0, max(y_vals)+50))

                            fig.canvas.draw()
                            fig.canvas.flush_events()

                            l = line.pop(0)
                            l.remove()

                            output_log()
                            match_counter = match_counter + 1
                        else:
                            break
            rep_counter = rep_counter + 1
        else:
            break
    
def cmd_compose(iperf_cmd):
    iperf_cmd = iperf_cmd.split()  # Split the input into a list of command and arguments
    global TIMEOPTION
    for idx, arg in enumerate(iperf_cmd):
        # Handle cases like '-t 3'
        if re.match(r'^-t$', arg) or re.match(r'^--time$', arg):
            if idx + 1 < len(iperf_cmd):
                TIMEOPTION = int(iperf_cmd[idx + 1])
                # if re.match(r'^\d+$', TIMEOPTION):  # Check if the time option value is a digit
                #     break
        # Handle cases like '-t3'
        if re.match(r'^-(t|--time)(\d+)$', arg):
            TIMEOPTION = int(arg[2:])
            break

    print("Time option value:", TIMEOPTION)

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
            time.sleep(1)  # Keep the program running
        except KeyboardInterrupt:
            pass  # Ignore Ctrl + C so the program keeps running