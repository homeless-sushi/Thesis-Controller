import csv
import os

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
T_URL = os.path.join(SCRIPT_DIR,"t.csv")

PROJECT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR,"../../"))
OUT_DIR = os.path.join(PROJECT_DIR,"schedules/interference/")

def main() :

    data = None
    with open(T_URL, "r") as data_file :
        data = csv.reader(data_file)
        next(data, None)
        data = list(data)

    os.makedirs(OUT_DIR, exist_ok=True)
    
    for t1, _, target1 in data :
        for t2, _, target2 in data :
            
            if t1 != t2 :
                instance1_name = f"DUMMY_{t1}"
                instance2_name = f"DUMMY_{t2}"
            else :
                instance1_name = "FIRST"
                instance2_name = "SECOND"

            file_url = os.path.join(OUT_DIR, f"dummy_{t1}_{t2}.csv")
            with open(file_url, "w") as schedule_file :
                schedule_file.write("BENCHMARK,INSTANCE_NAME,START_TIME,INPUT,OUTPUT,THROUGHPUT,APPEND\n")
                schedule_file.write(f"DUMMY,{instance1_name},0,8192.txt,FIRST.txt,{target1},--times {t1}\n")
                schedule_file.write(f"DUMMY,{instance2_name},0,8192.txt,SECOND.txt,{target2},--times {t2}\n")
                schedule_file.write(f"TERMINATE,{instance1_name},50,,,,\n")
                schedule_file.write(f"TERMINATE,{instance2_name},50,,,,\n")
                schedule_file.write("TERMINATE,CONTROLLER,52,,,,\n")


    for t, _, target in data :

        file_url = os.path.join(OUT_DIR, f"dummy_{t}.csv")
        with open(file_url, "w") as schedule_file :
            instance_name = f"DUMMY_{t}"
            schedule_file.write("BENCHMARK,INSTANCE_NAME,START_TIME,INPUT,OUTPUT,THROUGHPUT,APPEND\n")
            schedule_file.write(f"DUMMY,{instance_name},0,8192.txt,FIRST.txt,{target},--times {t}\n")
            schedule_file.write(f"TERMINATE,{instance_name},50,,,,\n")
            schedule_file.write("TERMINATE,CONTROLLER,52,,,,\n")

if __name__ == "__main__" :
    main()
