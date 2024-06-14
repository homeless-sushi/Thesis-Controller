import argparse
import os
import sys

import numpy as np
import pandas as pd

import matplotlib as mpl
import matplotlib.pyplot as plt

# Log file names
CONTROLLER_FILE = "controller.csv"
POWER_FILE = "power.csv"

# CSV fields
CYCLE = "CYCLE"

## Controller
PID = "PID"
NAME = "NAME"
APP = "APP"
INPUT_SIZE = "INPUT_SIZE"
GPU = "GPU"
N_CORES = "N_CORES"
TARGET_THR = "TARGET_THR"
CURRENT_THR = "CURRENT_THR"
MIN_PRECISION = "MIN_PRECISION"
CURR_PRECISION = "CURR_PRECISION"

## Power
UTILIZATION_ = "UTILIZATION"
CPUFREQ = "CPUFREQ"
GPUFREQ = "GPUFREQ"
SOCW = "SOCW"
CPUW = "CPUW"
GPUW = "GPUW"

# App colors
COLOR = "COLOR"
app_colors = ['cyan', 'blue', 'deepskyblue', 'blueviolet']
edge_colors = ['turquoise', 'darkblue', 'dodgerblue', 'purple']

# Approximate 
APPROXIMATE = "APPROXIMATE"

# Lower bound for throughput
LOWER_BOUND = "LOWER_BOUND"
EDGE_COLOR = "EDGE_COLOR"

# CPU Freqs
cpu_freqs = [102000, 204000, 307200, 403200, 518400, 614400, 710400, 825600, 921600, 1036800, 1132800, 1224000, 1326000, 1428000, 1479000]
# GPU Freqs
gpu_freqs = [76800000, 153600000, 230400000, 307200000, 384000000, 460800000, 537600000, 614400000, 691200000, 768000000, 844800000, 921600000]

def setup_arg_parse() :

    parser = argparse.ArgumentParser(
        prog='Plot Throughput',
        description=
            'This program reads the controller and power logs, and plots them.',
        usage=f'{sys.argv[0]} in_dir_url out_url'
    )

    parser.add_argument(
        "in_dir_url",
        type=str,
        help="the controller and power logs dir url"
    )

    parser.add_argument(
        "out_url",
        type=str,
        help="the output plot's url"
    )

    return parser

