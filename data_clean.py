import json

file_loc = "full/流浪地球.json"
with open(file_loc, mode="r") as file:
    lines = file.readlines()
    for line in lines:
        loaded = json.loads(line)
        movie_name = loaded["movieName"]
        raw_data = loaded["data"]

        time = raw_data["time"]
        assert isinstance(raw_data, dict)
        if "integrateBox" in raw_data:
            day_box_info = raw_data["integrateBox"]
        if "dayBoxInfo" in raw_data:
            day_box_info = raw_data["dayBoxInfo"]

        print(str(time) + "," + day_box_info)
