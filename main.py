import json
import logging
import random
from json import JSONDecodeError
import traceback
from typing import Literal

import requests
import time
from uuid import UUID

from pyvis.network import Network

from config import setup_logger, load, get, get_proxies
from util import request_headers, save_result, import_result

delay = 4

_nodes: list[UUID] = []
_uuid_to_ign: dict[str, str] = {}
_edges: list[tuple[UUID, UUID]] = []

_request_counts = 0
_last_req = -1  # timestamp

_import_json = ""


def _wait():
    global _request_counts
    global _last_req
    while True:
        if _last_req == -1:
            break
        _t = time.time()
        if _t - _last_req >= delay:
            break


def _reset():
    global _request_counts
    global _last_req
    _request_counts += 1
    _last_req = time.time()


def _build_edge(current: UUID, previous: UUID = None):
    if _nodes.count(current) == 0:
        _nodes.append(current)

    _has_prev = previous is not None
    if _has_prev:
        _cs = str(current)
        _pv = str(previous)
        if _cs > _pv:
            _o: tuple = (previous, current)
        else:
            _o: tuple = (current, previous)
        if _edges.count(_o) == 0:
            _edges.append(_o)

    _status, _res = _make_request(current)
    if _status != 200:
        logging.warning("Skipping fetching {} friend list because something did not go well.".format(current))
        if _status == 403:
            logging.error("Remote host returned 403 FORBIDDEN.")
        return

    for _i in _res:
        _next = _i["uuid"]
        _obj = UUID(_next)
        if _has_prev and str(_obj) == str(previous):
            continue
        _uuid_to_ign[str(_obj)] = _i["user_name"]
        _build_edge(_next, current)


def generate_graph_object():

    nt = Network(filter_menu=True, select_menu=True, height="1800px", width="1800px")
    _coord = len(_uuid_to_ign)

    for i in _nodes:
        _u = str(i)
        _u = _uuid_to_ign[_u]
        nt.add_node(n_id=_u, label=_u,
                    x=random.Random().randint(0, _coord), y=random.Random().randint(0, _coord))

    for i in _edges:
        _u0 = str(i[0])
        _u0 = _uuid_to_ign[_u0]
        _u1 = str(i[1])
        _u1 = _uuid_to_ign[_u1]
        nt.add_edge(_u0, _u1)
        nt.add_edge(_u1, _u0)

    nt.toggle_physics(False)
    nt.show("graph.html", local=True, notebook=False)


def _make_request(_uuid: UUID, mode: Literal["friends", "profile"] = "friends") -> [int, list]:
    if _request_counts >= get("maximum_requests") and mode == "friends":
        logging.warning("Maximum requests reached. Abort.")
        return 429, []
    _wait()
    _url = "https://{}/api/v3/user/{}/{}".format(request_headers["host"], _uuid, mode)
    logging.debug(_url)
    req = requests.get(_url, proxies=get_proxies(), headers=request_headers)
    _status = req.status_code
    logging.debug(_status)
    logging.debug(req.headers)
    res = req.text
    logging.debug(res)
    _reset()
    if _status != 200:
        return _status, []
    try:
        _r = json.loads(res)
    except JSONDecodeError:
        logging.error("There's some problem parsing response at {}: {}".format(_uuid, res))
        traceback.print_exc()
        _r = []
    logging.debug(_r)
    return _status, _r


def run(_uuid: UUID):
    global _nodes
    global _edges
    global _uuid_to_ign
    global _import_json
    if not _import_json:
        time.sleep(30)
        _build_edge(_uuid, None)
        _status, _res = _make_request(_uuid, "profile")
        _s = str(_uuid)
        if _status == 200:
            _uuid_to_ign[_s] = _res["username"]
        else:
            _uuid_to_ign[_s] = _s
    else:
        _nodes, _edges, _uuid_to_ign = import_result(_import_json)

    generate_graph_object()


def init():
    setup_logger()
    load()
    global _import_json
    _import_json = get("import_result")
    if _import_json:
        return None
    _start_spot = input("Give an UUID to start from: ")
    _uuid = UUID(_start_spot)
    return _uuid


if __name__ == "__main__":
    try:
        run(init())
    finally:
        if not _import_json:
            save_result(_nodes, _uuid_to_ign, _edges)
