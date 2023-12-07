__all__ = [
    "request_headers",
    "save_result",
    "import_result",
    "generate_graph_html"
]

import json
import logging
import os
import random
import time
from uuid import UUID
from pyvis.network import Network
import config

request_headers = {
    "host": "laby.net",
    "user-agent": "Mozilla/5.0 (compatible; LabynetFriendNetworkGraph/beta-0.1.2; +https://github.com/CrimsonEdgeHope)",
    "accept": "*/*"
}


def save_result(nodes: list[UUID], uuid_to_ign: dict[str, str], edges: list[tuple[UUID, UUID]],
                leftovers: list[UUID], forbid_out: list[UUID], error_out: list[UUID]):
    r = {
        "metadata": {
            "created_at_unix": time.time(),
            "request_headers": request_headers,
            "config": config.get_config_object()
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

    _filepath = os.path.join("result", "{}.json".format(time.strftime("%Y-%m-%d-%H-%M-%S")))
    _dirs = os.path.split(_filepath)[0]
    if _dirs:
        os.makedirs(_dirs, exist_ok=True)
    with open(_filepath, "w") as wf:
        wf.write(json.dumps(r, ensure_ascii=False, indent=2))
        logging.info("Saving result to {}".format(_filepath))


def import_result(filename: str):
    _filepath = os.path.join("result", filename)
    nodes: list[UUID] = []
    edges: list[tuple[UUID, UUID]] = []
    uuid_to_ign: dict[str, str] = {}
    with open(_filepath, "r") as resf:
        r = json.loads(resf.read())
        r = r["data"]
        nodes.extend(list(map(lambda _v: UUID(_v), r["nodes"])))
        edges.extend(list(map(lambda _v: (UUID(_v[0]), UUID(_v[1])), r["edges"])))
        for _k, _v in r["uuid_to_ign"].items():
            uuid_to_ign[_k] = _v

    logging.info("Importing result from {}".format(_filepath))
    return nodes, edges, uuid_to_ign


def generate_graph_html(nodes: list[UUID], edges: list[tuple[UUID, UUID]], uuid_to_ign: dict[str, str]):
    nt = Network(filter_menu=True,
                 select_menu=True,
                 height="{}px".format(config.get_item("export_height")),
                 width="{}px".format(config.get_item("export_width")),
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
    nt.show(config.get_item("export_html"), local=True, notebook=False)
