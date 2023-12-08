import json
import os
import inquirer
import time
import config
from util import import_result, path_to_result, CrawlerInitOpID, get_ign_from_uuid


def _validate_import_json(_v):
    return os.path.exists(path_to_result(_v))


if __name__ == "__main__":
    config.load_config()
    _import_json = config.get_import_json()
    if config.get_automate() != CrawlerInitOpID.IMPORT_RESULT:
        _ans = inquirer.prompt([
            inquirer.Text("filename", message="Result file name",
                          default=_import_json,
                          validate=lambda _prevans, _v: _validate_import_json(_v))
        ])
        _import_json = _ans["filename"]
    elif not _validate_import_json(_import_json):
        raise ValueError("Invalid import_json value.")

    nodes, edges, uuid_to_ign, _leftovers, _forbid_out, _error_out, _metadata = import_result(_import_json, full=True)

    len_of_nodes = len(nodes)
    len_of_edges = len(edges)
    len_of_igns = len(uuid_to_ign)
    len_of_leftovers = len(_leftovers)
    len_of_error_out = len(_error_out)
    len_of_forbid_out = len(_forbid_out)

    print("""
Result {import_json}:
Created at {created_at_unix} UTC

Web request headers:
{request_headers}

Config:
{config_object}
    """.format(import_json=_import_json,
               created_at_unix=time.strftime("%Y/%m/%d %H:%M:%S", time.gmtime(_metadata["created_at_unix"])),
               request_headers=_metadata["request_headers"],
               config_object=_metadata["config"]))

    if len_of_nodes <= 0:
        exit(0)

    print("""According to this copy of result, the crawler tracked {len_of_nodes} Minecraft player{_s} that have registered on laby.net.""".format(len_of_nodes=len_of_nodes, _s="" if len_of_nodes == 1 else "s"))

    _start_spot = _metadata["config"].get("start_spot", None)
    if _start_spot:
        _start_spot_name = get_ign_from_uuid(uuid_to_ign=uuid_to_ign, target=_start_spot)
        print("""Tracking began at the player{pn} with uuid {uuid}""".format(
            pn="" if _start_spot_name == _start_spot else f" named \"{_start_spot_name}\",",
            uuid=_start_spot
        ))

    if len_of_forbid_out > 0:
        print("""{len_of_forbid_out}/{len_of_nodes} hide their full friendship data (or the crawler was blocked by Cloudflare that returned 403 rather than laby.net itself)""".format(len_of_nodes=len_of_nodes,
                   len_of_forbid_out=len_of_forbid_out))

    if len_of_error_out > 0:
        print("""{len_of_error_out}/{len_of_nodes} have no result because the crawler encountered some issues that prevented the crawler from getting a web response, probably it was due to network connection issues. """.format(len_of_error_out=len_of_error_out, len_of_nodes=len_of_nodes))

    if len_of_edges > 0:
        print("""In all the {len_of_nodes} Minecraft player{_ps} on laby.net, {len_of_edges} friendship connection{_fs} discovered. {len_of_igns}/{len_of_nodes} username{_igs} fetched.""".format(len_of_nodes=len_of_nodes, len_of_edges=len_of_edges, len_of_igns=len_of_igns,
                   _ps="" if len_of_nodes == 1 else "s",
                   _fs="s are" if len_of_edges != 1 else " is",
                   _igs=" is" if len_of_igns == 1 else "s are"))

    if len_of_leftovers > 0:
        print("""Due to limitation, {len_of_leftovers} player{_s} yet to be tracked.""".format(
            len_of_leftovers=len_of_leftovers,
            _s=" is" if len_of_leftovers == 1 else "s are"
        ))
