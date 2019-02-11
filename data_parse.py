#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
from enum import Enum
import time
import json
import numpy as np


class MovieApi:
    import requests
    import json

    def __init__(self):
        self.request_api = "https://box.maoyan.com/promovie/api/box/second.json"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36'}
        self._raw_data = ""
        self._data = {}
        self.movie_ids = []
        self.refresh()

    def refresh(self):
        try:
            json_raw = self.requests.get(self.request_api, headers=self.headers, timeout=2.5).text
        except:
            try:
                json_raw = self.requests.get(self.request_api, headers=self.headers, timeout=2.5).text
            except:
                return False
        data_dict = json.loads(json_raw)
        self._raw_data = data_dict["data"]["list"]

        for movie_data in self._raw_data:
            now_id = movie_data["movieId"]
            if now_id not in self.movie_ids:
                self.movie_ids.append(now_id)
            self._data[now_id] = movie_data

        return True

    def get_data(self, movie_id, attribute_name):
        if movie_id in self.movie_ids:
            return self._data[movie_id][attribute_name]
        else:
            raise NameError("The movie id doesn't exist.")

    def get_raw_json(self, movie_id):
        if movie_id in self.movie_ids:
            return json.dumps(self._data[movie_id])
        else:
            raise NameError("The movie id doesn't exist.")


class MovieData:
    class DataType(Enum):
        time = 1
        seatRate = 2
        avgPersonPerShow = 3
        dayBoxInfo = 4
        boxRate = 5
        sumBoxInfo = 6
        totalShow = 7
        showRate = 8
        deltaBox = 9

        @staticmethod
        def to_str(data_type_obj):
            return str(data_type_obj).replace("DataType.", "")

        @staticmethod
        def is_raw_data_type(data_type_obj):
            raw_data_type_list = [
                "time",
                "seatRate",  # 上座率
                "avgPersonPerShow",  # 场均人次
                "dayBoxInfo",  # 当天综合票房
                "boxRate",  # 票房占比
                "sumBoxInfo",  # 总票房
                "totalShow",  # 排片量
                "showRate"
            ]
            # return data_type_str in MovieData.DataType.raw_data_type_list
            return MovieData.DataType.to_str(data_type_obj) in raw_data_type_list

    def __init__(self, json_raw=None):

        if json_raw:
            data_dict = json.loads(json_raw)
            time_stamp = int(time.time())

            self.movieId = data_dict["movieId"]
            self.movieName = data_dict["movieName"]

            self.data_record = [{
                "time": time_stamp,
                "seatRate": data_dict["avgSeatView"],  # 上座率
                "avgPersonPerShow": data_dict["avgShowView"],  # 场均人次
                "dayBoxInfo": data_dict["boxInfo"],  # 当天综合票房
                "boxRate": data_dict["boxRate"],  # 票房占比
                "sumBoxInfo": data_dict["sumBoxInfo"],  # 总票房
                "totalShow": data_dict["showInfo"],  # 排片量
                "showRate": data_dict["showRate"],  # 排片占比
            }]

        self._key_name_to_type = {
            "time": self.DataType.time,
            "seatRate": self.DataType.seatRate,  # 上座率
            "avgPersonPerShow": self.DataType.avgPersonPerShow,  # 场均人次
            "dayBoxInfo": self.DataType.dayBoxInfo,  # 当天综合票房
            "boxRate": self.DataType.boxRate,  # 票房占比
            "sumBoxInfo": self.DataType.sumBoxInfo,  # 总票房
            "totalShow": self.DataType.totalShow,  # 排片量
            "showRate": self.DataType.showRate,  # 排片占比
        }

        self.time_formatted_data = {}
        self.data_record = []

    def __str__(self):
        return self.movieId

    def update(self, json_raw, save=True):
        data_dict = json.loads(json_raw)
        time_stamp = int(time.time())

        to_save = {
            "time": time_stamp,
            "seatRate": data_dict["avgSeatView"],  # 上座率
            "avgPersonPerShow": data_dict["avgShowView"],  # 场均人次
            "dayBoxInfo": data_dict["boxInfo"],  # 当天综合票房
            "boxRate": data_dict["boxRate"],  # 票房占比
            "sumBoxInfo": data_dict["sumBoxInfo"],  # 总票房
            "totalShow": data_dict["showInfo"],  # 排片量
            "showRate": data_dict["showRate"],  # 排片占比
        }
        import os
        if save:
            if not os.path.exists("saved"):
                os.mkdir("saved")
            with open("saved/" + self.movieName + ".json", mode="a") as file:
                file.writelines(self._dumps(to_save) + "\n")

        self.data_record.append(to_save)

    def _dumps(self, content):
        return json.dumps({"movieName": self.movieName, "data": content})

    def loads(self, input_content):
        """
        Import from outer file
        :param input_content: List<Of String> allowed only. !Important
        :return: None
        """
        line_index = 0
        assert isinstance(input_content, list)
        self.movieName = json.loads(input_content[0])["movieName"]

        for line in input_content:
            line_index += 1
            try:
                json_data = json.loads(line)

                # To adapt the previous version of data format
                if "integrateBox" in json_data["data"]:
                    json_data["data"]["dayBoxInfo"] = json_data["data"]["integrateBox"]
                if "sumBoxInfo" not in json_data["data"]:
                    json_data["data"]["sumBoxInfo"] = 0

                # To reformat data format
                # from {time:%TIME%,data:{data1:%DATA1%...}}
                #   to {time:%TIME%,data1:%DATA1%...}
                formatted_data = dict()

                for key in json_data["data"]:
                    formatted_data[key] = json_data["data"][key]

                self.data_record.append(formatted_data)

            except json.decoder.JSONDecodeError:
                print("  WARNING: Data incomplete at line " + str(line_index))
                print("    Content: " + line)

        def calc_total_data(data_type):
            assert isinstance(data_type, MovieData.DataType)
            data_type_str = MovieData.DataType.to_str(data_type)
            all_data = []
            for record in self.data_record:
                record_time = record["time"]
                record_data = record[data_type_str]
                all_data.append({"time": record_time, "data": record_data})
            self.time_formatted_data[data_type_str] = all_data

        def calc_additional_data():

            # Delta Box Calculation
            delta_box_source = self.get_data_list(MovieData.DataType.dayBoxInfo)
            delta_box = list(np.zeros(len(delta_box_source)))

            for n in range(len(delta_box_source) - 1):
                if n == 0:
                    delta_data = 0
                else:

                    now_source = delta_box_source[n]
                    last_source = delta_box_source[n - 1]

                    delta_time = float(now_source["time"]) - float(last_source["time"])
                    if delta_time == 0:
                        delta_time = 1

                    delta_data = (float(now_source["data"]) - float(last_source["data"])) / delta_time

                    if delta_data < 0:  # Prevent interference of day-change
                        delta_data = 0
                    if delta_data > 10:  # Prevent interference of data-interruption
                        delta_data = 10

                delta_box[n] = {"time": delta_box_source[n]["time"], "data": delta_data}

            self.time_formatted_data[MovieData.DataType.deltaBox] = delta_box

        for typ in MovieData.DataType:
            if MovieData.DataType.is_raw_data_type(typ):
                calc_total_data(typ)

        calc_additional_data()

    def dumps_all(self):
        return json.dumps({"movieName": self.movieName, "data": self.data_record})

    def get_data_list(self, data_type):
        """
        Generate List styled data
        :param data_type:
        :return: <List>
        """

        return self.time_formatted_data[MovieData.DataType.to_str(data_type)]
