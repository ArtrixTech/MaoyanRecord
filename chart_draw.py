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
    movie_data = all_data[movie_name].get_data_list(MovieData.DataType.boxRate)
    for data in movie_data:
        if data["time"] < time_min:
            time_min = data["time"]
        if data["time"] > time_max:
            time_max = data["time"]

time_min_text = str(datetime.datetime.fromtimestamp(time_min))
time_max_text = str(datetime.datetime.fromtimestamp(time_max))

print(time_max_text)
print(time_min_text)


def draw_graph(data_type, gaussian_kernel_radius=16):
    assert isinstance(data_type, MovieData.DataType)
    fig = plt.figure(figsize=(10, 4), dpi=128)

    def reformat(input_list):

        for index in range(len(input_list)):
            if data_type == MovieData.DataType.sumBoxInfo:
                if "亿" in str(input_list[index]["data"]):
                    input_list[index]["data"] = float(input_list[index]["data"].replace("亿", "")) * 10000
                elif "万" in str(input_list[index]):
                    input_list[index]["data"] = float(input_list[index]["data"].replace("万", ""))

            input_list[index]["data"] = float(str(input_list[index]["data"]).replace("%", ""))

        return input_list

    def extract_time_list(input_list):
        rt = []
        for index in range(len(input_list)):
            rt.append(input_list[index]["time"])
        return rt

    def extract_data_list(input_list):
        rt = []
        for index in range(len(input_list)):
            rt.append(input_list[index]["data"])
        return rt

    def gaussian_smooth(input_data, degree=160):
        window = degree * 2 - 1
        weight = np.array([1.0] * window)
        weight_gauss = []
        for index in range(window):
            index = index - degree + 1
            fraction = index / float(window)
            gauss = 1 / (np.exp((4 * fraction) ** 2))
            weight_gauss.append(gauss)
        weight = np.array(weight_gauss) * weight
        smoothed = [0.0] * (len(input_data) - window)
        for index in range(len(smoothed)):
            smoothed[index] = sum(np.array(input_data[index:index + window]) * weight) / sum(weight)
        return smoothed

    # Traversal all movie and draw
    for now_movie_key in all_data:
        now_movie = all_data[now_movie_key]
        assert isinstance(now_movie, MovieData)

        # Extract needed data from each movie obj and re-format
        reformatted = reformat(now_movie.get_data_list(data_type))
        data_list = extract_data_list(reformatted)
        time_list = extract_time_list(reformatted)

        print(len(reformatted))
        print(len(data_list))

        # Rear part of data_list will lost due to gaussian convolution operation
        # data_length_bias is the length of the cut part
        data_length_bias = gaussian_kernel_radius * 2 - 1
        x_data = time_list[:len(time_list) - data_length_bias]
        y_data = gaussian_smooth(data_list, gaussian_kernel_radius)

        plt.plot(np.array(x_data), np.array(y_data), label=now_movie.movieName, linewidth=1.6)

        bottom = plt.ylim()[0]
        bottom_vals = np.zeros(len(x_data))
        for i in range(len(x_data) - 1):  # Temporarily set value to 0.
            bottom_vals[i] = 0

        plt.fill_between(np.array(x_data), bottom_vals, np.array(y_data), alpha=0.1)

    plt.grid(color=(0.8, 0.8, 0.8, 0.8))
    plt.xlim([time_min, time_max])
    plt.ylim(bottom=0)
    plt.legend()

    plt.xlabel("Unix时间戳")
    if data_type == MovieData.DataType.deltaBox:
        plt.ylabel("票房增速(万元/秒)")
        plt.title("票房增速 - " + "[" + time_min_text + "到" + time_max_text + "]")
    if data_type == MovieData.DataType.dayBoxInfo:
        plt.ylabel("单日票房(万元)")
        plt.title("单日票房 - " + "[" + time_min_text + "到" + time_max_text + "]")
    if data_type == MovieData.DataType.sumBoxInfo:
        plt.ylabel("总票房(万元)")
        plt.title("总票房 - " + "[" + time_min_text + "到" + time_max_text + "]")
    if data_type == MovieData.DataType.showRate:
        plt.ylabel("排片占比 %")
        plt.title("排片占比 - " + "[" + time_min_text + "到" + time_max_text + "]")
    plt.show()


draw_graph(MovieData.DataType.showRate, 16)
draw_graph(MovieData.DataType.sumBoxInfo, 16)
draw_graph(MovieData.DataType.deltaBox, 256)


