import logging
import os
import json

__all__ = [
    "load_config",
    "get_item",
    "set_item",
    "get_proxies",
    "get_config_object"
]


_config_file_name = "config.json"

# Actual config object to be used.
_config: dict = {}

# Default config object.
_default: dict = {
    "http_proxy": "",
    "https_proxy": "",
    "maximum_requests": 100,
    "debug": False,
    "export_html": "graph.html",
    "export_width": 1920,
    "export_height": 1080,
    "start_spot": None,
    "import_json": None,
    "automate": None,
    "crawling_method": "2"
}

_acceptable = str | int


def load_config():
    global _config

    if not os.path.exists(_config_file_name):
        with open(_config_file_name, "w", encoding="UTF-8") as wcf:
            wcf.write(json.dumps(_default, indent=2))

    with open(_config_file_name, "r", encoding="UTF-8") as cf:
        _config = json.loads(cf.read())
        for key, value in _config.items():
            if not isinstance(key, str):
                raise ValueError(f"Found key \"{key}\" that's not a string.")
            if not isinstance(value, _acceptable):
                raise ValueError(f"Value \"{value}\"'s type is not acceptable.")
            try:
                if not isinstance(None, type(_default[key])) and not isinstance(value, type(_default[key])):
                    raise ValueError(f"Value \"{value}\"'s type is not acceptable for key \"{key}\"")
            except KeyError:
                pass
    logging_pam = {
        "level": logging.DEBUG if get_item("debug") else logging.INFO,
        "format": "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s"
    }
    logging.basicConfig(**logging_pam)
    logging.debug(_config)


def get_item(key: str) -> _acceptable | None:
    _c = get_config_object()
    try:
        _def = _default[key]
    except KeyError:
        _def = None

    r = _c.get(key, _def)
    if r is None:
        logging.warning(f"Key \"{key}\" does not exist.")

    return r


def set_item(key: str, value: _acceptable | None):
    logging.debug("{} {}".format(key, value))
    _config[key] = value
    logging.debug(_config)


def get_proxies() -> dict:
    return {
        "http": get_item("http_proxy"),
        "https": get_item("https_proxy")
    }


def get_config_object():
    return _config
