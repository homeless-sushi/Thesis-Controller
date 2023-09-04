import argparse
import sys

import pandas as pd

# csv field and keywords
## fields
PHASE = "PHASE"
MEAN_DURATION = "MEAN_DURATION"
PERCENTAGE = "PERCENTAGE"
## phases
LOOP = "LOOP"
SETUP = "SETUP"
WAIT_REGISTRATION = "WAIT REGISTRATION"
CONTROLLER_PULL = "CONTROLLER PULL"
MARGOT_PULL = "MARGOT PULL"
WIND_UP = "WIND UP"
UPLOAD = "UPLOAD"
KERNEL_GPU = "KERNEL_GPU"
DOWNLOAD = "DOWNLOAD"
WIND_DOWN = "WIND DOWN"
CONTROLLER_PUSH = "CONTROLLER PUSH"
MARGOT_PUSH = "MARGOT PUSH"
## devices
CPU = "CPU"
GPU = "GPU"


## computed


def setup_arg_parse() :

    parser = argparse.ArgumentParser(
        prog='Plot Applications Detail',
        description=
            'This program reads an two application detail files and computes '
            'the experct interference the interference;\n'
            'The application details are csv\'s, with the following format:\n\n'
            'PHASE,TOT_DURATION,PERCENTAGE',
        usage=f'{sys.argv[0]} app1_detail_URL app2_detail_URL'
    )

    parser.add_argument(
        "app1_detail_URL",
        type=str,
        help="An application detail in .csv format"
    )

    parser.add_argument(
        "app2_detail_URL",
        type=str,
        help="An application detail in .csv format"
    )

    return parser

def time(a1, a2) :
    a1_loop = a1[a1[PHASE]==LOOP][MEAN_DURATION].item()
    a2_gpu_percentage = (
        a2[a2[PHASE]==UPLOAD][PERCENTAGE].item() + 
        a2[a2[PHASE]==KERNEL_GPU][PERCENTAGE].item()
    )
    
    time = a1_loop
    a2_cpu_percentage = 100-a2_gpu_percentage
    time_with_delay = a1_loop + delay(a1,a2)
    return (time*a2_cpu_percentage + time_with_delay*a2_gpu_percentage)/100

def delay(a1, a2) :

    a1_upload = a1[a1[PHASE]==UPLOAD][MEAN_DURATION].item()
    a1_kernel = a1[a1[PHASE]==KERNEL_GPU][MEAN_DURATION].item()

    a2_upload = a2[a2[PHASE]==UPLOAD][MEAN_DURATION].item()
    a2_kernel = a2[a2[PHASE]==KERNEL_GPU][MEAN_DURATION].item()
    a2_download = a2[a2[PHASE]==DOWNLOAD][MEAN_DURATION].item()

    return (a2_upload + 
            max(0,a2_kernel-a1_upload) + 
            max(0,a2_download-a1_kernel))

def main() :

    # Setup argument parser and parse 
    parser = setup_arg_parse()
    args = parser.parse_args()

    # Read details
    a1 = pd.read_csv(args.app1_detail_URL)
    a2 = pd.read_csv(args.app2_detail_URL)

    a1_time = time(a1,a2)

    print(f"Application1's estimated loop time: {a1_time}")
    

if __name__ == "__main__" :
    main()