import argparse
import os
import string
import sys

import pandas as pd

import matplotlib as mpl
import matplotlib.pyplot as plt

def setup_arg_parse() :

    parser = argparse.ArgumentParser(
        prog='Plot Throughput',
        description=
            'This program reads a controller and power log, '
            'and plots power and utilisations.\n',
        usage=f'{sys.argv[0]} in_folder_url --utilisation'
    )

    parser.add_argument(
        "in_folder_url",
        type=str,
        help="the folder containing the run's logs url"
    )

    parser.add_argument(
        '--utilisations',
        action='store_true', 
        help='plot utilisations'
    )

    return parser


def predict_cpu_power(us):
    idle_power = 123.6
    max_powers = [
        948.9580324308162, 
        819.0535814371926, 
        789.5708446924566, 
        824.9241895871996
    ]
    w = idle_power + sum(max_powers[i]*us[i]/100 for i in range(len(us)))
    return w


def main() :

    # Setup argument parser and parse 
    parser = setup_arg_parse()
    args = parser.parse_args()

    schedule_name = os.path.basename(args.in_folder_url)

    controller_csv = os.path.join(args.in_folder_url, "controller.csv")
    controller_df = pd.read_csv(controller_csv)
    power_csv = os.path.join(args.in_folder_url, "power.csv")
    power_df = pd.read_csv(power_csv)

    start_cycle = controller_df["CYCLE"].min()
    end_cycle = controller_df["CYCLE"].max()

    # app_infos = []
    # names = [name.upper() for name in schedule_name.split('_')]
    # for i in range(0,3) :
        # app_df = controller_df.loc[
            # controller_df["NAME" == f"APP{i+1}"] & controller_df["CURRENT" != 0]
        # ]
# 
        # xs = app_df["CYCLE"].values.tolist()
        # xs = [*range(start_cycle, xs[0])] + xs + [*range(xs[-1], end_cycle)]
        # ys = [0]*(xs[0] - start_cycle) + app_df["CURRENT"].values.tolist() + [0]*(end_cycle - xs[-1])
        # app_info = {
            # "name": names[i],
            # "multiplier": 0.25*(i+1),
            # "target" : app_df["CYCLE"].iloc[0],
            # "xs" : xs,
            # "ys" : ys
        # }
        # app_infos.append(app_info)

    power_df = power_df[
        (power_df["CYCLE"] >= start_cycle) & (power_df["CYCLE"] <= end_cycle)
    ]

    utilisation_traces = []
    for i in range(0,4):
        utilisation_trace = {
            "name": f"Core {i} Utilisation",
            "ys": power_df[f"UTILIZATION_{i}"].values.tolist()
        }
        utilisation_traces.append(utilisation_trace)

    measured_power = {
        "name": "Measured CPU Power",
        "ys" : power_df["CPUW"].values.tolist()
    }

    #predicted_power_ys = power_df.apply(
    #    lambda row : predict_cpu_power([
    #       row["UTILIZATION_0"],
    #       row["UTILIZATION_1"],
    #       row["UTILIZATION_2"],
    #       row["UTILIZATION_3"]
    #    ]), axis=1).tolist()
    predicted_power = {
        "name" : "Predicted CPU Power",
        "ys" : [predict_cpu_power([0, 75, 50, 25])]*(end_cycle+1 - start_cycle)
    }


    if (args.utilisations) :
        fig, (ax1, ax2) = plt.subplots(2, 1)
    else :
        fig, ax1 = plt.subplots()

    ax1.set_title('Measured vs Predicted CPU Power')
    ax1.set_xlabel('Control Cycle (#)')
    ax1.set_ylabel('Power (mW)')
    max_power = max(measured_power["ys"] + predicted_power["ys"])
    min_power = min(measured_power["ys"] + predicted_power["ys"])
    avg_power = sum(measured_power["ys"])/len(measured_power["ys"])
    ax1.set_ylim(bottom=0, top=max_power*1.10)
    ax1.plot( # measured power
        range(start_cycle, end_cycle+1),
        measured_power["ys"],
        label=measured_power["name"],
        linestyle='solid',
        color='red'
    )
    ax1.plot( # measured power avg
        range(start_cycle, end_cycle+1),
        [sum(measured_power["ys"])/len(measured_power["ys"])]*(end_cycle+1 - start_cycle), 
        label="Average of " + measured_power["name"],
        linestyle='dashed',
        color='red'
    )
    ax1.plot( 
        range(start_cycle, end_cycle+1),
        predicted_power["ys"],
        #[sum(predicted_power["ys"])/len(predicted_power["ys"])]*(end_cycle+1 - start_cycle),
        label=predicted_power["name"],
        linestyle='dashed',
        color='dodgerblue'
    )
    ax1.legend(
        loc='lower right'
    )

    if (args.utilisations) :
        ax2.set_title('Cores\' Utilisation')
        ax2.set_xlabel('Control Cycle (#)')
        ax2.set_ylabel('Utilisations (%)')
        ax2.set_ylim(bottom=0, top=110)
        ax2.set_yticks(range(0, 101, 10))
        colors = ['cyan','dodgerblue','blue','blueviolet']
        for utilisation_trace in utilisation_traces :
            current_color = colors.pop()
            ax2.plot(
                range(start_cycle, end_cycle+1),
                utilisation_trace["ys"], 
                label = utilisation_trace["name"],
                color = current_color
            )
        ax2.legend(
            loc='upper right'
        )

    plt.tight_layout()

    if (args.utilisations) :
        fig.set_figheight(8)
        fig.set_figwidth(12)
        out_file = os.path.join(args.in_folder_url, "power_utilisation.pdf")
        fig.savefig(out_file)
    else :
        fig.set_figheight(4)
        fig.set_figwidth(8)
        out_file = os.path.join(args.in_folder_url, "power.pdf")
        fig.savefig(out_file)

    #plt.show()
    #plt.close()

    print(f"MAX: {max_power}")
    print(f"MIN: {min_power}")
    print(f"AVG: {avg_power}")
    print(f"PREDICTIED: {predicted_power['ys'][0]}")

if __name__ == "__main__" :
    main()