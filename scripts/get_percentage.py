import argparse
import sys

import pandas as pd
import matplotlib.pyplot as plt

# csv field and keywords
## fields
PHASE = 'PHASE'
DEVICE = 'DEVICE'
DURATION = 'DURATION'
## phases
LOOP = 'LOOP'
SETUP = "SETUP"
WAIT_REGISTRATION = "WAIT REGISTRATION"
CONTROLLER_PULL = "CONTROLLER PULL"
MARGOT_PULL = "MARGOT PULL"
WIND_UP = "WIND UP"
KERNEL = 'KERNEL'
WIND_DOWN = "WIND DOWN"
CONTROLLER_PUSH = "CONTROLLER PUSH"
MARGOT_PUSH = "MARGOT PUSH"
KERNEL = 'KERNEL'


## computed


def setup_arg_parse() :

    parser = argparse.ArgumentParser(
        prog='Plot Applications Detail',
        description=
            'This program reads an application log and computes the percentage'
            ' of time spent in each stage;\n'
            'The application logs are csv\'s, with the following format:\n\n'
            'PHASE,DEVICE,DURATION',
        usage=f'{sys.argv[0]} input_URL output_URL'
    )

    parser.add_argument(
        "input_URL",
        type=str,
        help="An application log in .csv format"
    )

    parser.add_argument(
        "output_URL",
        type=str,
        help="output file's URL"
    )

    return parser

def main() :

    # Setup argument parser and parse 
    parser = setup_arg_parse()
    args = parser.parse_args()

    # Read details
    detail_df = pd.read_csv(args.input_URL)

    # Delete uncompleted loops data
    last_loop_index = detail_df[detail_df[PHASE] == LOOP].index[-1]
    detail_df = detail_df.iloc[:last_loop_index + 1]

    # Total times
    SETUP_tot = detail_df[detail_df[PHASE] == SETUP][DURATION].sum()
    WAIT_REGISTRATION_tot = detail_df[detail_df[PHASE] == WAIT_REGISTRATION][DURATION].sum()
    LOOP_tot = detail_df[detail_df[PHASE] == LOOP][DURATION].sum()
    CONTROLLER_PULL_tot = detail_df[detail_df[PHASE] == CONTROLLER_PULL][DURATION].sum()
    MARGOT_PULL_tot = detail_df[detail_df[PHASE] == MARGOT_PULL][DURATION].sum()
    WIND_UP_tot = detail_df[detail_df[PHASE] == WIND_UP][DURATION].sum()
    KERNEL_tot = detail_df[detail_df[PHASE] == KERNEL][DURATION].sum()
    WIND_DOWN_tot = detail_df[detail_df[PHASE] == WIND_DOWN][DURATION].sum()
    CONTROLLER_PUSH_tot = detail_df[detail_df[PHASE] == CONTROLLER_PUSH][DURATION].sum()
    MARGOT_PUSH_tot = detail_df[detail_df[PHASE] == MARGOT_PUSH][DURATION].sum()

    # App total time
    tot_time = SETUP_tot + WAIT_REGISTRATION_tot + LOOP_tot

    # Number of loops
    n_loops = len(detail_df[detail_df[PHASE] == LOOP])

    # Mean times
    LOOP_avg = LOOP_tot / n_loops
    CONTROLLER_PULL_avg = CONTROLLER_PULL_tot / n_loops
    MARGOT_PULL_avg = MARGOT_PULL_tot / n_loops
    WIND_UP_avg = WIND_UP_tot / n_loops
    KERNEL_avg = KERNEL_tot / n_loops
    WIND_DOWN_avg = WIND_DOWN_tot / n_loops
    CONTROLLER_PUSH_avg = CONTROLLER_PUSH_tot / n_loops
    MARGOT_PUSH_avg = MARGOT_PUSH_tot / n_loops

    with open(args.output_URL, "w") as output_file :
        output_file.write("PHASE,MEAN_DURATION,TOT_DURATION,PERCENTAGE\n")
    
        # Phases
        output_file.write(f"{SETUP},,{SETUP_tot:.5f},\n")
        output_file.write(f"{WAIT_REGISTRATION},,{WAIT_REGISTRATION_tot:.5f},\n")
        output_file.write(f"{LOOP},{LOOP_avg:.5f},{LOOP_tot:.5f},{LOOP_avg/LOOP_avg*100:.3f}\n")
        output_file.write(f"{CONTROLLER_PULL},{CONTROLLER_PULL_avg:.5f},{CONTROLLER_PULL_tot:.5f},{CONTROLLER_PULL_avg/LOOP_avg*100:.3f}\n")
        output_file.write(f"{MARGOT_PULL},{MARGOT_PULL_avg:.5f},{MARGOT_PULL_tot:.5f},{MARGOT_PULL_avg/LOOP_avg*100:.3f}\n")
        output_file.write(f"{WIND_UP},{WIND_UP_avg:.5f},{WIND_UP_tot:.5f},{WIND_UP_avg/LOOP_avg*100:.3f}\n")
        output_file.write(f"{KERNEL},{KERNEL_avg:.5f},{KERNEL_tot:.5f},{KERNEL_avg/LOOP_avg*100:.3f}\n")
        output_file.write(f"{WIND_DOWN},{WIND_DOWN_avg:.5f},{WIND_DOWN_tot:.5f},{WIND_DOWN_avg/LOOP_avg*100:.3f}\n")
        output_file.write(f"{CONTROLLER_PUSH},{CONTROLLER_PUSH_avg:.5f},{CONTROLLER_PUSH_tot:.5f},{CONTROLLER_PUSH_avg/LOOP_avg*100:.3f}\n")
        output_file.write(f"{MARGOT_PUSH},{MARGOT_PUSH_avg:.5f},{MARGOT_PUSH_tot:.5f},{MARGOT_PUSH_avg/LOOP_avg*100:.3f}\n")

        # Other stats
        setup_overheads_tot = SETUP_tot + WAIT_REGISTRATION_tot
        output_file.write(f"SETUP_OVERHEADS,,{setup_overheads_tot:.5f},\n")
        controller_overheads_tot = CONTROLLER_PULL_tot + CONTROLLER_PUSH_tot
        controller_overheads_avg = CONTROLLER_PULL_avg + CONTROLLER_PUSH_avg
        output_file.write(f"CONTROLLER_OVERHEADS,{controller_overheads_avg:.5f},{controller_overheads_tot:.5f},{controller_overheads_avg/LOOP_avg*100:.3f}\n")
        margot_overheads_tot = MARGOT_PULL_tot + MARGOT_PUSH_tot
        margot_overheads_avg = MARGOT_PULL_avg + MARGOT_PUSH_avg
        output_file.write(f"MARGOT_OVERHEADS,{margot_overheads_avg:.5f},{margot_overheads_tot:.5f},{margot_overheads_avg/LOOP_avg*100:.3f}\n")
        algorithm_tot = WIND_UP_tot + KERNEL_tot + WIND_DOWN_tot
        algorithm_avg = WIND_UP_avg + KERNEL_avg + WIND_DOWN_avg
        output_file.write(f"ALGORITHM,{algorithm_avg:.5f},{algorithm_tot:.5f},{algorithm_avg/LOOP_avg*100:.3f}\n")

if __name__ == "__main__" :
    main()