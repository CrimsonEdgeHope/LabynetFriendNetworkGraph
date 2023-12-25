import json
import logging
from json import JSONDecodeError
import traceback
from typing import Literal
import requests
import time
from uuid import UUID
from config import (get_item,
                    get_start_spot,
                    get_proxies,
                    get_crawling_method,
                    get_automation_id,
                    get_import_json,
                    AUTOMATION_START_FROM_UUID, AUTOMATION_IMPORT_RESULT,
                    CRAWLING_DEPTH_FIRST, CRAWLING_BREADTH_FIRST, set_item)
from util import (save_result,
                  import_result,
                  generate_graph_html,
                  uuid_to_str,
                  validate_import_json,
                  request_to_labynet,
                  validate_start_spot)
from ui_prompt import *


__all__ = [
    "run"
]


crawler_request_counts: int = 0
crawler_proxies = get_proxies()
crawler_request_maximum_counts: int = get_item("crawler", "maximum_requests").value
crawler_last_req_time: float | int = -1  # timestamp
bfs_pending: list[UUID] = []


def freeze(delay: int, last_time: float | int = None):
    if last_time is None:
        last_time = time.time()
    if time.time() - last_time >= delay:
        return
    time.sleep(delay)


def crawler_wait(delay: int):
    global crawler_last_req_time
    if crawler_last_req_time == -1:
        return
    freeze(delay=delay, last_time=crawler_last_req_time)


def crawler_req_add_count():
    global crawler_request_counts
    global crawler_last_req_time
    crawler_request_counts += 1
    crawler_last_req_time = time.time()


def crawler_init_prompt() -> str | int:
    _start_spot = get_start_spot()
    _import_json = get_import_json()

    _automate = get_automation_id()
    if _automate is not None:
        if _automate == AUTOMATION_START_FROM_UUID:
            if not validate_start_spot(_start_spot):
                raise ValueError("Automation failure: Invalid start_spot value.")
        elif _automate == AUTOMATION_IMPORT_RESULT:
            if not validate_import_json(_import_json):
                raise ValueError("Automation failure: Invalid import_json value.")
        else:
            raise ValueError("Automation failure: Unknown config value: {}".format(_automate))
        _op = _automate
    else:
        # Prompts
        _ans = prompt_startup()
        _op = _ans["op"]
        if _op == AUTOMATION_IMPORT_RESULT:
            _ans = prompt_import_json(import_json=_import_json)
            _import_json = _ans["filename"]
            _start_spot = None
        elif _op == AUTOMATION_START_FROM_UUID:
            _ans = prompt_start_spot(start_spot=_start_spot)
            _start_spot = _ans["uuid"]
            _import_json = None
        else:
            exit(0)

    if _start_spot:
        set_item("crawler", "start_spot", value=_start_spot)
    if _import_json:
        set_item("import_json", value=_import_json)

    return _op


def _construct_graph_add_node(nodes: list[UUID], obj: UUID):
    if nodes.count(obj) == 0:
        nodes.append(obj)


def _construct_graph_add_edge(edges: list[tuple[UUID, UUID]], source: UUID, to: UUID):
    _obj: tuple[UUID, UUID] = tuple(sorted((source, to)))
    if edges.count(_obj) == 0:
        edges.insert(0, _obj)


def _construct_graph_get_data_from_laby(session: requests.Session, delay: int, uuid: UUID,
                                        leftovers: list[UUID], forbid_out: list[UUID], error_out: list[UUID]):
    def _halt(_at, _re):
        if _at >= _re:
            return True
        logging.warning("A previous request just failed! Freeze, 2 minutes.")
        freeze(delay=120)
        return False

    def _do_request():
        if crawler_request_counts >= crawler_request_maximum_counts:
            logging.warning("Maximum request counts reached. Abort.")
            leftovers.append(uuid)
            return 429, []
        return crawler_make_request_to_laby(delay=delay, session=session, uuid=_current, mode="friends")

    _retries = 3
    _attempts = 0
    _current = uuid
    while True:
        try:
            _res_t = []
            _status_t, _res_t = _do_request()
            if _status_t != 200:
                if _status_t == 403:
                    logging.error("Remote host returned 403 FORBIDDEN: 1. Blocked by Cloudflare. 2. {} hides "
                                  "friend list".format(uuid_to_str(_current)))
                    _res_t = []
                    forbid_out.append(_current)
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

    logging.error("Skipping fetching {} friend list because something did not go well".format(uuid_to_str(_current)))
    error_out.append(_current)
    return 500, []


