import os
import random
from itertools import product

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__)) + "/"

nbody = [
    ('NBODY', 256, 1.096, 'NBODY,CONFIG,{},3,256.txt,{}.txt,{},\n'),
]

sgemm = [
    ('SGEMM', 32, 159.0, 'SGEMM,CONFIG,{},3,32x32.txt,{},{},--cpu-tile-exp 1\n'),
    ('SGEMM', 64, 35.3, 'SGEMM,CONFIG,{},3,64x64.txt,{},{},--cpu-tile-exp 1\n'),
    ('SGEMM', 128, 6.98, 'SGEMM,CONFIG,{},3,128x128.txt,{},{},--cpu-tile-exp 1\n'),
    ('SGEMM', 256, 1.18, 'SGEMM,CONFIG,{},3,256x256.txt,{},{},--cpu-tile-exp 1\n'),
]

histo = [
    ('HISTO', 480, 17.18, 'HISTO,CONFIG,{},3,854x480.bin,{},{},\n'),
    ('HISTO', 720, 8.27, 'HISTO,CONFIG,{},3,1280x720.bin,{},{},\n'),
    ('HISTO', 1080, 3.72, 'HISTO,CONFIG,{},3,1920x1080.bin,{},{},\n'),
    ('HISTO', 1440, 2.13, 'HISTO,CONFIG,{},3,2560x1440.bin,{},{},\n')
]

terminate_app = 'TERMINATE,,{},33,,,,\n'
terminate_controller = 'TERMINATE,,CONTROLLER,36,,,,\n'

permutations = []
permutations.extend(list(product(nbody, sgemm, histo)))
permutations.extend(list(product(nbody, histo, sgemm)))
permutations.extend(list(product(sgemm, nbody, histo)))
permutations.extend(list(product(sgemm, histo, nbody)))
permutations.extend(list(product(histo, nbody, sgemm)))
permutations.extend(list(product(histo, sgemm, nbody)))
random_perms = random.sample(permutations, 15)

#permutations.extend(list(product(histo, sgemm, histo)))
#permutations.extend(list(product(sgemm, histo, sgemm)))
#random_perms = random.sample(permutations, 5)
for perm in random_perms:
    dir_url = os.path.join(PROJECT_DIR, "schedules", "cpu_power_test")
    file_name = f"{perm[0][0].lower()}{perm[0][1]}_{perm[1][0].lower()}{perm[1][1]}_{perm[2][0].lower()}{perm[2][1]}"
    file_url = os.path.join(dir_url, file_name + ".csv")

    controller_file_url = os.path.join(PROJECT_DIR, "data", "cpu_power_test", file_name, "controller.csv")
    power_file_url = os.path.join(PROJECT_DIR, "data", "cpu_power_test", file_name, "power.csv")
    configuration_url = os.path.join(PROJECT_DIR, "schedules", "cpu_power_test", "1479000_76800000_3_apps.txt")

    with open(file_url, 'w') as out_file:
        out_file.write('BENCHMARK,TYPE,INSTANCE_NAME,START_TIME,INPUT,OUTPUT,THROUGHPUT,APPEND\n')
        out_file.write(f'CONTROLLER,SET_CONFIGURATION,,0,,,,--controller-log {controller_file_url} --sensors-log {power_file_url} --configuration-file {configuration_url}\n')
        out_file.write(perm[0][3].format("APP1", "1.txt", str(perm[0][2] * 0.75)))
        out_file.write(perm[1][3].format("APP2", "2.txt", str(perm[1][2] * 0.50)))
        out_file.write(perm[2][3].format("APP3", "3.txt", str(perm[2][2] * 0.25)))
        out_file.write(terminate_app.format("APP1"))
        out_file.write(terminate_app.format("APP2"))
        out_file.write(terminate_app.format("APP3"))
        out_file.write(terminate_controller)
