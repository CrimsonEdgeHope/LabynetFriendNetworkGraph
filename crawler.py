import os
import inquirer
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
from config import get, get_proxies, set_item
from util import request_headers, save_result, import_result

__all__ = [
    "run"
]


class _OpID:
    START_FROM_UUID = "1"
    IMPORT_RESULT = "2"

    def __init__(self):
        raise NotImplementedError()


def _init() -> str | int:
    _start_spot = get("start_spot")
    _import_json = get("import_json")

    class AutomationErrorAtInit(Exception):
        def __init__(self, msg):
            super().__init__(msg)

    def _validate_start_spot(_v):
        try:
            UUID(_v)
            return True
        except:
            return False

    def _validate_import_json(_v):
        return os.path.exists(os.path.join("result", _v))

    _automate = get("automate")
    if _automate is not None:
        if _automate == _OpID.START_FROM_UUID:
            if not _validate_start_spot(_start_spot):
                raise AutomationErrorAtInit("Invalid start_spot value.")
        elif _automate == _OpID.IMPORT_RESULT:
            if not _validate_import_json(_import_json):
                raise AutomationErrorAtInit("Invalid import_json value.")
        else:
            raise AutomationErrorAtInit("Unknown config value: {}".format(_automate))
        _op = _automate
    else:
        # Prompts
        _ans = inquirer.prompt([inquirer.List("op", message="What to do",
                                              choices=[
                                                  ("Start from an UUID", _OpID.START_FROM_UUID),
                                                  ("Import previous result", _OpID.IMPORT_RESULT)
                                              ],
                                              default=_OpID.IMPORT_RESULT)])
        _op = _ans["op"]
        if _op == "2":
            _ans = inquirer.prompt([
                inquirer.Text("filename", message="Result file name",
                              default=_import_json,
                              validate=lambda _prevans, _v: _validate_import_json(_v))
            ])
            _import_json = _ans["filename"]
            _start_spot = None
        else:
            _ans = inquirer.prompt([
                inquirer.Text("uuid", message="Give an UUID to start from",
                              default=_start_spot,
                              validate=lambda _prevans, _v: _validate_start_spot(_v))
            ])
            _start_spot = UUID(_ans["uuid"])
            _import_json = None

    set_item("start_spot", _start_spot)
    set_item("import_json", _import_json)

    return _op


def _wait(gap: int, last_time: float | int = None):
    if last_time is None:
        last_time = time.time()
    while True:
        if time.time() - last_time >= gap:
            break


def _construct_graph_json(nodes: list[UUID], edges: list[tuple[UUID, UUID]], uuid_to_ign: dict[str, str],
                          delay: int, session: requests.Session,
                          leftovers: list[UUID], forbid_out: list[UUID], error_out: list[UUID],
                          current: UUID, previous: UUID = None):
    def _add_edge(source: UUID, to: UUID):
        _src = str(source)
        _to = str(to)
        if _src > _to:
            _o: tuple = (to, source)
        else:
            _o: tuple = (source, to)
        if edges.count(_o) == 0:
            edges.append(_o)

    def _fetch_res():
        def _halt(_at, _re):
            if _at >= _re:
                return True
            logging.warning("A previous request just failed! Waiting 90 seconds")
            _wait(gap=90)
            return False

        _retries = 3
        _attempts = 0
        while True:
            try:
                _res_t = []
                _status_t, _res_t = _make_request_to_laby(delay=delay, session=session, uuid=current,
                                                          leftovers=leftovers)
                if _status_t != 200:
                    if _status_t == 403:
                        logging.error("Remote host returned 403 FORBIDDEN: 1. Blocked by Cloudflare. 2. {} hides "
                                      "friend list".format(str(current)))
                        _res_t = []
                        forbid_out.append(current)
                    if _status_t >= 500:
                        _attempts += 1
                        if _halt(_attempts, _retries):
                            break
                        continue

                return _status_t, _res_t
            except:
                _attempts += 1
                if _halt(_attempts, _retries):
                    break

        logging.error("Skipping fetching {} friend list because something did not go well".format(str(current)))
        error_out.append(current)
        return 500, []

    _node_present = nodes.count(current)
    if _node_present == 0:
        nodes.append(current)

    _has_prev = previous is not None
    if _has_prev:
        _add_edge(current, previous)

    if _node_present != 0:
        return

    _status, _res = _fetch_res()

    for _i in _res:
        _next = _i["uuid"]
        _obj = UUID(_next)
        _add_edge(_obj, current)

    for _i in _res:
        _next = _i["uuid"]
        _obj = UUID(_next)
        if _has_prev and str(_obj) == str(previous):
            continue
        uuid_to_ign[str(_obj)] = _i["user_name"]
        _construct_graph_json(nodes=nodes, edges=edges, uuid_to_ign=uuid_to_ign,
                              forbid_out=forbid_out, error_out=error_out, leftovers=leftovers,
                              delay=delay, session=session, current=_next, previous=current)


