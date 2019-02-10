import json
import os
import math
import datetime
import numpy as np
import matplotlib.pyplot as plt
from data_parse import MovieData

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
        obj = MovieData()
        obj.loads(lines)
        all_data[obj.movieName] = obj

time_max = 0
time_min = 2000000000
for movie_name in all_data:
    movie_data = all_data[movie_name].get_data_list(time)
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


fig = plt.figure(figsize=(10, 4), dpi=128)

for movie_name in all_data:

    print("Drawing " + movie_name + ".")

    movie_data = all_data[movie_name]
    all_day_box_info = []
    all_sum_box_info = []
    all_seat_rate = []
    all_box_rate = []
    all_show = []

    time_stamps = []

    for data in movie_data:

        time = data["time"]
        day_box_info = data["dayBoxInfo"]
        sum_box_info = reformat(data["sumBoxInfo"])
        seat_rate = reformat(data["seatRate"])
        box_rate = reformat(data["boxRate"])
        total_show = data["totalShow"]

        if "亿" in sum_box_info:
            sum_box_info = float(sum_box_info.replace("亿", "")) * 10000
        elif "万" in sum_box_info:
            sum_box_info = float(sum_box_info.replace("万", ""))

        all_day_box_info.append(float(day_box_info))
        all_sum_box_info.append(float(sum_box_info))
        all_seat_rate.append(float(seat_rate))
        all_box_rate.append(float(box_rate))
        all_show.append(float(total_show))

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
            if all_delta_box[n] > 10:  # Prevent interference of data-interruption
                all_delta_box[n] = 10

    gaussian_kernel_radius = 256
    # gaussian_kernel_radius = 16
    gaussian_kernel_radius = 1

    data_bias = gaussian_kernel_radius * 2 - 1
    x = time_stamps[:len(time_stamps) - data_bias]
    y = gaussian_smooth(all_sum_box_info, gaussian_kernel_radius)

    plt.plot(np.array(x), np.array(y), label=movie_name, linewidth=1.6)
    bottom = plt.ylim()[0]
    bottom_vals = np.zeros(len(x))
    for i in range(len(x) - 1):  # Temporarily set value to 0.
        bottom_vals[i] = 0
    plt.fill_between(np.array(x), bottom_vals, np.array(y), alpha=0.1)

plt.grid(color=(0.8, 0.8, 0.8, 0.8))
plt.xlim([time_min, time_max])
plt.ylim(bottom=0)
plt.legend()

plt.xlabel("Unix时间戳")
plt.ylabel("票房增速 万元/秒")
plt.title("电影票房增长速度 - " + "[" + time_min_text + "到" + time_max_text + "]")

if False:
    plt.xlabel("Unix时间戳")
    plt.ylabel("总票房 万元")
    plt.title("电影总票房 - " + "[" + time_min_text + "到" + time_max_text + "]")

elif False:
    plt.xlabel("Unix时间戳")
    plt.ylabel("排片量 （场）")
    plt.title("排片量 - " + "[" + time_min_text + "到" + time_max_text + "]")

plt.show()
