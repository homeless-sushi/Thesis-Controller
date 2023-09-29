import utils

import argparse
import csv
import os
import sys

RUN_FOR = 50
CONTROLLER_DELAY = 2

def setup_arg_parse() :

    parser = argparse.ArgumentParser(
        prog='Schedules Gen',
        description=
            'This program reads a benchmark\'s info and generates '
            'schedules to measure GPU interference.\n'
            'The schedules are written in the project\'s schedules folder '
            'under BENCHMARK_inferference.\n',
        usage=f'{sys.argv[0]} benchmark'
    )

    parser.add_argument(
        "benchmark",
        type=str,
        help="the benchmark's name"
    )

    return parser


def get_schedule_header() :
    return "BENCHMARK,TYPE,INSTANCE_NAME,START_TIME,INPUT,OUTPUT,THROUGHPUT,APPEND\n"


def get_controller_start_line(controller_log_url) :
    #controller_log = os.path.join(utils.RUN_DATA_DIR, schedule_name, "controller.csv")
    return f"CONTROLLER,GPU_INTERFERENCE,,0,,,,--controller-log {controller_log_url}\n"


def get_controller_terminate_line(time) :
    return f"TERMINATE,,CONTROLLER,{time},,,,\n"


def get_instance_terminate_line(instance,time) :
    return f"TERMINATE,,{instance},{time},,,,\n"


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
    benchmark_interference_dir = os.path.join(
        utils.SCHEDULES_DIR,
        benchmark_interference_name
    )
    os.makedirs(benchmark_interference_dir, exist_ok=True)

    benchmark_name_upper = benchmark_name.upper()
    benchmarks_funcs = utils.import_benchmark_funcs(benchmark_name)
    for t1, _, target1 in data :
        for t2, _, target2 in data :
            
            if t1 != t2 :
                instance1_name = f"{benchmark_name_upper}_{t1}"
                instance2_name = f"{benchmark_name_upper}_{t2}"
            else :
                instance1_name = "FIRST"
                instance2_name = "SECOND"

            schedule_name = utils.get_benchmark_schedule_name(
                benchmark_name,
                t1,
                t2
            )
            schedule_url = os.path.join(
                benchmark_interference_dir,
                schedule_name+".csv"
            )
            controller_log_url = utils.get_controller_log_url(
                benchmark_interference_name,
                schedule_name
            )
            with open(schedule_url, "w") as schedule_file :
                schedule_file.write(get_schedule_header())
                schedule_file.write(get_controller_start_line(controller_log_url))
                schedule_file.write(benchmarks_funcs.get_instance_start_line(instance1_name,CONTROLLER_DELAY,t1,target1))
                schedule_file.write(benchmarks_funcs.get_instance_start_line(instance2_name,CONTROLLER_DELAY,t2,target2))
                schedule_file.write(get_instance_terminate_line(instance1_name,CONTROLLER_DELAY+RUN_FOR))
                schedule_file.write(get_instance_terminate_line(instance2_name,CONTROLLER_DELAY+RUN_FOR))
                schedule_file.write(get_controller_terminate_line(CONTROLLER_DELAY+RUN_FOR+CONTROLLER_DELAY))

    for t, _, target in data :

        instance_name = f"{benchmark_name_upper}_{t}"
        schedule_name = utils.get_benchmark_schedule_name(benchmark_name,t)
        schedule_url = os.path.join(
            benchmark_interference_dir,
            schedule_name+".csv"
        )
        controller_log_url = utils.get_controller_log_url(
            benchmark_interference_name,
            schedule_name
        )
        with open(schedule_url, "w") as schedule_file :
            schedule_file.write(get_schedule_header())
            schedule_file.write(get_controller_start_line(controller_log_url))
            schedule_file.write(benchmarks_funcs.get_instance_start_line(instance_name,CONTROLLER_DELAY,t,target))
            schedule_file.write(get_instance_terminate_line(instance_name,CONTROLLER_DELAY+RUN_FOR))
            schedule_file.write(get_controller_terminate_line(CONTROLLER_DELAY+RUN_FOR+CONTROLLER_DELAY))


if __name__ == "__main__" :
    main()