def _generate_graph_html(nodes: list[UUID], edges: list[tuple[UUID, UUID]], uuid_to_ign: dict[str, str]):
    nt = Network(filter_menu=True,
                 select_menu=True,
                 height="{}px".format(get("export_height")),
                 width="{}px".format(get("export_width")),
                 neighborhood_highlight=True,
                 cdn_resources="remote")
    _coord = len(uuid_to_ign) * 10

    for i in nodes:
        _u = str(i)
        _u = uuid_to_ign.get(_u, _u)
        nt.add_node(n_id=_u, label=_u,
                    x=random.Random().randint(0, _coord), y=random.Random().randint(0, _coord), size=10)

    for i in edges:
        _u0 = str(i[0])
        _u0 = uuid_to_ign.get(_u0, _u0)
        _u1 = str(i[1])
        _u1 = uuid_to_ign.get(_u1, _u1)
        nt.add_edge(_u0, _u1)
        nt.add_edge(_u1, _u0)

    nt.toggle_physics(False)
    nt.show(get("export_html"), local=True, notebook=False)


class _Requests:
    request_counts: int = 0
    last_req_time: float | int = -1  # timestamp

    def __init__(self):
        raise NotImplementedError()

    @staticmethod
    def wait(delay: int):
        if _Requests.last_req_time == -1:
            return
        _wait(gap=delay, last_time=_Requests.last_req_time)

    @staticmethod
    def add_count():
        _Requests.request_counts += 1
        _Requests.last_req_time = time.time()


def _make_request_to_laby(delay: int, session: requests.Session,
                          uuid: UUID, leftovers: list[UUID] = None,
                          mode: Literal["friends", "profile"] = "friends") -> [int, list]:
    if _Requests.request_counts >= get("maximum_requests") and mode == "friends":
        logging.warning("Maximum request counts reached. Abort.")
        leftovers.append(uuid)
        return 429, []

    _Requests.wait(delay)

    _url = "https://{}/api/v3/user/{}/{}".format(request_headers["host"], uuid, mode)
    logging.info(_url)
    req = session.get(_url, proxies=get_proxies(), headers=request_headers)
    _status = req.status_code
    logging.debug(_status)
    logging.debug(req.headers)
    res = req.text
    logging.debug(res)

    _Requests.add_count()
    if _status != 200:
        return _status, []
    try:
        _r = json.loads(res)
    except JSONDecodeError:
        logging.error("There's some problem parsing response at {}: {}".format(uuid, res))
        traceback.print_exc()
        _r = []
    logging.debug(_r)
    return _status, _r


def _run(nodes: list[UUID], edges: list[tuple[UUID, UUID]], uuid_to_ign: dict[str, str],
         delay: int = None, leftovers: list[UUID] = None, forbid_out: list[UUID] = None, error_out: list[UUID] = None,
         session: requests.Session = None,
         start_spot: UUID = None, import_json: str = None):
    _uuid = start_spot

    if _uuid is not None:
        logging.info("Wait 30 seconds in case 429")
        _wait(gap=30)
        _construct_graph_json(nodes=nodes, edges=edges, uuid_to_ign=uuid_to_ign,
                              delay=delay, session=session,
                              leftovers=leftovers, forbid_out=forbid_out, error_out=error_out,
                              current=_uuid)
        _status, _res = _make_request_to_laby(delay=delay, session=session, uuid=_uuid, mode="profile")
        _s = str(_uuid)
        if _status == 200:
            uuid_to_ign[_s] = _res["username"]
        else:
            uuid_to_ign[_s] = _s
    elif import_json is not None:
        nodes, edges, uuid_to_ign = import_result(import_json)
    else:
        raise ValueError("There's nothing.")

    _generate_graph_html(nodes, edges, uuid_to_ign)


def run():
    _op = _init()

    _start_spot = get("start_spot")
    _import_json = get("import_json")

    _nodes: list[UUID] = []
    _edges: list[tuple[UUID, UUID]] = []
    _uuid_to_ign: dict[str, str] = {}

    if _op == _OpID.IMPORT_RESULT:
        _run(nodes=_nodes, edges=_edges, uuid_to_ign=_uuid_to_ign, import_json=_import_json)
    else:
        _delay = 4
        _leftovers: list[UUID] = []
        _forbid_out: list[UUID] = []
        _error_out: list[UUID] = []
        _session = requests.Session()
        try:
            _run(nodes=_nodes, edges=_edges, uuid_to_ign=_uuid_to_ign,
                 delay=_delay, leftovers=_leftovers, forbid_out=_forbid_out, error_out=_error_out, session=_session,
                 start_spot=_start_spot)
        finally:
            save_result(nodes=_nodes, edges=_edges, uuid_to_ign=_uuid_to_ign,
                        leftovers=_leftovers, forbid_out=_forbid_out, error_out=_error_out)