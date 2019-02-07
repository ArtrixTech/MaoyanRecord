import json
import os
import math
import datetime
import numpy as np
import matplotlib.pyplot as plt

# Prevent Chinese encoding error
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
record_dir = "records/"

path = os.listdir(record_dir)
all_records_loc = []
for p in path:
    all_records_loc.append(record_dir + p)

all_data = {}

for file_loc in all_records_loc:
    with open(file_loc, mode="r") as file:
        lines = file.readlines()
        print("Processing file '" + file_loc + "'")
        for line in lines:
            try:
                json_data = json.loads(line)
                movie_name = json_data["movieName"]

                # To adapt the previous version of data format
                if "integrateBox" in json_data["data"]:
                    json_data["data"]["dayBoxInfo"] = json_data["data"]["integrateBox"]
                if "sumBoxInfo" not in json_data["data"]:
                    json_data["data"]["sumBoxInfo"] = 0

                if movie_name in all_data:
                    assert isinstance(all_data[movie_name], list)
                    all_data[movie_name].append(json_data["data"])
                else:
                    all_data[movie_name] = [json_data["data"]]
            except json.decoder.JSONDecodeError:
                print(line)
                print(lines[lines.index(line) - 1])

time_max = 0
time_min = 2000000000
for movie_name in all_data:
    movie_data = all_data[movie_name]
    for data in movie_data:
        if data["time"] < time_min:
            time_min = data["time"]
        if data["time"] > time_max:
            time_max = data["time"]

print(datetime.datetime.fromtimestamp(time_max))
print(datetime.datetime.fromtimestamp(time_min))

for movie_name in all_data:

    movie_data = all_data[movie_name]
    x_data = []
    y_data = []

    for data in movie_data:

        time = data["time"]
        day_box_info = data["dayBoxInfo"]
        sum_box_info = str(data["boxRate"]).replace("%","")

        if "亿" in sum_box_info:
            sum_box_info = float(sum_box_info.replace("亿", "")) * 10000
        elif "万" in sum_box_info:
            sum_box_info = float(sum_box_info.replace("万", ""))

        x_data.append(time)
        y_data.append(sum_box_info)

    plt.plot(np.array(x_data), np.array(y_data), label=movie_name)

plt.legend()
plt.show()
