__all__ = [
    "prompt_startup",
    "prompt_import_json",
    "prompt_start_spot"
]

import inquirer
from config import AUTOMATION_START_FROM_UUID, AUTOMATION_IMPORT_RESULT
from util import validate_import_json, validate_start_spot


def prompt_startup(**kwargs):
    return inquirer.prompt([inquirer.List("op", message="What to do",
                                          choices=[
                                              ("Start from an UUID", AUTOMATION_START_FROM_UUID),
                                              ("Import previous result", AUTOMATION_IMPORT_RESULT),
                                              ("Quit", "3")
                                          ],
                                          default=AUTOMATION_IMPORT_RESULT)])


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
