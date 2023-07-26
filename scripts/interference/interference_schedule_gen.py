import csv
import os

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_URL = os.path.join(SCRIPT_DIR,"data")

PROJECT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR,"../../"))
OUT_DIR = os.path.join(PROJECT_DIR,"schedules/interference/")

def main() :

    data_files = [f for f in os.listdir(DATA_URL) if os.path.isfile(os.path.join(DATA_URL, f))]
    datas = []
    for data_file in data_files:
        benchmark, _ = os.path.splitext(data_file)
        data = {}
        data["NAME"] = benchmark.upper()

        data_file_url = os.path.join(DATA_URL, data_file)
        with open(data_file_url, "r") as data_file :
            csv_data = csv.reader(data_file)
            next(csv_data, None)
            data["CSV"] = list(csv_data)

        datas.append(data)

    os.makedirs(OUT_DIR, exist_ok=True)
    
    for i in range(len(datas)) :
        data1 = datas[i]
        n1 = data1["NAME"]
        
        for csv_data1 in data1["CSV"]:
            input1, _, target1 = csv_data1
            
            for j in range(i+1, len(datas)) :
                data2 = datas[j]
                n2 = data2["NAME"]

                for csv_data2 in data2["CSV"]:
                    input2, _, target2 = csv_data2

                    instance1_name = "FIRST"
                    instance2_name = "SECOND"

                    file_url = os.path.join(OUT_DIR, f"{n1}_{input1}_{n2}_{input2}.csv")
                    with open(file_url, "w") as schedule_file :
                        schedule_file.write("BENCHMARK,INSTANCE_NAME,START_TIME,INPUT,OUTPUT,THROUGHPUT,APPEND\n")
                        schedule_file.write(f"{n1},{instance1_name},0,{input1}.txt,FIRST.txt,{target1},\n")
                        schedule_file.write(f"{n2},{instance2_name},0,{input2}.txt,SECOND.txt,{target2},\n")
                        schedule_file.write(f"TERMINATE,{instance1_name},50,,,,\n")
                        schedule_file.write(f"TERMINATE,{instance2_name},50,,,,\n")
                        schedule_file.write("TERMINATE,CONTROLLER,52,,,,\n")

if __name__ == "__main__" :
    main()
