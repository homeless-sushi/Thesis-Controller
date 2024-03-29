import argparse
import sys

import pandas as pd

import matplotlib as mpl
import matplotlib.pyplot as plt

def setup_arg_parse() :

    parser = argparse.ArgumentParser(
        prog='Plot Throughput',
        description=
            'This program reads a controller log, and plots it.\n'
            'The controller log is a .csv file with the header:\n'
            'CYCLE,PID,NAME,TARGET,CURRENT',
        usage=f'{sys.argv[0]} log_in_url out_plot_url'
    )

    parser.add_argument(
        "log_in_url",
        type=str,
        help="the controller's log's url"
    )

    parser.add_argument(
        "out_plot_url",
        type=str,
        help="the output plot's url"
    )

    return parser

def main() :

    # Setup argument parser and parse 
    parser = setup_arg_parse()
    args = parser.parse_args()
    
    traces = pd.read_csv(args.log_in_url)

    traces["CYCLE"] = traces["CYCLE"] - traces["CYCLE"].min()
    run_last_cycle = traces["CYCLE"].max()
    apps_pids = traces["PID"].unique()

    app_traces = []
    for pid in apps_pids :
        app_trace = traces[traces["PID"] == pid]
        app_traces.append(
            {
                "PID": app_trace["PID"].iloc[0],
                "NAME": app_trace["NAME"].iloc[0],
                "CYCLE": app_trace["CYCLE"].values.tolist(),
                "TARGET": app_trace["TARGET"].values.tolist(),
                "CURRENT": app_trace["CURRENT"].values.tolist()            
            }
        )

    for app_trace in app_traces :

        first_cycle = app_trace["CYCLE"][0]
        last_cycle = app_trace["CYCLE"][-1]
        start_cycle_pad = [*range(0, first_cycle)]
        end_cycle_pad = [*range(last_cycle+1, run_last_cycle+1)]
        app_trace["CYCLE"] = start_cycle_pad + app_trace["CYCLE"] + end_cycle_pad

        start_throughput_pad = [0] * len(start_cycle_pad)
        end_throughput_pad = [0] * len(end_cycle_pad)
        app_trace["CURRENT"] = start_throughput_pad + app_trace["CURRENT"] + end_throughput_pad

        start_throughput_pad = [0] * len(start_cycle_pad)
        end_throughput_pad = [0] * len(end_cycle_pad)
        app_trace["TARGET"] = start_throughput_pad + app_trace["TARGET"] + end_throughput_pad

    tot_ticks = [0] * (run_last_cycle+1)
    for i in range(0, len(tot_ticks)) :
        for app_trace in app_traces :
            tot_ticks[i] += app_trace["CURRENT"][i]

    fig, ax = plt.subplots()
    ax.set_xlabel('Control Cycles')
    ax.set_ylabel('Throughput')
    ax.set_title('Applications Throughput Performance')

    colors = ['b','g','r','c','m','y']
    for app_trace in app_traces :
        current_color = colors.pop()
        ax.plot(
            app_trace["CYCLE"], 
            app_trace["TARGET"],
            linestyle= 'dashed',
            label= " ".join([app_trace["NAME"],"TARGET"]),
            color= current_color
        )
    
        ax.plot(
            app_trace["CYCLE"], 
            app_trace["CURRENT"],
            label= " ".join([app_trace["NAME"],"CURRENT"]),
            color= current_color
        )

    ax.plot(
        range(len(tot_ticks)), 
        tot_ticks,
        label= "TOTAL PERFORMANCE",
        color= "k",
        alpha=0.5
    )

    ax.set_ylim(bottom=0)
    ax.legend()
    plt.savefig(args.out_plot_url)
    plt.show()
    plt.close()

if __name__ == "__main__" :
    main()