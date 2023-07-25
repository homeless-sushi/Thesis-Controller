import csv
import os

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
N_URL = os.path.join(SCRIPT_DIR,"n.csv")

PROJECT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR,"../../"))
OUT_DIR = os.path.join(PROJECT_DIR,"schedules/nbody_interference/")

def main() :

    data = None
    with open(N_URL, "r") as data_file :
        data = csv.reader(data_file)
        next(data, None)
        data = list(data)

    os.makedirs(OUT_DIR, exist_ok=True)
    
    for n1, _, target1 in data :
        for n2, _, target2 in data :
            
            if n1 != n2 :
                instance1_name = f"NBODY_{n1}"
                instance2_name = f"NBODY_{n2}"
            else :
                instance1_name = "FIRST"
                instance2_name = "SECOND"

            file_url = os.path.join(OUT_DIR, f"nbody_{n1}_{n2}.csv")
            with open(file_url, "w") as schedule_file :
                schedule_file.write("BENCHMARK,INSTANCE_NAME,START_TIME,INPUT,OUTPUT,THROUGHPUT,APPEND\n")
                schedule_file.write(f"NBODY,{instance1_name},0,{n1}.txt,FIRST.txt,{target1},\n")
                schedule_file.write(f"NBODY,{instance2_name},0,{n2}.txt,SECOND.txt,{target2},\n")
                schedule_file.write(f"TERMINATE,{instance1_name},50,,,,\n")
                schedule_file.write(f"TERMINATE,{instance2_name},50,,,,\n")
                schedule_file.write("TERMINATE,CONTROLLER,52,,,,\n")


    for n, _, target in data :

        file_url = os.path.join(OUT_DIR, f"nbody_{n}.csv")
        with open(file_url, "w") as schedule_file :
            instance_name = f"NBODY_{n}"
            schedule_file.write("BENCHMARK,INSTANCE_NAME,START_TIME,INPUT,OUTPUT,THROUGHPUT,APPEND\n")
            schedule_file.write(f"NBODY,{instance_name},0,{n}.txt,FIRST.txt,{target},\n")
            schedule_file.write(f"TERMINATE,{instance_name},50,,,,\n")
            schedule_file.write("TERMINATE,CONTROLLER,52,,,,\n")

if __name__ == "__main__" :
    main()
