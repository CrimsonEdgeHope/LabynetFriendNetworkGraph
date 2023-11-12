import logging
import os
import json

__all__ = [
    "setup_logger",
    "load",
    "get",
    "get_proxies",
    "get_config"
]


_config_file_name = "config.json"

# Actual config object to be used.
_config: dict = {}

# Default config object.
_default: dict = {
    "http_proxy": "",
    "https_proxy": "",
    "maximum_requests": 1000,
}

_acceptable = str | int


def setup_logger():
    logging_pam = {
        "level": logging.DEBUG,
        "format": "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s"
    }
    logging.basicConfig(**logging_pam)


def load():
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
                if not isinstance(value, type(_default[key])):
                    raise ValueError(f"Value \"{value}\"'s type is not acceptable for key \"{key}\"")
            except KeyError:
                pass

    logging.debug(_config)


def get(key: str) -> _acceptable | None:
    _c = get_config()
    try:
        _def = _default[key]
    except KeyError:
        _def = None

    r = _c.get(key, _def)
    if r is None:
        logging.warning(f"Key \"{key}\" does not exist.")

    return r


def get_proxies() -> dict:
    return {
        "http": get("http_proxy"),
        "https": get("https_proxy")
    }


def get_config():
    return _config
