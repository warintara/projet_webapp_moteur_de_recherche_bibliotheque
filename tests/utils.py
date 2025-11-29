import time
import requests

BASE_URL = "http://127.0.0.1:8000"


def api_get(path, params=None):
    url = BASE_URL + path
    try:
        r = requests.get(url, params=params)
        return r.json()
    except Exception as e:
        print("Erreur API:", e)
        return None

def measure_time(func, *args, repeat=10):
    times = []
    for _ in range(repeat):
        start = time.perf_counter()
        func(*args)
        end = time.perf_counter()
        times.append((end - start) * 1000)  # ms
    return sum(times) / len(times), times
