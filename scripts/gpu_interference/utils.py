import importlib.util
import os

INTERFERENCE_DIR = os.path.dirname(os.path.realpath(__file__))
BENCHMARKS_DATA_DIR = os.path.join(INTERFERENCE_DIR,"benchmarks")
BENCHMARK_DATA_FILENAME = "n.csv"

PROJECT_DIR = os.path.abspath(os.path.join(INTERFERENCE_DIR,"../../"))
SCHEDULES_DIR = os.path.join(PROJECT_DIR,"schedules")
RUN_DATA_DIR = os.path.join(PROJECT_DIR,"data")
RUN_SCHEDULE_URL = os.path.join(PROJECT_DIR, "run_schedule.py")

SCHEDULE_HEADER = "BENCHMARK,INSTANCE_NAME,START_TIME,INPUT,OUTPUT,THROUGHPUT,APPEND\n"

def get_benchmark_data_url(benchmark_name) :
    return os.path.join(BENCHMARKS_DATA_DIR,benchmark_name,"data","in",BENCHMARK_DATA_FILENAME)

def get_benchmark_interference_name(benchmark_name) :
    return f'{benchmark_name}_interference'

def get_benchmark_schedule_name(benchmark_name, t1, t2=None) :
    if t2 is None :
        return f'{benchmark_name}_{t1}'
    else :
        return f'{benchmark_name}_{t1}_{t2}'

def get_controller_log_url(benchmark_interference_name, benchmark_schedule_name) :
    return os.path.join(
        RUN_DATA_DIR,
        benchmark_interference_name,
        benchmark_schedule_name,
        "controller.csv"
    )

def get_no_interference_url(benchmark_name) :
    return os.path.join(
        BENCHMARKS_DATA_DIR,
        benchmark_name,
        "data",
        "out",
        "no_interference.csv"
    )

def get_interference_url(benchmark_name) :
    return os.path.join(
        BENCHMARKS_DATA_DIR,
        benchmark_name,
        "data",
        "out",
        "interference.csv"
    )

def get_estimated_interference_url(benchmark_name) :
    return os.path.join(
        BENCHMARKS_DATA_DIR,
        benchmark_name,
        "data",
        "out",
        "estimated_interference.csv"
    )

def import_benchmark_funcs(benchmark_name) :
    module_name = f"{benchmark_name}.utils"
    benchmark_utils_url = os.path.join(
        BENCHMARKS_DATA_DIR,
        benchmark_name,
        "scripts",
        "utils.py"
    )

    try:
        spec = importlib.util.spec_from_file_location(module_name, benchmark_utils_url)
        benchmark = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(benchmark)

    except ImportError:
        print(f"Failed to import module '{module_name}'")

    return benchmark