def _construct_graph_dfs(nodes: list[UUID], edges: list[tuple[UUID, UUID]], uuid_to_ign: dict[str, str],
                         leftovers: list[UUID], forbid_out: list[UUID], error_out: list[UUID],
                         session: requests.Session, delay: int,
                         current: UUID, previous: UUID = None):

    _has_prev = previous is not None
    if _has_prev:
        _construct_graph_add_edge(edges=edges, source=current, to=previous)

    if nodes.count(current) != 0:
        return

    _construct_graph_add_node(nodes, current)

    _status, _res = _construct_graph_get_data_from_laby(delay=delay, session=session, uuid=current,
                                                        leftovers=leftovers, error_out=error_out, forbid_out=forbid_out)

    for _i in _res:
        _next = _i["uuid"]
        _obj = UUID(_next)
        _construct_graph_add_edge(edges=edges, source=_obj, to=current)

    for _i in _res:
        _next = _i["uuid"]
        _obj = UUID(_next)
        _obj_str = uuid_to_str(_obj)
        if _has_prev and _obj_str == uuid_to_str(previous):
            continue
        uuid_to_ign[_obj_str] = _i["user_name"]
        _construct_graph_dfs(nodes=nodes, edges=edges, uuid_to_ign=uuid_to_ign,
                             forbid_out=forbid_out, error_out=error_out, leftovers=leftovers,
                             delay=delay, session=session, current=_obj, previous=current)


def _construct_graph_bfs(nodes: list[UUID], edges: list[tuple[UUID, UUID]], uuid_to_ign: dict[str, str],
                         leftovers: list[UUID], forbid_out: list[UUID], error_out: list[UUID],
                         session: requests.Session, delay: int,
                         start_spot: UUID):

    _queue = bfs_pending

    _queue.append(start_spot)

    while True:
        if len(_queue) == 0:
            break
        _current = _queue[0]
        _queue.remove(_current)

        _node_present = nodes.count(_current)
        if _node_present != 0:
            continue
        _construct_graph_add_node(nodes, _current)

        _status, _res = _construct_graph_get_data_from_laby(delay=delay, session=session, uuid=_current,
                                                            leftovers=leftovers, error_out=error_out, forbid_out=forbid_out)

        for _i in _res:
            _next = _i["uuid"]
            _obj = UUID(_next)
            uuid_to_ign[uuid_to_str(_obj)] = _i["user_name"]
            _construct_graph_add_edge(edges=edges, source=_obj, to=_current)
            _queue.append(_obj)


def crawler_make_request_to_laby(session: requests.Session, delay: int, uuid: UUID,
                                 mode: Literal["friends", "profile"] = "friends") -> [int, list]:

    crawler_wait(delay)

    req = request_to_labynet(session=session, uuid=uuid, mode=mode, proxies=crawler_proxies)

    _status = req.status_code
    logging.debug(_status)
    logging.debug(req.headers)
    res = req.text
    logging.debug(res)

    crawler_req_add_count()
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


def _crawler_run(nodes: list[UUID], edges: list[tuple[UUID, UUID]], uuid_to_ign: dict[str, str],
                 leftovers: list[UUID], forbid_out: list[UUID], error_out: list[UUID],
                 session: requests.Session, delay: int,
                 start_spot: UUID):

    _uuid = start_spot
    if _uuid is None:
        raise ValueError("There's nothing.")

    logging.info("Wait 30 seconds in case 429")
    freeze(delay=30)
    _method_op = get_crawling_method()
    if _method_op == CRAWLING_DEPTH_FIRST:
        logging.debug("Depth-first crawling.")
        _construct_graph_dfs(nodes=nodes, edges=edges, uuid_to_ign=uuid_to_ign,
                             delay=delay, session=session,
                             leftovers=leftovers, forbid_out=forbid_out, error_out=error_out,
                             current=_uuid)
    elif _method_op == CRAWLING_BREADTH_FIRST:
        logging.debug("Breadth-first crawling.")
        _construct_graph_bfs(nodes=nodes, edges=edges, uuid_to_ign=uuid_to_ign,
                             delay=delay, session=session,
                             leftovers=leftovers, forbid_out=forbid_out, error_out=error_out,
                             start_spot=_uuid)
    else:
        raise ValueError("There's nothing.")

    _status, _res = crawler_make_request_to_laby(delay=delay, session=session, uuid=_uuid, mode="profile")
    _s = uuid_to_str(_uuid)
    if _status == 200:
        uuid_to_ign[_s] = _res["username"]
    else:
        uuid_to_ign[_s] = _s

    generate_graph_html(nodes, edges, uuid_to_ign)


def run():
    _op = crawler_init_prompt()

    _start_spot = get_start_spot()
    if _start_spot:
        _start_spot = UUID(_start_spot)
        logging.debug(_start_spot)
    _import_json = get_import_json()

    _nodes: list[UUID] = []
    _edges: list[tuple[UUID, UUID]] = []
    _uuid_to_ign: dict[str, str] = {}

    if _op == AUTOMATION_IMPORT_RESULT:
        _nodes, _edges, _uuid_to_ign = import_result(_import_json)
        generate_graph_html(_nodes, _edges, _uuid_to_ign)
    else:
        _delay = 5
        _leftovers: list[UUID] = []
        _forbid_out: list[UUID] = []
        _error_out: list[UUID] = []
        _session = requests.Session()
        try:
            _crawler_run(nodes=_nodes, edges=_edges, uuid_to_ign=_uuid_to_ign,
                         leftovers=_leftovers, forbid_out=_forbid_out, error_out=_error_out,
                         session=_session, delay=_delay,
                         start_spot=_start_spot)
        finally:
            save_result(nodes=_nodes, edges=_edges, uuid_to_ign=_uuid_to_ign,
                        leftovers=_leftovers, forbid_out=_forbid_out, error_out=_error_out)
