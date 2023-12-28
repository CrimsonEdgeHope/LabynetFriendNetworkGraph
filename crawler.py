import logging
from typing import Literal
import requests
import time
from uuid import UUID
import labynet
from config import (get_item,
                    get_start_spot,
                    get_proxies,
                    get_crawling_method,
                    get_import_json,
                    AUTOMATION_IMPORT_RESULT,
                    CRAWLING_DEPTH_FIRST, CRAWLING_BREADTH_FIRST)
from ui_prompt import *
from util import (save_result,
                  import_result,
                  generate_graph_html,
                  uuid_to_str)

__all__ = [
    "init"
]

crawler_request_counts: int = 0
crawler_proxies = get_proxies()
crawler_request_maximum_counts: int = get_item("crawler", "maximum_requests").value
crawler_delay = get_item("crawler", "delay").value
crawler_last_req_time: float | int = -1  # timestamp
crawler_follow_alt = get_item("crawler", "follow_alternatives").value
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


def _graph_node_presence(nodes: list[UUID], obj: UUID) -> bool:
    _c = nodes.count(obj)
    return _c != 0


def _construct_graph_add_node(nodes: list[UUID], obj: UUID):
    if not _graph_node_presence(nodes, obj):
        nodes.append(obj)


def _construct_graph_add_edge(edges: list[tuple[UUID, UUID]], source: UUID, to: UUID):
    _obj: tuple[UUID, UUID] = tuple(sorted((source, to)))
    if edges.count(_obj) == 0:
        edges.insert(0, _obj)


