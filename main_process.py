from data_parse import MovieData, request_api
import requests
import json
import time

json_raw = requests.get(request_api).text
data_dict = json.loads(json_raw)
all_movies_data = [data_dict["data"]["list"]]
movies_count = [len(all_movies_data)]
all_movies = []

for movie_data in all_movies_data[0]:
    all_movies.append(MovieData(json.dumps(movie_data)))


def find_movie_obj(movie_id):
    for movie in all_movies:
        if movie_id == movie:
            return all_movies.index(movie)
    return False


def refresh_all():
    # For outer scope variant can't be modified, used list for replacement.
    all_movies_data[0] = json.loads(requests.get(request_api).text)["data"]["list"]
    movies_count[0] = len(all_movies_data)

    for movie_data in all_movies_data[0]:
        now_id = movie_data["movieId"]
        now_movie_index = find_movie_obj(now_id)
        if now_movie_index:
            all_movies[now_movie_index].update(json.dumps(movie_data))
            all_movies[now_movie_index].p()



refresh_interval = 2  # Unit = Second
last_refresh = time.time()
while True:
    if time.time() - last_refresh > refresh_interval:
        refresh_all()
        last_refresh = time.time()
    time.sleep(0.2)
