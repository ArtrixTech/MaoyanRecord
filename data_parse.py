#!/usr/bin/python3.6
# -*- coding: utf-8 -*-


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
            json_raw = self.requests.get(self.request_api, headers=self.headers, timeout=2).text
        except self.requests.exceptions.ReadTimeout:
            try:
                json_raw = self.requests.get(self.request_api, headers=self.headers, timeout=2).text
            except self.requests.exceptions.ReadTimeout:
                return False
        data_dict = self.json.loads(json_raw)
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
            raise NameError("The movie id is not exist.")

    def get_raw_json(self, movie_id):
        if movie_id in self.movie_ids:
            return self.json.dumps(self._data[movie_id])
        else:
            raise NameError("The movie id is not exist.")


class MovieData:
    import time
    import json

    def __init__(self, json_raw):
        data_dict = self.json.loads(json_raw)
        time_stamp = int(self.time.time())

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

    def __str__(self):
        return self.movieId

    def update(self, json_raw, save=True):
        data_dict = self.json.loads(json_raw)
        time_stamp = int(self.time.time())

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
        return self.json.dumps({"movieName": self.movieName, "data": content})

    def dumps_all(self):
        return self.json.dumps({"movieName": self.movieName, "data": self.data_record})
