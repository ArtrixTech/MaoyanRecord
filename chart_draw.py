import json
import os
import math
import datetime
import numpy as np
import matplotlib.pyplot as plt

# Prevent Chinese encoding error
plt.style.use("seaborn-dark")
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

time_min_text = str(datetime.datetime.fromtimestamp(time_min))
time_max_text = str(datetime.datetime.fromtimestamp(time_max))

print(time_max_text)
print(time_min_text)


def reformat(data):
    return str(data).replace("%", "")


fig = plt.figure(figsize=(9, 4), dpi=256)

for movie_name in all_data:

    print("Drawing " + movie_name + ".")

    movie_data = all_data[movie_name]
    all_day_box_info = []
    all_sum_box_info = []
    all_seat_rate = []
    all_box_rate = []

    time_stamps = []

    for data in movie_data:

        time = data["time"]
        day_box_info = data["dayBoxInfo"]
        sum_box_info = reformat(data["sumBoxInfo"])
        seat_rate = reformat(data["seatRate"])
        box_rate = reformat(data["boxRate"])

        if "亿" in sum_box_info:
            sum_box_info = float(sum_box_info.replace("亿", "")) * 10000
        elif "万" in sum_box_info:
            sum_box_info = float(sum_box_info.replace("万", ""))

        all_day_box_info.append(float(day_box_info))
        all_sum_box_info.append(float(sum_box_info))
        all_seat_rate.append(float(seat_rate))
        all_box_rate.append(float(box_rate))

        time_stamps.append(time)


    def gaussian_smooth(input_data, degree=160):
        window = degree * 2 - 1
        weight = np.array([1.0] * window)
        weight_gauss = []
        for i in range(window):
            i = i - degree + 1
            fraction = i / float(window)
            gauss = 1 / (np.exp((4 * fraction) ** 2))
            weight_gauss.append(gauss)
        weight = np.array(weight_gauss) * weight
        smoothed = [0.0] * (len(input_data) - window)
        for i in range(len(smoothed)):
            smoothed[i] = sum(np.array(input_data[i:i + window]) * weight) / sum(weight)
        return smoothed


    all_delta_box = np.zeros(len(all_day_box_info))

    for n in range(len(all_day_box_info) - 1):
        if n == 0:
            all_delta_box[n] = 0
        else:
            all_delta_box[n] = (all_day_box_info[n] - all_day_box_info[n - 1]) / 5
            if all_delta_box[n] < 0:  # Prevent interference of day-change
                all_delta_box[n] = 0

    gaussian_kernel_radius = 256
    data_bias = gaussian_kernel_radius * 2 - 1
    x = time_stamps[:len(time_stamps) - data_bias]
    y = gaussian_smooth(all_delta_box, gaussian_kernel_radius)

    plt.plot(np.array(x), np.array(y), label=movie_name, linewidth=1.6)
    bottom = plt.ylim()[0]
    bottom_vals = np.zeros(len(x))
    for i in range(len(x) - 1):
        bottom_vals[i] = 0
    plt.fill_between(np.array(x), bottom_vals, np.array(y), alpha=0.1)

plt.grid(color=(0.8, 0.8, 0.8, 0.8))
plt.xlim([time_min, time_max])
plt.ylim(bottom=0)
plt.legend()

plt.xlabel("Unix时间戳")
plt.ylabel("票房增速 万元/秒")
plt.title("电影票房增长速度 - " + "[" + time_min_text + "到" + time_max_text + "]")

plt.show()
