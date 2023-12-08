import config
from result_json import result_json_prompt
from util import get_ign_from_uuid, path_to_result

LABEL_MINECRAFT_PLAYER = "MINECRAFT_PLAYER"
LABEL_LABY_NET_USER = "LABY_NET_USER"
EDGE_RELATION_LABY_FRIEND = "LABY_FRIEND"


def save_cql(filename: str, content: str):
    with open(filename, "w") as f:
        f.write(content)


if __name__ == "__main__":
    config.load_config()

    import_json, (nodes, edges, uuid_to_ign, leftovers, forbid_out, error_out, metadata) = result_json_prompt()

    create_nodes_cql = []
    for n in nodes:
        create_nodes_cql.append("(:{label_mcp}:{label_lnu} {node_cql})".format(
            label_mcp=LABEL_MINECRAFT_PLAYER, label_lnu=LABEL_LABY_NET_USER,
            node_cql="{" + "name: \"{name}\", uuid: \"{uuid}\"".format(
                name=get_ign_from_uuid(uuid_to_ign=uuid_to_ign, target=n), uuid=str(n)) + "}"))
    create_nodes_cql = "CREATE {0}".format(",".join(create_nodes_cql))

    create_edges_cql = []
    for i, e in enumerate(edges):
        create_edges_cql.insert(0,
                                "MATCH (from{fi}:{label_lnu}), (to{ti}:{label_lnu}) "
                                "WHERE from{fi}.uuid=\"{from_uuid}\" AND to{ti}.uuid=\"{to_uuid}\""
                                .format(fi=i, ti=i,
                                        label_lnu=LABEL_LABY_NET_USER,
                                        from_uuid=e[0], to_uuid=e[1]))
        create_edges_cql.append("CREATE (from{fi})-[:{relation_laf}]->(to{ti})".format(
            fi=i, ti=i, relation_laf=EDGE_RELATION_LABY_FRIEND
        ))

    create_edges_cql = '\n'.join(create_edges_cql)

    save_cql(path_to_result(f"{import_json}_create_nodes.cql"), create_nodes_cql)
    save_cql(path_to_result(f"{import_json}_create_edges.cql"), create_edges_cql)
