import logging
import re
import sys
from typing import Any
from util import import_result
import config
from result_json import result_json_prompt


__all__ = [
    "fire"
]

mark = True


def fire(import_json: str = None):
    def check_duplicates(list_obj: list[Any], prefix: str, verbose: bool = False):
        logging.info(f"Checking duplicates of {prefix}")
        expect_count = 1

        def _f():
            global mark
            _d = True
            for i, v in enumerate(list_obj):
                if verbose:
                    logging.info(f"{prefix} no.{i}, value {v}")
                _c = list_obj.count(v)
                if _c > expect_count:
                    logging.error(f"DUPLICATE: {prefix}, at no.{i}, value {v}, {_c} entities, expected {expect_count}")
                    _d = False
            if (not _d) and mark:
                mark = False
            return None if _d else _d

        return _f() is None

    if import_json is not None:
        nodes, edges, uuid_to_ign, leftovers, forbid_out, error_out, metadata = import_result(import_json, full=True)
    else:
        import_json, (nodes, edges, uuid_to_ign, leftovers, forbid_out, error_out, metadata) = result_json_prompt()

    logging.warning("""
<============================>
Checking {import_json}
<============================>
    """.format(import_json=import_json))

    logging.info(metadata)

    if not check_duplicates(nodes, "Nodes"):
        logging.error("Failure at Nodes")
    if not check_duplicates(edges, "Edges"):
        logging.error("Failure at Edges")
    if not check_duplicates(leftovers, "Leftovers"):
        logging.error("Failure at Leftovers")
    if not check_duplicates(forbid_out, "FORBID_OUT"):
        logging.error("Failure at FORBID_OUT")
    if not check_duplicates(error_out, "ERROR_OUT"):
        logging.error("Failure at ERROR_OUT")

    logging.warning("""
<============================>
End of checking {import_json}
<============================>""".format(import_json=import_json))


if __name__ == "__main__":
    config.load_config()
    if len(sys.argv) >= 2:
        for v in sys.argv[1:]:
            if re.match(r"^[0-9a-zA-Z\_\-]+\.json$", v):
                fire(v)
    else:
        fire()
    if not mark:
        exit(1)