def _construct_graph_get_data_from_laby(session: requests.Session, uuid: UUID,
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
        _r = crawler_make_request_to_laby(session=session, uuid=_current, mode="friends")
        _ra = crawler_make_request_to_laby(session=session, uuid=_current, mode="accounts")
        _r[1].extend(_ra[1])
        return _r[0].status_code, _r[1]

    _retries = 3
    _attempts = 0
    _current = uuid
    while True:
        try:
            _res_t = []
            _status_t, _res_t = _do_request()
            if _status_t != 200:
                if _status_t == 403:
                    _res_t = []
                    forbid_out.append(_current)
                if _status_t >= 500:
                    _attempts += 1
                    if _halt(_attempts, _retries):
                        break
                    continue

            return _res_t
        except:
            _attempts += 1
            if _halt(_attempts, _retries):
                break

    logging.error("Skipping fetching {} friend list because something did not go well".format(uuid_to_str(_current)))
    error_out.append(_current)
    return []


def _construct_graph_dfs(nodes: list[UUID], edges: list[tuple[UUID, UUID]], uuid_to_ign: dict[str, str],
                         leftovers: list[UUID], forbid_out: list[UUID], error_out: list[UUID],
                         session: requests.Session, current: UUID, previous: UUID = None):
    _has_prev = previous is not None
    if _has_prev:
        _construct_graph_add_edge(edges=edges, source=current, to=previous)

    if _graph_node_presence(nodes, current):
        return

    _construct_graph_add_node(nodes, current)

    _res = _construct_graph_get_data_from_laby(session=session, uuid=current,
                                               leftovers=leftovers, error_out=error_out, forbid_out=forbid_out)

    for _i in _res:
        _next = _i["uuid"]
        _construct_graph_add_edge(edges=edges, source=_next, to=current)

    for _i in _res:
        _next = _i["uuid"]
        _obj_str = uuid_to_str(_next)
        if _has_prev and _obj_str == uuid_to_str(previous):
            continue
        uuid_to_ign[_obj_str] = _i["user_name"]
        _construct_graph_dfs(nodes=nodes, edges=edges, uuid_to_ign=uuid_to_ign,
                             forbid_out=forbid_out, error_out=error_out, leftovers=leftovers,
                             session=session, current=_next, previous=current)


def _construct_graph_bfs(nodes: list[UUID], edges: list[tuple[UUID, UUID]], uuid_to_ign: dict[str, str],
                         leftovers: list[UUID], forbid_out: list[UUID], error_out: list[UUID],
                         session: requests.Session, start_spot: UUID):
    _queue = bfs_pending

    _queue.append(start_spot)

    while True:
        if len(_queue) == 0:
            break
        _current = _queue[0]
        _queue.remove(_current)

        if _graph_node_presence(nodes, _current):
            continue
        _construct_graph_add_node(nodes, _current)

        _res = _construct_graph_get_data_from_laby(session=session, uuid=_current,
                                                   leftovers=leftovers,
                                                   error_out=error_out,
                                                   forbid_out=forbid_out)

        for _i in _res:
            _next = _i["uuid"]
            uuid_to_ign[uuid_to_str(_next)] = _i["user_name"]
            _construct_graph_add_edge(edges=edges, source=_next, to=_current)
            _queue.append(_next)


def crawler_make_request_to_laby(session: requests.Session, uuid: UUID,
                                 mode: Literal["friends", "profile", "accounts"] = "friends"):
    crawler_wait(delay=crawler_delay)
    if mode == "profile":
        r = labynet.profile(session=session, uuid=uuid, proxies=crawler_proxies)
    elif mode == "friends" or mode == "accounts":
        r = labynet.friend_or_alt(session=session, uuid=uuid, mode=mode, proxies=crawler_proxies)
    else:
        raise ValueError(f"What's this? ({mode})")
    crawler_req_add_count()
    return r


def crawler_run(nodes: list[UUID], edges: list[tuple[UUID, UUID]], uuid_to_ign: dict[str, str],
                leftovers: list[UUID], forbid_out: list[UUID], error_out: list[UUID],
                session: requests.Session, start_spot: UUID):
    _uuid = start_spot
    if _uuid is None:
        raise ValueError("There's nothing.")

    logging.info("Wait 30 seconds in case 429")
    freeze(delay=30)
    _method_op = get_crawling_method()
    if _method_op == CRAWLING_DEPTH_FIRST:
        logging.debug("Depth-first crawling.")
        _construct_graph_dfs(nodes=nodes, edges=edges, uuid_to_ign=uuid_to_ign,
                             session=session,
                             leftovers=leftovers, forbid_out=forbid_out, error_out=error_out,
                             current=_uuid)
    elif _method_op == CRAWLING_BREADTH_FIRST:
        logging.debug("Breadth-first crawling.")
        _construct_graph_bfs(nodes=nodes, edges=edges, uuid_to_ign=uuid_to_ign,
                             session=session,
                             leftovers=leftovers, forbid_out=forbid_out, error_out=error_out,
                             start_spot=_uuid)
    else:
        raise ValueError("There's nothing.")

    _, _res = crawler_make_request_to_laby(session=session, uuid=_uuid, mode="profile")
    _s = uuid_to_str(_uuid)
    uuid_to_ign[_s] = _res["username"]

    generate_graph_html(nodes, edges, uuid_to_ign)


def init():
    _op = crawler_init_prompt()

    _start_spot = get_start_spot(as_uuid_object=True)
    logging.debug(_start_spot)
    _import_json = get_import_json()

    _nodes: list[UUID] = []
    _edges: list[tuple[UUID, UUID]] = []
    _uuid_to_ign: dict[str, str] = {}

    if _op == AUTOMATION_IMPORT_RESULT:
        _nodes, _edges, _uuid_to_ign = import_result(_import_json)
        generate_graph_html(_nodes, _edges, _uuid_to_ign)
    else:
        logging.debug(f"Proxies: {crawler_proxies}")
        logging.debug(f"Delay: {crawler_delay}")
        logging.debug(f"Follow alt: {crawler_follow_alt}")
        _leftovers: list[UUID] = []
        _forbid_out: list[UUID] = []
        _error_out: list[UUID] = []
        _session = requests.Session()
        try:
            crawler_run(nodes=_nodes, edges=_edges, uuid_to_ign=_uuid_to_ign,
                        leftovers=_leftovers, forbid_out=_forbid_out, error_out=_error_out,
                        session=_session, start_spot=_start_spot)
        finally:
            save_result(nodes=_nodes, edges=_edges, uuid_to_ign=_uuid_to_ign,
                        leftovers=_leftovers, forbid_out=_forbid_out, error_out=_error_out)
