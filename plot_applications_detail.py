import argparse
import os
import sys
import time

import pandas as pd
import matplotlib.pyplot as plt

# csv field and keywords
EVENT = 'EVENT'
TYPE = 'TYPE'
DEVICE = 'DEVICE'
TIMESTAMP = 'TIMESTAMP'

## computed
DURATION = 'DURATION'

## event types
START = 'START'
STOP = 'STOP'
## devices types
CPU = 'CPU'
GPU = 'GPU'

class Bar :
    name = ''
    y = 0
    xs = []
    colors = []

    def device_to_color(self, device) :

        DEVICE_TO_COLOR = {
            CPU: 'tab:blue',
            GPU: 'tab:green'
        }

        return DEVICE_TO_COLOR[device]



def setup_arg_parse() :

    parser = argparse.ArgumentParser(
        prog='Plot Applications Detail',
        description=
            'This program reads a series of application logs and plots them;\n'
            'The application logs are csv\'s, with the following format:\n\n'
            'EVENT,TYPE,DEVICE,TIMESTAMP',
        usage=f'{sys.argv[0]} out_plot_URL details_URL+'
    )

    parser.add_argument(
        "out_plot_URL",
        type=str,
        help="URL for the plot output"
    )

    parser.add_argument(
        "detail_URLs",
        type=str,
        nargs="+",
        help="A list of application logs in .csv format"
    )

    return parser

def main() :

    # Setup argument parser and parse 
    parser = setup_arg_parse()
    args = parser.parse_args()

    # Read details
    detail_dfs = []
    for detail_URL in args.detail_URLs :
        detail_dfs.append(pd.read_csv(detail_URL))

    # Find min and max times
    min_time = detail_dfs[0][TIMESTAMP].iat[0]
    max_time = detail_dfs[0][TIMESTAMP].iat[-1]
    for detail_df in detail_dfs :
        detail_min_time = detail_df[TIMESTAMP].iat[0]
        detail_max_time = detail_df[TIMESTAMP].iat[-1]
        min_time = detail_min_time if (min_time > detail_min_time) else min_time
        max_time = detail_max_time if (max_time > detail_max_time) else max_time

    # Change format so it can be represented
    n_details = len(args.detail_URLs)
    bars = [Bar() for i in range(n_details)]

    for i in range(n_details) :

        bar = bars[i]
        detail_df = detail_dfs[i]

        # Name
        bar.name = (os.path.splitext(os.path.basename(args.detail_URLs[i]))[0])

        # Compute durations
        start = detail_df[detail_df[TYPE] == START]
        stop = detail_df[detail_df[TYPE] == STOP]
        start[DURATION] = stop[TIMESTAMP].values - start[TIMESTAMP].values
        bar.xs = list(map(tuple, start[[TIMESTAMP,DURATION]].values))

        # Colors
        bar.colors = (list(map(bar.device_to_color, start[DEVICE].values)))
    
    # Plot
    fig, ax = plt.subplots()

    ## y information
    yPadding = 10
    yMin = 0
    yMax = len(args.detail_URLs)*2*yPadding + yPadding
    ax.set_ylim(yMin, yMax)

    for i in range(n_details) :
        bar = bars[i]
        bar.y = i*2*yPadding + 1*yPadding

    ax.set_yticks(
        [bar.y+0.5*yPadding for bar in bars],
        labels=[bar.name for bar in bars]
    )

    ax.set_ylabel('Apps')

    # x information
    for i in range(n_details) :
        bar = bars[i]
        ax.broken_barh(bar.xs,
            (bar.y, yPadding),
            facecolors = bar.colors
        )
    
    ax.set_xlabel('Time')

    ax.grid(True)
    plt.show()

if __name__ == "__main__" :
    main()