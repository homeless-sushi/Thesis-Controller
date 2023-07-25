import collections
import csv
import os

import numpy as np
import matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def main() :

    no_interference_url = os.path.join(SCRIPT_DIR, "no_interference.csv")
    with open(no_interference_url, "r") as no_interference_file :
        no_interference = csv.reader(no_interference_file)
        next(no_interference, None)
        no_interference = dict([(app, float(throughput)) for app, throughput in no_interference])
        apps = no_interference.keys()

    interference_url = os.path.join(SCRIPT_DIR, "interference.csv")
    with open(interference_url, "r") as interference_file :
        interference = csv.reader(interference_file)
        next(interference, None)
        c = collections.defaultdict(dict)
        for app1, app2, throughput in interference :
            c[app1][app2] = float(throughput)/no_interference[app1]

    data = []
    for app1 in apps :

        row = []
        for app2 in apps :
            row.append(c[app1][app2])

        data.append(row)
    data = np.array(data)

    fig, ax = plt.subplots()
    im = ax.imshow(data)

    # Show all ticks and label them with the respective list entries
    ax.set_xticks(np.arange(len(apps)), labels=["With "+app+"%" for app in apps])
    ax.set_yticks(np.arange(len(apps)), labels=["Running "+app+"%" for app in apps])

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
            rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    for i in range(len(apps)):
        for j in range(len(apps)):
            text = ax.text(j, i, f"{data[i,j]:.2f}",
                ha="center", va="center", color="w")

    ax.set_title("App GPU interfence")
    fig.tight_layout()
    plt.show()   

if __name__ == '__main__' :
    main()