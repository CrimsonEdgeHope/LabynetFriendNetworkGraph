__all__ = [
    "save_result",
    "import_result",
    "generate_graph_html",
    "path_to_result",
    "get_ign_from_uuid",
    "CrawlerInitOpID"
]

import json
import logging
import os
import random
import time
from uuid import UUID
from pyvis.network import Network
from config import get_item, get_config_object, get_request_headers


def save_result(nodes: list[UUID], uuid_to_ign: dict[str, str], edges: list[tuple[UUID, UUID]],
                leftovers: list[UUID], forbid_out: list[UUID], error_out: list[UUID]):
    r = {
        "metadata": {
            "created_at_unix": time.time(),
            "request_headers": get_request_headers(),
            "config": get_config_object()
        },
        "leftovers": [str(i) for i in leftovers],
        "errored": {
            "forbid_out": [str(i) for i in forbid_out],
            "error_out": [str(i) for i in error_out]
        },
        "data": {
            "nodes": [str(i) for i in nodes],
            "edges": list(map(lambda _v: (str(_v[0]), str(_v[1])), edges)),
            "uuid_to_ign": {}
        }
    }
    _obj = r["data"]["uuid_to_ign"]
    for _k, _v in uuid_to_ign.items():
        _obj[_k] = _v

    _filepath = path_to_result("{}.json".format(time.strftime("%Y-%m-%d_%H-%M-%S")))
    _dirs = os.path.split(_filepath)[0]
    if _dirs:
        os.makedirs(_dirs, exist_ok=True)
    with open(_filepath, "w") as wf:
        wf.write(json.dumps(r, ensure_ascii=False, indent=2))
        logging.info("Saving result to {}".format(_filepath))


def import_result(filename: str, full: bool = False):
    _filepath = path_to_result(filename)
    nodes: list[UUID] = []
    edges: list[tuple[UUID, UUID]] = []
    uuid_to_ign: dict[str, str] = {}

    with open(_filepath, "r") as resf:
        r = json.loads(resf.read())
        nodes.extend(list(map(lambda _v: UUID(_v), r["data"]["nodes"])))
        edges.extend(list(map(lambda _v: (UUID(_v[0]), UUID(_v[1])), r["data"]["edges"])))
        for _k, _v in r["data"]["uuid_to_ign"].items():
            uuid_to_ign[_k] = _v
        if not full:
            logging.info("Importing result from {}".format(_filepath))
            return nodes, edges, uuid_to_ign

        leftovers: list[UUID] = []
        error_out: list[UUID] = []
        forbid_out: list[UUID] = []
        leftovers.extend(list(map(lambda _v: UUID(_v), r["leftovers"])))
        error_out.extend(list(map(lambda _v: UUID(_v), r["errored"]["error_out"])))
        forbid_out.extend(list(map(lambda _v: UUID(_v), r["errored"]["forbid_out"])))
        metadata: dict = r["metadata"]

    logging.info("Importing result from {}".format(_filepath))
    return nodes, edges, uuid_to_ign, leftovers, forbid_out, error_out, metadata


def generate_graph_html(nodes: list[UUID], edges: list[tuple[UUID, UUID]], uuid_to_ign: dict[str, str]):
    nt = Network(filter_menu=True,
                 select_menu=True,
                 height="{}px".format(get_item("export_height")),
                 width="{}px".format(get_item("export_width")),
                 neighborhood_highlight=True,
                 cdn_resources="remote")
    _coord = len(uuid_to_ign) * 10

    for i in nodes:
        _u = str(i)
        _u = get_ign_from_uuid(uuid_to_ign=uuid_to_ign, target=_u)
        nt.add_node(n_id=_u, label=_u,
                    x=random.Random().randint(0, _coord), y=random.Random().randint(0, _coord), size=10)

    for i in edges:
        _u0 = str(i[0])
        _u0 = get_ign_from_uuid(uuid_to_ign=uuid_to_ign, target=_u0)
        _u1 = str(i[1])
        _u1 = get_ign_from_uuid(uuid_to_ign=uuid_to_ign, target=_u1)
        nt.add_edge(_u0, _u1)
        nt.add_edge(_u1, _u0)

    nt.toggle_physics(False)
    nt.show(get_item("export_html"), local=True, notebook=False)


def path_to_result(filename: str) -> str:
    return os.path.join("result", filename)


def get_ign_from_uuid(uuid_to_ign: dict[str, str], target: str | UUID) -> str:
    _target = str(target)
    return uuid_to_ign.get(_target, _target)


class CrawlerInitOpID:
    START_FROM_UUID = "1"
    IMPORT_RESULT = "2"

    def __init__(self):
        raise NotImplementedError()
