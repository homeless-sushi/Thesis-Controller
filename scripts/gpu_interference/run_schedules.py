import utils

import argparse
import csv
import os
import sys

def setup_arg_parse() :

    parser = argparse.ArgumentParser(
        prog='Run Schedules',
        description=
            'This program reads a benchmark\'s info and runs all the '
            'schedules generated to measure GPU interference.\n'
            'The schedules are read from the project\'s schedules folder '
            'under BENCHMARK_inferference.\n',
        usage=f'{sys.argv[0]} benchmark'
    )

    parser.add_argument(
        "benchmark",
        type=str,
        help="the benchmark's name"
    )

    return parser


def run_schedule(schedule) :
    os.system(
        f"sudo python3.8 "
        f"{utils.RUN_SCHEDULE_URL} {schedule}"
    )


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
    
    for t1, _, _ in data :
        for t2, _, _ in data :

            schedule_name = utils.get_benchmark_schedule_name(
                benchmark_name,
                t1,
                t2
            )
            run_schedule(os.path.join(
                benchmark_interference_name,
                schedule_name
            ))

    for t, _, _ in data :

        schedule_name = utils.get_benchmark_schedule_name(
            benchmark_name,
            t1,
            t2
        )
        run_schedule(os.path.join(
            benchmark_interference_name,
            schedule_name
        ))
    
    benchmark_interference_dir = os.path.join(
        utils.RUN_DATA_DIR,
        benchmark_interference_name
    )
    os.system(f"sudo chown -R miele {benchmark_interference_dir}")


if __name__ == "__main__" :
    main()
