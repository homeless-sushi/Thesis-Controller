import csv
import os

import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
T_URL = os.path.join(SCRIPT_DIR,"t.csv")

PROJECT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR,"../../"))
IN_DATA_DIR = os.path.join(PROJECT_DIR,"data/interference")

def main() :

    data = None
    with open(T_URL, "r") as data_file :
        data = csv.reader(data_file)
        next(data, None)
        data = list(csv.reader(data_file))

    solo = []
    for t, p, _ in data :
        df = pd.read_csv(os.path.join(IN_DATA_DIR,f"dummy_{t}/controller.csv"))
        df = df[df["CURRENT"] != 0]
        average = df["CURRENT"].mean()
        solo.append((p, average))

    no_interference_url = os.path.join(SCRIPT_DIR,"no_interference.csv")
    with open(no_interference_url, "w") as no_interfence_file :
        no_interfence_file.write("PERCENTAGE,THROUGHPUT\n")

        for p, throughput in solo :
            no_interfence_file.write(f"{p},{throughput}\n") 

    interference = []
    for t1, p1, _ in data :
        for t2, p2, _ in data :
            df = pd.read_csv(os.path.join(IN_DATA_DIR,f"dummy_{t1}_{t2}/controller.csv"))

            instance_name = f"DUMMY_{t1}"
            if t1 == t2 :
                instance_name = "FIRST"

            df = df[df["CURRENT"] != 0]
            average = df[df["NAME"] == instance_name]["CURRENT"].mean()
            interference.append((p1,p2,average))

    interference_url = os.path.join(SCRIPT_DIR,"interference.csv")
    with open(interference_url, "w") as interference_file :
        interference_file.write("PERCENTAGE,WITH,THROUGHPUT\n")
        
        for p1, p2, throughput in interference :
            interference_file.write(f"{p1},{p2},{throughput}\n") 

if __name__ == "__main__" :
    main()
