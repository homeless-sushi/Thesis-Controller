import argparse
import os
import subprocess
import sys
import time

import pandas as pd

# directory where to place all of a runs data
SCHEDULE_LOG_PATH = "data/"

# csv field and keywords
BENCHMARK = 'BENCHMARK'
INSTANCE_NAME = 'INSTANCE_NAME'
START_TIME = 'START_TIME'
INPUT = 'INPUT'
OUTPUT = 'OUTPUT'
THROUGHPUT = 'THROUGHPUT'

CONTROLLER_NAME = "CONTROLLER"
TERMINATE = "TERMINATE"

def setup_arg_parse() :

    parser = argparse.ArgumentParser(
        prog='Benchmark_Scheduler',
        description=
            'This program reads a schedule of benchmarks'
            'and runs them according to it;\n'
            'The schedule is a csv, with the following format:\n\n'
            'BENCHMARK,INSTANCE_NAME,START_TIME,INPUT,OUTPUT,THROUGHPUT',
        usage=f'{sys.argv[0]} schedule_URL'
    )

    parser.add_argument(
        "schedule_URL",
        type=str,
        help="the schedule's URL"
    )

    return parser

def run_benchmark(name, instance_name, in_file, out_file, target_throughput) :
    
    # path names
    BENCHMARK_PATH = "benchmarks"
    BUILD_PATH = "build"
    IN_DIR = "data/in"
    OUT_DIR = "data/out"
    
    # command options
    INSTANCE_NAME_OPTION = "--instance-name"
    INPUT_OPTION = "--input-file"
    OUTPUT_OPTION = "--output-file"
    THROUGHTPUT_OPTION = "--target-throughput"

    instance_log = open(os.path.abspath(os.path.join(SCHEDULE_LOG_PATH, instance_name+".csv")), 'w')

    program_path = os.path.abspath(os.path.join(BENCHMARK_PATH, name, BUILD_PATH, name+"Benchmark"))
    process = subprocess.Popen(
        [program_path,
        INPUT_OPTION,  os.path.abspath(os.path.join(BENCHMARK_PATH, name, IN_DIR, in_file)), 
        OUTPUT_OPTION, os.path.abspath(os.path.join(BENCHMARK_PATH, name, OUT_DIR, out_file)),
        INSTANCE_NAME_OPTION, instance_name,
        THROUGHTPUT_OPTION, str(target_throughput)],
        stdout=instance_log
    )

    instance_log.close()
 
    return process

def run_controller() :
 
    # controller
    CONTROLLER_PATH = "build/RtrmController"
    CONTROLLER_LOG = "controller.csv"

    controller_log = open(os.path.abspath(os.path.join(SCHEDULE_LOG_PATH, CONTROLLER_LOG)), 'w')
    
    controller_path = os.path.abspath(CONTROLLER_PATH)
    process = subprocess.Popen(
        [controller_path],
        stdin=sys.stdin,
        stdout=controller_log,
        stderr=sys.stderr
    )

    controller_log.close()

    return process

def main() :

    # Setup argument parser and parse 
    parser = setup_arg_parse()
    args = parser.parse_args()

    # Create a directory with the name of the schedule
    # where to place all of the schedule data
    global SCHEDULE_LOG_PATH
    SCHEDULE_LOG_PATH = SCHEDULE_LOG_PATH + (os.path.splitext(os.path.basename(args.schedule_URL))[0])
    os.makedirs(SCHEDULE_LOG_PATH, exist_ok=True)

    # Read schedule
    schedule_df = pd.read_csv(args.schedule_URL)
    schedule_df = schedule_df.sort_values("START_TIME")

    # Convert start times to delays from previous events
    DELAY = "DELAY"
    schedule_df[DELAY] = schedule_df[START_TIME] - schedule_df[START_TIME].shift(1, fill_value=0)  
    schedule_df = schedule_df.drop(START_TIME, axis=1)

    # Start controller first
    processes = {}
    processes[CONTROLLER_NAME] = run_controller()

    # Start or terminate benchmarks accourding to the schedule
    for _, row in schedule_df.iterrows() :

        # Sleep according to the schedule
        time.sleep(row[DELAY])

        # If command is TERMINATE, terminate the instance
        if(row[BENCHMARK] == TERMINATE) :
            processes[row["INSTANCE_NAME"]].terminate()

        # Else run benchmark
        else :
            processes[row["INSTANCE_NAME"]] = run_benchmark(
                row[BENCHMARK],
                row[INSTANCE_NAME],
                row[INPUT],
                row[OUTPUT],
                row[THROUGHPUT]
            )

    # Wait for the controller to terminate
    processes[CONTROLLER_NAME].wait()

    return 0

if __name__ == "__main__" :
    main()