def main() :

    # Setup argument parser and parse 
    parser = setup_arg_parse()
    args = parser.parse_args()

    # input files
    controller_url = os.path.abspath(os.path.join(args.in_dir_url,CONTROLLER_FILE))
    power_url = os.path.abspath(os.path.join(args.in_dir_url,POWER_FILE))

    # DFs
    controller_df = pd.read_csv(controller_url)
    power_df = pd.read_csv(power_url)

    # Trim the DFs
    run_first_cycle = max(power_df[CYCLE].iloc[0], controller_df[CYCLE].iloc[0]-1)
    run_last_cycle = min(power_df[CYCLE].iloc[-1], controller_df[CYCLE].iloc[-1]+1)-run_first_cycle
    controller_df[CYCLE] = controller_df[CYCLE] - run_first_cycle
    controller_df = controller_df[controller_df[CYCLE] >= 0]
    power_df[CYCLE] = power_df[CYCLE] - run_first_cycle
    power_df = power_df[power_df[CYCLE] >= 0]

    # App traces
    apps_pids = controller_df[PID].unique()

    app_traces = []
    for pid in apps_pids :
        app_df = controller_df[controller_df[PID] == pid]
        app_traces.append(
            {
                PID: app_df[PID].iloc[0],
                NAME: app_df[NAME].iloc[0],
                APP: app_df[APP].iloc[0],
                INPUT_SIZE: app_df[INPUT_SIZE].iloc[0],
                CYCLE: app_df[CYCLE].tolist(),
                GPU: app_df[GPU].tolist(),
                N_CORES: app_df[N_CORES].tolist(),
                TARGET_THR: app_df[TARGET_THR].tolist(),
                LOWER_BOUND: [y*0.95 for y in app_df[TARGET_THR].tolist()],
                CURRENT_THR: app_df[CURRENT_THR].tolist(),
                MIN_PRECISION: app_df[MIN_PRECISION].tolist(),
                CURR_PRECISION: app_df[CURR_PRECISION].tolist(),

                COLOR: app_colors.pop(),
                EDGE_COLOR: edge_colors.pop(),
                APPROXIMATE: True     
            }
        )

    # Check if the app is approximate
    for app_trace in app_traces :
        app_trace[APPROXIMATE] = not (
            all(precision == 100 for precision in app_trace[CURR_PRECISION]) and
            all(precision == 100 for precision in app_trace[MIN_PRECISION])
        )

    # Pad app traces
    for app_trace in app_traces :

        app_first_cycle = app_trace[CYCLE][0]
        app_last_cycle = app_trace[CYCLE][-1]
        start_cycle_pad = [*range(0, app_first_cycle)]
        end_cycle_pad = [*range(app_last_cycle+1, run_last_cycle+1)]
        app_trace[CYCLE] = start_cycle_pad + app_trace[CYCLE] + end_cycle_pad

        start_pad = [0] * len(start_cycle_pad)
        end_pad = [0] * len(end_cycle_pad)
        app_trace[N_CORES] = start_pad + app_trace[N_CORES] + end_pad
        app_trace[GPU] = start_pad + app_trace[GPU] + end_pad
        app_trace[TARGET_THR] = start_pad + app_trace[TARGET_THR] + end_pad
        app_trace[CURRENT_THR] = start_pad + app_trace[CURRENT_THR] + end_pad
        app_trace[LOWER_BOUND] = start_pad + app_trace[LOWER_BOUND] + end_pad
        app_trace[MIN_PRECISION] = start_pad + app_trace[MIN_PRECISION] + end_pad
        app_trace[CURR_PRECISION] = start_pad + app_trace[CURR_PRECISION] + end_pad

    # Figure
    fig, axs = plt.subplots(3,2)
    throughput_ax = axs[0, 0]
    precision_ax = axs[0, 1]
    resources_ax = axs[1, 0]
    fig.delaxes(axs[1,1])
    power_ax = axs[2, 0]
    freq_ax = axs[2, 1]

    # Draw Throughput
    throughput_ax.set_title('Applications Throughput')
    throughput_ax.set_xlabel('Control Cycles')
    throughput_ax.set_ylabel('Throughput (#/s)')
    throughput_ax.set_facecolor('whitesmoke')
    throughput_ax.grid(True)
    for app_trace in app_traces :
        throughput_ax.plot(
            app_trace[CYCLE], 
            app_trace[TARGET_THR],
            linestyle= 'dashed',
            color= app_trace[COLOR], alpha=0.5
        )
        throughput_ax.plot(
            app_trace[CYCLE], 
            app_trace[LOWER_BOUND],
            linestyle= 'dashed',
            color= app_trace[COLOR], alpha=0.5
        )
        throughput_ax.fill_between(
            app_trace[CYCLE], 
            app_trace[TARGET_THR], app_trace[LOWER_BOUND],
            where=(np.array(app_trace[TARGET_THR]) >= np.array(app_trace[LOWER_BOUND])), 
            color= app_trace[COLOR], alpha=0.1, 
            #edgecolor=app_trace[EDGE_COLOR], linestyle='-', linewidth=2,
            label=f'{app_trace[APP]}[{app_trace[INPUT_SIZE]}] target'
        )

        throughput_ax.plot(
            app_trace[CYCLE], 
            app_trace[CURRENT_THR],
            label= f"{app_trace[APP]}[{app_trace[INPUT_SIZE]}]",
            color= app_trace[COLOR]
        )
    throughput_ax.tick_params(axis='both', which='both', labelsize=7)
    throughput_ax.set_ylim(bottom=0)
    throughput_ax.legend(loc="lower center",fontsize="xx-small",ncol=len(app_traces))

    # Are there approximate applications
    #draw_precision = False
    #for app_trace in app_traces :
    #    if app_trace[APPROXIMATE] :
    #        draw_precision = True
    #        break
    
    # Draw Precision
    #if draw_precision :
    #    precision_ax.set_title('Applications Precision')
    #    precision_ax.set_xlabel('Control Cycles')
    #    precision_ax.set_ylabel('Precision (#/s)')
    #    precision_ax.set_facecolor('whitesmoke')
    #    precision_ax.grid(True)
    #    for app_trace in app_traces :
    #        if not app_trace[APPROXIMATE] :
    #            continue
    #        precision_ax.plot(
    #            app_trace[CYCLE], 
    #            app_trace[MIN_PRECISION],
    #            linestyle= 'dashed',
    #            label= f"{app_trace[APP]}[{app_trace[INPUT_SIZE]}] requested",
    #            color= app_trace[COLOR]
    #        )
    #        precision_ax.plot(
    #            app_trace[CYCLE], 
    #            app_trace[CURR_PRECISION],
    #            label= f"{app_trace[APP]}[{app_trace[INPUT_SIZE]}]",
    #            color= app_trace[COLOR]
    #        )
    #    precision_ax.set_yticks(range(0,101,10))
    #    precision_ax.set_ylim(bottom=0, top=110)
    #    precision_ax.legend(loc="lower center",fontsize="xx-small",ncol=len(app_traces))
    # Delete precision graph
    #else:
    #    fig.delaxes(axs[0, 1])

    # Draw Precision
    precision_ax.set_title('Applications Precision')
    precision_ax.set_xlabel('Control Cycles')
    precision_ax.set_ylabel('Precision (#/s)')
    precision_ax.set_facecolor('whitesmoke')
    precision_ax.grid(True)
    for app_trace in app_traces :
        precision_ax.plot(
            app_trace[CYCLE], 
            app_trace[MIN_PRECISION],
            linestyle= 'dashed',
            drawstyle='steps-post',
            label= f"{app_trace[APP]}[{app_trace[INPUT_SIZE]}] min",
            color= app_trace[COLOR]
        )
        precision_ax.plot(
            app_trace[CYCLE], 
            app_trace[CURR_PRECISION],
            drawstyle='steps-post',
            label= f"{app_trace[APP]}[{app_trace[INPUT_SIZE]}]",
            color= app_trace[COLOR]
        )
    precision_ax.set_yticks(range(0,101,10))
    precision_ax.tick_params(axis='both', which='both', labelsize=7)
    precision_ax.set_ylim(bottom=0, top=110)
    precision_ax.legend(loc="lower center",fontsize="xx-small",ncol=len(app_traces))

    # Draw Resources
    #resources_ax.set_title('Resources Allocation')
    #resources_ax.set_xlabel('Control Cycles')
    #resources_ax.set_ylabel('CPU Cores and GPU')
    #resources_ax.set_facecolor('whitesmoke')
    #resources_ax.grid(True)
    #cpu_accumulator = [0]*(run_last_cycle+1)
    #gpu_accumulator = [4]*(run_last_cycle+1)
    #for app_trace in app_traces :
    #    total_cpu_cores = [x+y if not (y == 0) else 0 for x,y in zip(cpu_accumulator, app_trace[N_CORES])]
    #    total_cpu_cores = np.ma.masked_where(np.array(total_cpu_cores) == 0, total_cpu_cores)
    #    resources_ax.plot(
    #        app_trace[CYCLE], 
    #        total_cpu_cores,
    #        linestyle= '-',
    #        drawstyle='steps-post',
    #        color= app_trace[COLOR],
    #        label=f'{app_trace[APP]}[{app_trace[INPUT_SIZE]}] cores',
    #    )
    #    resources_ax.fill_between(
    #        app_trace[CYCLE], 
    #        total_cpu_cores, cpu_accumulator,
    #        where=(np.array(total_cpu_cores) >= np.array(cpu_accumulator)),
    #        step='post',
    #        color= app_trace[COLOR], alpha=0.5, 
    #        #edgecolor=app_trace[EDGE_COLOR], linestyle='-', linewidth=2,
    #    )
    #    cpu_accumulator = [x+y for x,y in zip(cpu_accumulator, app_trace[N_CORES])]
    #
    #    total_gpu_apps = [x+y if not (y == 0) else 0 for x,y in zip(gpu_accumulator, app_trace[GPU])]
    #    total_gpu_apps = np.ma.masked_where(np.array(total_gpu_apps) == 0, total_gpu_apps)
    #    resources_ax.plot(
    #        app_trace[CYCLE], 
    #        total_gpu_apps,
    #        linestyle= '-',
    #        drawstyle='steps-post',
    #        color= app_trace[COLOR],
    #        label=f'{app_trace[APP]}[{app_trace[INPUT_SIZE]}] gpu'
    #    )
    #    resources_ax.fill_between(
    #        app_trace[CYCLE], 
    #        total_gpu_apps, gpu_accumulator,
    #        where=(np.array(total_gpu_apps) >= np.array(gpu_accumulator)), 
    #        step='post',
    #        color= app_trace[COLOR], alpha=0.5, 
    #        #edgecolor=app_trace[EDGE_COLOR], linestyle='-', linewidth=2,
    #    )
    #    gpu_accumulator = [x+y for x,y in zip(gpu_accumulator, app_trace[GPU])]
    #resources_ax.set_yticks(
    #    range(0,7,1), 
    #    labels=([""]+[f"CPU core #{i}" for i in range(1,5)] + [f"GPU slot #{i}" for i in range(1,3)]),
    #)
    #resources_ax.tick_params(axis='y', which='both', labelsize=7)
    #resources_ax.set_ylim(bottom=0, top=7)
    #resources_ax.legend(loc="lower center",fontsize="xx-small",ncols=len(app_traces))

    # Draw Resources
    resources_ax.set_title('Resources Allocation')
    resources_ax.set_xlabel('Control Cycles')
    resources_ax.set_ylabel('CPU Cores and GPU slots')
    data = np.zeros((6, run_last_cycle+1))
    cpu_accumulator = [0]*(run_last_cycle+1)
    gpu_accumulator = [4]*(run_last_cycle+1)
    pid_colors = ['whitesmoke']
    pid_bounds = [-0.5, 0.5]
    for app_trace in app_traces :
        for col, (n_cores, start_core) in enumerate(zip(app_trace[N_CORES], cpu_accumulator)):
            for row_increment in range(n_cores) :
                data[start_core+row_increment,col] = app_trace[PID]
        cpu_accumulator = [x+y for x,y in zip(cpu_accumulator, app_trace[N_CORES])]

        for col, (n_slot, start_slot) in enumerate(zip(app_trace[GPU], gpu_accumulator)):
            for row_increment in range(n_slot) :
                data[start_slot+row_increment,col] = app_trace[PID]
        gpu_accumulator = [x+y for x,y in zip(gpu_accumulator, app_trace[GPU])]

        pid_colors.append(app_trace[COLOR])
        pid_bounds.append(app_trace[PID]+0.5)
    cmap = mpl.colors.ListedColormap(pid_colors)
    norm = mpl.colors.BoundaryNorm(pid_bounds, cmap.N)
    resource_cax = resources_ax.imshow(data, aspect='auto', cmap=cmap, norm=norm, interpolation='nearest')
    resources_ax.set_yticks(
        np.arange(data.shape[0]),
        labels=[f"CPU core #{i}" for i in range(1,5)] + [f"GPU slot #{i}" for i in range(1,3)]
    )
    resources_ax.tick_params(axis='both', which='both', labelsize=7)
    #resources_ax.set_yticklabels(
    #    [f"CPU core #{i}" for i in range(1,5)] + [f"GPU slot #{i}" for i in range(1,3)]
    #)


    #resources_ax.set_yticks(
    #    range(0,7,1), 
    #    labels=([""]+[f"CPU core #{i}" for i in range(1,5)] + [f"GPU slot #{i}" for i in range(1,3)]),
    #)
    #resources_ax.tick_params(axis='y', which='both', labelsize=7)
    #resources_ax.set_ylim(bottom=0, top=7)
    #resources_ax.legend(loc="lower center",fontsize="xx-small",ncols=len(app_traces))

    # Draw Power
    power_ax.set_title('Power Draw')
    power_ax.set_xlabel('Control Cycles')
    power_ax.set_ylabel('Power (mW)')
    power_ax.set_facecolor('whitesmoke')
    power_ax.grid(True)
    power_ax.plot(
        power_df[CYCLE], 
        [2600] * len(power_df[CYCLE]),
        linestyle= 'dashed',
        label= f"Max Power",
        color='firebrick'
    )
    power_ax.plot(
        power_df[CYCLE], 
        power_df.apply(lambda row: row[CPUW] + row[GPUW], axis=1).tolist(),
        label= f"Power Draw",
        color='red'
    )
    power_ax.tick_params(axis='both', which='both', labelsize=7)
    power_ax.set_ylim(bottom=0)
    power_ax.legend(loc="lower center",fontsize="small")

    # Draw Frequency
    freq_ax.set_title('CPU and GPU Frequency')
    freq_ax.set_xlabel('Control Cycles')
    freq_ax.set_facecolor('whitesmoke')
    cpu_freq_ax = freq_ax
    gpu_freq_ax = freq_ax.twinx()

    cpu_freq_ax.set_ylabel('CPU Freq (KHz)', color='blue')
    cpu_freq_ax.plot(
        power_df[CYCLE], 
        power_df[CPUFREQ],
        label= f"CPU Freq",
        drawstyle='steps-post',
        color='blue'
    )
    cpu_freq_ax.set_yticks(cpu_freqs)
    for used_cpu_freq in power_df[CPUFREQ].unique():
        cpu_freq_ax.axhline(y=used_cpu_freq, color='gray', linestyle='-', linewidth=0.5)
    cpu_freq_ax.tick_params(axis='y', which='both', labelsize=7, labelcolor='blue')
    cpu_freq_ax.tick_params(axis='x', which='both', labelsize=7)
    cpu_freq_ax.set_ylim(bottom=cpu_freqs[0], top=cpu_freqs[-1]*1.05)
    cpu_freq_ax.legend(loc="upper left",fontsize="small")

    gpu_freq_ax.set_ylabel('GPU Freq (Hz)', color='lime')
    gpu_freq_ax.plot(
        power_df[CYCLE], 
        power_df[GPUFREQ],
        label= f"GPU Freq",
        drawstyle='steps-post',
        color='lime'
    )
    gpu_freq_ax.set_yticks(gpu_freqs)
    for used_gpu_freq in power_df[GPUFREQ].unique():
        gpu_freq_ax.axhline(y=used_gpu_freq, color='gray', linestyle='-', linewidth=0.5)
    gpu_freq_ax.tick_params(axis='y', which='both', labelsize=7, labelcolor='lime')
    gpu_freq_ax.set_ylim(bottom=gpu_freqs[0], top=gpu_freqs[-1]*1.05)
    gpu_freq_ax.legend(loc="upper right",fontsize="small")

    #plt.savefig(args.out_plot_url)
    plt.subplots_adjust(hspace=0.455, wspace=0.3)
    #plt.tight_layout()
    plt.show()
    plt.close()

if __name__ == "__main__" :
    main()