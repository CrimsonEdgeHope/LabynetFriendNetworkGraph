__all__ = [
    "request_headers",
    "save_result"
]

import json
import logging
import os
import time
from uuid import UUID

import config

request_headers = {
    "host": "laby.net",
    "user-agent": "curl/7.74.0",
    "accept": "*/*"
}


def save_result(nodes: list[UUID], uuid_to_ign: dict[UUID, str], edges: list[tuple[UUID, UUID]]):
    r = {
        "metadata": {
            "created_at_unix": time.time(),
            "request_headers": request_headers,
            "config": config.get_config()
        },
        "data": {
            "nodes": [str(i) for i in nodes],
            "edges": list(map(lambda _v: (str(_v[0]), str(_v[1])), edges)),
            "uuid_to_ign": {}
        }
    }
    _obj = r["data"]["uuid_to_ign"]
    for _k, _v in uuid_to_ign.items():
        _obj[str(_k)] = _v

    _filepath = os.path.join("result", "{}.json".format(time.strftime("%Y-%m-%d-%H-%M-%S")))
    _dirs = os.path.split(_filepath)[0]
    if _dirs:
        os.makedirs(_dirs, exist_ok=True)
    with open(_filepath, "w") as wf:
        wf.write(json.dumps(r, ensure_ascii=False, indent=2))
        logging.info("Saving result to {}".format(_filepath))
