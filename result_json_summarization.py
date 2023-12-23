import re
import sys
import time
import inquirer
import config
from config import AUTOMATION_IMPORT_RESULT
from util import import_result, get_ign_from_uuid, validate_import_json

__all__ = [
    "result_json_prompt",
    "fire"
]


def result_json_prompt(full: bool = True):
    _import_json = config.get_import_json()
    if config.get_automation_id() != AUTOMATION_IMPORT_RESULT:
        _ans = inquirer.prompt([
            inquirer.Text("filename", message="Result file name",
                          default=_import_json,
                          validate=lambda _prevans, _v: validate_import_json(_v))
        ])
        _import_json = _ans["filename"]
    elif not validate_import_json(_import_json):
        raise ValueError("Invalid import_json value.")

    return _import_json, import_result(_import_json, full=full)


def fire(import_json: str = None):
    if import_json is None:
        import_json, (nodes, edges, uuid_to_ign, leftovers, forbid_out, error_out, metadata) = result_json_prompt()
    else:
        nodes, edges, uuid_to_ign, leftovers, forbid_out, error_out, metadata = import_result(import_json, full=True)

    len_of_nodes = len(nodes)
    len_of_edges = len(edges)
    len_of_igns = len(uuid_to_ign)
    len_of_leftovers = len(leftovers)
    len_of_error_out = len(error_out)
    len_of_forbid_out = len(forbid_out)

    print("""
<============================>
Summarization of {import_json}
<============================>""".format(import_json=import_json))

    print("""{import_json} was created at {created_at_unix} UTC

Web request headers:
{request_headers}

Config:
{config_object}
        """.format(import_json=import_json,
                   created_at_unix=time.asctime(time.gmtime(metadata["created_at_unix"])),
                   request_headers=metadata["request_headers"],
                   config_object=metadata["config"]))

    if len_of_nodes <= 0:
        print("Nothing to summarize, abort...")
        exit(0)

    print(
        """According to this copy of result, the crawler tracked {len_of_nodes} Minecraft player{_s} that have been registered on laby.net.""".format(
            len_of_nodes=len_of_nodes, _s="" if len_of_nodes == 1 else "s"))

    _start_spot = metadata["config"]["crawler"].get("start_spot", None)
    if _start_spot:
        _start_spot_name = get_ign_from_uuid(uuid_to_ign=uuid_to_ign, target=_start_spot)
        print("""Tracking began at the player{pn} with uuid {uuid}""".format(
            pn="" if _start_spot_name == _start_spot else f" named \"{_start_spot_name}\",",
            uuid=_start_spot
        ))

    if len_of_forbid_out > 0:
        print(
            """{len_of_forbid_out}/{len_of_nodes} hide their full friendship data (or the crawler was blocked by Cloudflare that returned 403 rather than laby.net itself)""".format(
                len_of_nodes=len_of_nodes,
                len_of_forbid_out=len_of_forbid_out))

    if len_of_error_out > 0:
        print(
            """{len_of_error_out}/{len_of_nodes} have no result because the crawler encountered some issues that prevented the crawler from getting a web response, probably it was due to network connection issues. """.format(
                len_of_error_out=len_of_error_out, len_of_nodes=len_of_nodes))

    if len_of_edges > 0:
        print(
            """In all the {len_of_nodes} Minecraft player{_ps} on laby.net, {len_of_edges} friendship connection{_fs} discovered. {len_of_igns}/{len_of_nodes} username{_igs} fetched.""".format(
                len_of_nodes=len_of_nodes, len_of_edges=len_of_edges, len_of_igns=len_of_igns,
                _ps="" if len_of_nodes == 1 else "s",
                _fs="s are" if len_of_edges != 1 else " is",
                _igs=" is" if len_of_igns == 1 else "s are"))

    if len_of_leftovers > 0:
        print("""Due to limitation, {len_of_leftovers} player{_s} yet to be tracked.""".format(
            len_of_leftovers=len_of_leftovers,
            _s=" is" if len_of_leftovers == 1 else "s are"
        ))

    print("""
<============================>
End of summarizing {import_json}
<============================>""".format(import_json=import_json))


if __name__ == "__main__":
    config.load_config()
    if len(sys.argv) >= 2:
        for v in sys.argv[1:]:
            if re.match(r"^[0-9a-zA-Z\_\-]+\.json$", v):
                fire(v)
    else:
        fire()
