import utils

import argparse
import csv
import os
import sys

import pandas as pd

def setup_arg_parse() :

    parser = argparse.ArgumentParser(
        prog='Compute Averages',
        description=
            'This program reads a benchmark\'s info and runs\' results '
            'and computes the average throughput to measure GPU interference.\n'
            'The results are read from the project\'s data folder '
            'under BENCHMARK_inferference.\n',
        usage=f'{sys.argv[0]} benchmark'
    )

    parser.add_argument(
        "benchmark",
        type=str,
        help="the benchmark's name"
    )

    return parser

def main() :

    # Setup argument parser and parse 
    parser = setup_arg_parse()
    args = parser.parse_args()
    benchmark_name = args.benchmark.lower()

    benchmark_data_url = utils.get_benchmark_data_url(benchmark_name)
    data = None
    with open(benchmark_data_url, "r") as data_file :
        data = csv.reader(data_file)
        next(data, None)
        data = list(data)
    
    benchmark_interference_name = utils.get_benchmark_interference_name(benchmark_name)
    solo = []
    for n, p, _ in data :

        schedule_name = utils.get_benchmark_schedule_name(
            benchmark_name,
            n
        )
        controller_log_url = utils.get_controller_log_url(
            benchmark_interference_name,
            schedule_name
        )
        df = pd.read_csv(controller_log_url)
        df = df[df["CURRENT"] != 0]
        average = df["CURRENT"].mean()
        solo.append((n, p, average))


    no_interference_url = utils.get_no_interference_url(benchmark_name)
    with open(no_interference_url, "w") as no_interfence_file :
        no_interfence_file.write("N,PERCENTAGE,THROUGHPUT\n")

        for n, p, throughput in solo :
            no_interfence_file.write(f"{n},{p},{throughput}\n") 

    benchmark_name_upper = benchmark_name.upper()
    interference = []
    for n1, p1, _ in data :
        for n2, p2, _ in data :

            schedule_name = utils.get_benchmark_schedule_name(
                benchmark_name,
                n1,
                n2
            )
            controller_log_url = utils.get_controller_log_url(
                benchmark_interference_name,
                schedule_name
            )
            df = pd.read_csv(controller_log_url)

            if n1 == n2 :
                instance_name = "FIRST"
            else :
                instance_name = f"{benchmark_name_upper}_{n1}"

            df = df[df["CURRENT"] != 0]
            average = df[df["NAME"] == instance_name]["CURRENT"].mean()
            interference.append((n1,p1,n2,p2,average))

    interference_url = utils.get_interference_url(benchmark_name)
    with open(interference_url, "w") as interference_file :
        interference_file.write("N,PERCENTAGE,WITH_N,WITH_PERCENTAGE,THROUGHPUT\n")
        
        for n1, p1, n2, p2, throughput in interference :
            interference_file.write(f"{n1},{p1},{n2},{p2},{throughput}\n") 

if __name__ == "__main__" :
    main()
