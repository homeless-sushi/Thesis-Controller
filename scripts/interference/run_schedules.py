import csv
import os

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
T_URL = os.path.join(SCRIPT_DIR,"t.csv")

PROJECT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR,"../../"))
RUN_SCHEDULE_URL = os.path.join(PROJECT_DIR, "run_schedule.py")
PLOT_THROUGHPUT_URL = os.path.join(PROJECT_DIR, "scripts/plot_throughput.py")
DATA_DIR = os.path.join(PROJECT_DIR, "data")

SCHEDULES_SUBDIR = "interference"

def main() :

    data = None
    with open(T_URL, "r") as data_file :
        data = csv.reader(data_file)
        next(data, None)
        data = list(csv.reader(data_file))

    for t1, _, _ in data :
        for t2, _, _ in data :

            SCHEDULE_NAME = f"dummy_{t1}_{t2}"
            os.system(
                f"sudo python3.8 "
                f"{RUN_SCHEDULE_URL} {SCHEDULES_SUBDIR}/{SCHEDULE_NAME}"
            )
            os.system(f"sudo chown -R miele {DATA_DIR}")
            os.system(
                f"sudo python3.8 "
                f"{PLOT_THROUGHPUT_URL} "
                f"{DATA_DIR}/{SCHEDULES_SUBDIR}/{SCHEDULE_NAME}/controller.csv "
                f"{DATA_DIR}/{SCHEDULES_SUBDIR}/{SCHEDULE_NAME}/throughput_plot.png"
            )

    for t, _, _ in data :
    
        SCHEDULE_NAME = f"dummy_{t}"
        os.system(
            f"sudo python3.8 "
            f"{RUN_SCHEDULE_URL} {SCHEDULES_SUBDIR}/{SCHEDULE_NAME}"
        )
        os.system(f"sudo chown -R miele {DATA_DIR}")
        os.system(
            f"sudo python3.8 "
            f"{PLOT_THROUGHPUT_URL} "
            f"{DATA_DIR}/{SCHEDULES_SUBDIR}/{SCHEDULE_NAME}/controller.csv "
            f"{DATA_DIR}/{SCHEDULES_SUBDIR}/{SCHEDULE_NAME}/throughput_plot.png"
        )

if __name__ == "__main__" :
    main()

