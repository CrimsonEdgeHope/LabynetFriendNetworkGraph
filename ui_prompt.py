__all__ = [
    "crawler_init_prompt",
    "prompt_startup",
    "prompt_import_json",
    "prompt_start_spot",
    "prompt_use_example_uuid",
    "PROMPT_USE_EXAMPLE_UUID",
    "PROMPT_QUIT"
]

import os.path
import inquirer
import pandas as pd
from config import (set_item,
                    get_start_spot,
                    get_import_json,
                    AUTOMATION_IMPORT_RESULT,
                    AUTOMATION_START_FROM_UUID,
                    get_automation_id)
from util import validate_import_json, validate_start_spot


PROMPT_QUIT = "3"
PROMPT_USE_EXAMPLE_UUID = "4"


def prompt_startup(**kwargs):
    return inquirer.prompt([inquirer.List("op", message="What to do",
                                          choices=[
                                              ("Start from an UUID", AUTOMATION_START_FROM_UUID),
                                              ("Use an example UUID and start from it", PROMPT_USE_EXAMPLE_UUID),
                                              ("Import previous result", AUTOMATION_IMPORT_RESULT),
                                              ("Quit", PROMPT_QUIT)
                                          ],
                                          default=AUTOMATION_START_FROM_UUID)])


def prompt_import_json(**kwargs):
    return inquirer.prompt([
        inquirer.Text("filename", message="Result file name",
                      default=kwargs["import_json"],
                      validate=lambda _prevans, _v: validate_import_json(_v))
    ])


def prompt_start_spot(**kwargs):
    return inquirer.prompt([
        inquirer.Text("uuid", message="Give an UUID to start from",
                      default=kwargs["start_spot"],
                      validate=lambda _prevans, _v: validate_start_spot(_v))
    ])


def prompt_use_example_uuid(**kwargs):
    if not os.path.exists("uuid-examples.csv"):
        raise FileNotFoundError("Where's my uuid example CSV?")
    _csv = pd.read_csv("uuid-examples.csv")
    _uuids = _csv["uuid"].values.tolist()
    for _v in _uuids:
        assert validate_start_spot(_v)
    return inquirer.prompt([
        inquirer.List("uuid", message="Select an UUID to start from",
                      choices=_uuids)
    ])


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
        elif _op == PROMPT_USE_EXAMPLE_UUID:
            _ans = prompt_use_example_uuid()
            _start_spot = _ans["uuid"]
            _import_json = None
        else:
            exit(0)

    if _start_spot:
        set_item("crawler", "start_spot", value=_start_spot)
    if _import_json:
        set_item("import_json", value=_import_json)

    return _op
