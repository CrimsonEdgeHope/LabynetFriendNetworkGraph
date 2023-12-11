import re
import sys
import config
from result_json import result_json_prompt
from util import get_ign_from_uuid, path_to_result, import_result, uuid_to_str

__all__ = [
    "fire"
]

LABEL_MINECRAFT_PLAYER = "MINECRAFT_PLAYER"
LABEL_LABY_NET_USER = "LABY_NET_USER"
EDGE_RELATION_LABY_FRIEND = "LABY_FRIEND"


def save_cql(filename: str, content: str):
    with open(filename, "w") as f:
        f.write(content)


def fire(import_json: str = None):
    if import_json is not None:
        nodes, edges, uuid_to_ign = import_result(import_json)
    else:
        import_json, (nodes, edges, uuid_to_ign) = result_json_prompt(full=False)

    create_nodes_cql = []
    for n in nodes:
        create_nodes_cql.append("CREATE (mc{uuid_no_dash}:{label_mcp}:{label_lnu} {node_cql})".format(
            label_mcp=LABEL_MINECRAFT_PLAYER, label_lnu=LABEL_LABY_NET_USER,
            uuid_no_dash=uuid_to_str(n, no_dash=True),
            node_cql="{" + "name: \"{name}\", uuid: \"{uuid}\"".format(
                name=get_ign_from_uuid(uuid_to_ign=uuid_to_ign, target=n), uuid=uuid_to_str(n)) + "}"))

    create_nodes_cql = '\n'.join(create_nodes_cql)
    create_edges_cql = []
    for i, e in enumerate(edges):
        create_edges_cql.append("CREATE (mc{from_uuid_no_dash})-[:{relation_laf}]->(mc{to_uuid_no_dash})".format(
            relation_laf=EDGE_RELATION_LABY_FRIEND, from_uuid_no_dash=uuid_to_str(e[0], no_dash=True),
            to_uuid_no_dash=uuid_to_str(e[1], no_dash=True)
        ))

    create_edges_cql = '\n'.join(create_edges_cql)

    save_cql(path_to_result(f"{import_json}.cql"), create_nodes_cql + "\n" + create_edges_cql)


if __name__ == "__main__":
    config.load_config()
    if len(sys.argv) >= 2:
        for v in sys.argv[1:]:
            if re.match(r"^[0-9a-zA-Z\_\-]+\.json$", v):
                fire(v)
    else:
        fire()
