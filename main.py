import json
import logging
import requests
import time
from uuid import UUID
from config import setup_logger, load, get

request_headers = {
    "Host": "laby.net",
    "user-agent": "curl/7.74.0",
    "accept": "*/*"
}

delay = 3.5
maximum_requests = 2

nodes: list[UUID] = []
uuid_to_ign: dict[UUID, str] = {}
edges: list[tuple[str, str]] = []


def make_request(_uuid: str):
    _r = []
    request_counts = 0
    _last_req = -1  # timestamp
    while request_counts < maximum_requests:
        while True:
            if _last_req == -1:
                break
            _t = time.time()
            if _t - _last_req >= delay:
                break
        req = requests.get("https://laby.net/api/v3/user/{}/friends".format(_uuid), proxies={
            "http": get("http_proxy"),
            "https": get("https_proxy")
        }, headers=request_headers)
        _status = req.status_code
        logging.debug(_status)
        logging.debug(req.headers)
        res = req.text
        logging.debug(res)
        request_counts += 1
        _last_req = time.time()
        if _status != 200:
            if _status == 403:
                logging.error("Failed to get friend list from {} !!!".format(_uuid))
                continue
        _r.append(json.loads(res))
    return _r


if __name__ == "__main__":
    setup_logger()
    load()
    _start_spot = input("Give an UUID to start from: ")
    _uuid = str(UUID(_start_spot))
    print(make_request(_uuid))
