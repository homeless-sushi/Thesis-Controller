import utils

import argparse
import collections
import csv
import os
import sys

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

benchmark_name = ""
 
def setup_arg_parse() :

    parser = argparse.ArgumentParser(
        prog='Plot Interference',
        description=
            'This program reads a benchmark\'s info and average/estimated '
            'throughputs, and plots the results.\n',
        usage=f'{sys.argv[0]} benchmark'
    )

    parser.add_argument(
        "benchmark",
        type=str,
        help="the benchmark's name"
    )

    return parser


def plot_ratio(ns, no_interference_dict, interference_dict) :

    # Generate data
    x_ratios = []
    for n1 in ns :
        row = []

        for n2 in ns :
            row.append(interference_dict[n1][n2]['x']/no_interference_dict[n1]['x'])

        x_ratios.append(row)
    x_ratios = np.array(x_ratios)

    fig, ax = plt.subplots()
    im = ax.imshow(x_ratios, vmin=0.0, vmax=1.0)

    # Show all ticks and label them with the respective list entries
    ax.set_xticks(
        np.arange(len(ns)),
        labels=[f"B: {n} ({no_interference_dict[n]['p']}%)" for n in ns]
    )
    ax.set_yticks(
        np.arange(len(ns)),
        labels=[f"A: {n} ({no_interference_dict[n]['p']}%)" for n in ns]
    )

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(),
        rotation=45, ha="right",rotation_mode="anchor"
    )
    
    # Color bar
    ax.figure.colorbar(im, ax=ax)

    # Loop over data dimensions and create text annotations.
    textcolors = ["black", "white"]
    for i in range(len(ns)):
        for j in range(len(ns)):
            ax.text(
                j, i, f"{x_ratios[i,j]:.2f}",
                ha="center", va="center", 
                color=textcolors[int(x_ratios[i, j] < 0.5)])

    ax.set_title(f"{benchmark_name.upper()}: GPU Interference")
    fig.tight_layout()
    plt.show()


def plot_difference(ns, interference_dict, estimated_dict) :

    # Generate data
    relative_errors = []
    for n1 in ns :
        row = []

        for n2 in ns :
            estimate = estimated_dict[n1][n2]['x']
            actual = interference_dict[n1][n2]['x']
            relative_error = (estimate-actual)/actual
            row.append(relative_error)

        relative_errors.append(row)
    relative_errors = np.array(relative_errors)

    fig, ax = plt.subplots()
    im = ax.imshow(relative_errors, vmin=-1.0, vmax=1.0,cmap=mpl.colormaps["bwr"])

    # Show all ticks and label them with the respective list entries
    ax.set_xticks(
        np.arange(len(ns)),
        labels=[f"B: {n} ({interference_dict[n][n]['p1']}%)" for n in ns]
    )
    ax.set_yticks(
        np.arange(len(ns)),
        labels=[f"A: {n} ({interference_dict[n][n]['p1']}%)" for n in ns]
    )

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(),
        rotation=45, ha="right",rotation_mode="anchor"
    )
    
    # Color bar
    ax.figure.colorbar(im, ax=ax)

    # Loop over data dimensions and create text annotations.
    textcolors = ["black", "white"]
    for i in range(len(ns)):
        for j in range(len(ns)):
            ax.text(
                j, i, f"{relative_errors[i,j]:.2f}",
                ha="center", va="center", 
                color=textcolors[int(abs(relative_errors[i, j]) > 0.5)])

    ax.set_title(f"{benchmark_name.upper()}: Prediction Relative Error")
    fig.tight_layout()
    plt.show()


def main() : 

    # Setup argument parser and parse 
    parser = setup_arg_parse()
    args = parser.parse_args()
    global benchmark_name
    benchmark_name = args.benchmark.lower()

    no_interference_url = utils.get_no_interference_url(benchmark_name)
    no_interference_data = None
    with open(no_interference_url, "r") as data_file :
        no_interference_data = csv.reader(data_file)
        next(no_interference_data, None)
        no_interference_data = list(no_interference_data)

    ns = [n for n, _, _ in no_interference_data]

    no_interference_dict = collections.defaultdict(dict)
    for n, p, x in no_interference_data :
        no_interference_dict[n] = {'p': float(p), 'x': float(x)}

    interference_url = utils.get_interference_url(benchmark_name)
    interference_data = None
    with open(interference_url, "r") as data_file :
        interference_data = csv.reader(data_file)
        next(interference_data, None)
        interference_data = list(interference_data)

    interference_dict = collections.defaultdict(dict)
    for n1, p1, n2, p2, x in interference_data :
        interference_dict[n1][n2] = {'p1': float(p1), 'p2': float(p2), 'x': float(x)}

    plot_ratio(ns, no_interference_dict, interference_dict)

    estimated_url = utils.get_estimated_interference_url(benchmark_name)
    estimated_data = None
    with open(estimated_url, "r") as data_file :
        estimated_data = csv.reader(data_file)
        next(estimated_data, None)
        estimated_data = list(estimated_data)

    estimated_dict = collections.defaultdict(dict)
    for n1, p1, n2, p2, x in estimated_data :
        estimated_dict[n1][n2] = {'p1': float(p1), 'p2': float(p2), 'x': float(x)}

    plot_ratio(ns, no_interference_dict, estimated_dict)

    plot_difference(ns, interference_dict, estimated_dict)

if __name__ == '__main__' :
    main()
