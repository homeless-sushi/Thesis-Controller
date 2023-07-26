import csv
import os

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
IN_DATA_DIR = os.path.join(SCRIPT_DIR,"data")

PROJECT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR,"../../"))
RUN_SCHEDULE_URL = os.path.join(PROJECT_DIR, "run_schedule.py")
PLOT_THROUGHPUT_URL = os.path.join(PROJECT_DIR, "scripts/plot_throughput.py")
OUT_DATA_DIR = os.path.join(PROJECT_DIR, "data")

SCHEDULES_SUBDIR = "interference"

def main() :

    data_files = [f for f in os.listdir(IN_DATA_DIR) if os.path.isfile(os.path.join(IN_DATA_DIR, f))]
    datas = []
    for data_file in data_files:
        benchmark, _ = os.path.splitext(data_file)
        data = {}
        data["NAME"] = benchmark.upper()

        data_file_url = os.path.join(IN_DATA_DIR, data_file)
        with open(data_file_url, "r") as data_file :
            csv_data = csv.reader(data_file)
            next(csv_data, None)
            data["CSV"] = list(csv_data)

        datas.append(data)

    for i in range(len(datas)) :
        data1 = datas[i]
        n1 = data1["NAME"]
        
        for csv_data1 in data1["CSV"]:
            input1, _, _ = csv_data1
            
            for j in range(i+1, len(datas)) :
                data2 = datas[j]
                n2 = data2["NAME"]

                for csv_data2 in data2["CSV"]:
                    input2, _, _ = csv_data2

                    SCHEDULE_NAME = f"{n1}_{input1}_{n2}_{input2}"
                    os.system(
                        f"sudo python3.8 "
                        f"{RUN_SCHEDULE_URL} {SCHEDULES_SUBDIR}/{SCHEDULE_NAME}"
                    )
                    os.system(f"sudo chown -R miele {OUT_DATA_DIR}")
                    os.system(
                        f"sudo python3.8 "
                        f"{PLOT_THROUGHPUT_URL} "
                        f"{OUT_DATA_DIR}/{SCHEDULES_SUBDIR}/{SCHEDULE_NAME}/controller.csv "
                        f"{OUT_DATA_DIR}/{SCHEDULES_SUBDIR}/{SCHEDULE_NAME}/throughput_plot.png"
                    )

if __name__ == "__main__" :
    main()

