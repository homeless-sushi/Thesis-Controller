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

def setup_arg_parse() :

    parser = argparse.ArgumentParser(
        prog='Plot Applications Detail',
        description=
            'This program reads an application log and computes the percentage'
            ' of time spent in each stage;\n'
            'The application logs are csv\'s, with the following format:\n\n'
            'EVENT,TYPE,DEVICE,TIMESTAMP',
        usage=f'{sys.argv[0]} detail_URL out_percentage_URL'
    )

    parser.add_argument(
        "detail_URL",
        type=str,
        help="An application log in .csv format"
    )

    parser.add_argument(
        "out_percentage_URL",
        type=str,
        help="URL for percentage output"
    )

    return parser

def main() :

    # Setup argument parser and parse 
    parser = setup_arg_parse()
    args = parser.parse_args()

    # Read details
    detail_df = pd.read_csv(args.detail_URL)

    # Compute total time
    min_time = detail_df[TIMESTAMP].iat[0]
    max_time = detail_df[TIMESTAMP].iat[-1]
    tot_time = max_time - min_time
    print(tot_time)

    # Compute durations
    start = detail_df[detail_df[TYPE] == START]
    stop = detail_df[detail_df[TYPE] == STOP]
    start[DURATION] = stop[TIMESTAMP].values - start[TIMESTAMP].values

    # Drop uninteresting data
    start = start.drop([TYPE,TIMESTAMP], axis='columns')

    # Sum durations
    start = start.groupby([EVENT,DEVICE]).sum()

    # Compute percentage
    start['%'] = (start[DURATION]*100) / tot_time 

    start.to_csv(args.out_percentage_URL)

if __name__ == "__main__" :
    main()