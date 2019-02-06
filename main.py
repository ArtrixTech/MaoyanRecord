from data_parse import MovieData, MovieApi
import requests
import json
import time
import os
import datetime

movie_api = MovieApi()
all_movies = {}
for movie_id in movie_api.movie_ids:
    all_movies[movie_id] = MovieData(movie_api.get_raw_json(movie_id))


def refresh_all():
    result = movie_api.refresh()
    if result:
        for movie_id2 in movie_api.movie_ids:
            all_movies[movie_id2].update(movie_api.get_raw_json(movie_id2))
        return True
    return False


refresh_interval = 5  # Unit = Second
last_refresh = time.time()
while True:
    if time.time() - last_refresh > refresh_interval:
        result = refresh_all()
        if result:
            print("[" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "]: Refreshed.")
        else:
            print("[" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "]: Failed due to connection error.")

        last_refresh = time.time()
    time.sleep(0.1)
