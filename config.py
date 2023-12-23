__all__ = [
    "load_config",
    "get_item",
    "set_item",
    "get_proxies",
    "get_config_object",
    "get_automation_id",
    "get_start_spot",
    "get_import_json",
    "get_crawling_method",
    "is_debugging",
    "get_request_headers",
    "set_request_headers",
    "CRAWLING_DEPTH_FIRST",
    "CRAWLING_BREADTH_FIRST",
    "AUTOMATION_IMPORT_RESULT",
    "AUTOMATION_START_FROM_UUID"
]

import logging
import os
import json
from types import UnionType
from typing import Type

_config_file_name = "config.json"
_acceptable_type = str | int | bool | dict | None


class ConfigItem:
    def __init__(self,
                 key: str,
                 value=None,
                 value_type: Type | UnionType = _acceptable_type,
                 validation=None):
        self._key = key
        self._value = value
        self._value_type = value_type
        assert isinstance(key, str)
        assert isinstance(value, value_type)
        if validation is not None:
            assert callable(validation)
            validation(key, value, value_type)

    @property
    def key(self) -> str:
        return self._key

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, _value):
        assert isinstance(_value, self._value_type)
        self._value = _value


_config: dict[str, ConfigItem] = {}


def serialize_config(_obj: dict[str, ConfigItem]) -> dict:
    _rs = {}
    for k, iv in _obj.items():
        assert _obj[k].key == k
        if isinstance(iv.value, dict):
            _rs[k] = serialize_config(iv.value)
        else:
            _rs[k] = iv.value

    return _rs


def deserialize_config(_obj: dict, *keys):
    for key, value in _obj.items():
        if not isinstance(key, str):
            raise ValueError(f"Found key \"{key}\" that's not a string.")
        if not isinstance(value, _acceptable_type):
            raise ValueError(f"Value \"{value}\"'s type is not acceptable.")

        _o = get_item(*keys, key)
        assert _o.key == key
        if isinstance(value, dict):
            deserialize_config(value, *keys, key)
        else:
            _o.value = value


def load_config():
    _config_obj = get_config_object()

    _config_obj["debug"] = ConfigItem("debug", False, bool)
    _config_obj["proxy"] = ConfigItem("proxy", {
        "http_proxy": ConfigItem("http_proxy", "", str | None),
        "https_proxy": ConfigItem("https_proxy", "", str | None)
    }, dict)
    _config_obj["import_json"] = ConfigItem("import_json", None, str | None)
    _config_obj["automate"] = ConfigItem("automate", None, str | None)
    _config_obj["crawler"] = ConfigItem("crawler", {
        "crawling_method": ConfigItem("crawling_method", "2", str),
        "maximum_requests": ConfigItem("maximum_requests", 10, int),
        "start_spot": ConfigItem("start_spot", None, str | None)
    }, dict)
    _config_obj["static_html_export"] = ConfigItem("static_html_export", {
        "html": ConfigItem("html", "graph.html", str),
        "graph_width": ConfigItem("graph_width", 1920, int),
        "graph_height": ConfigItem("graph_height", 1080, int)
    }, dict)

    if not os.path.exists(_config_file_name):
        with open(_config_file_name, "w", encoding="UTF-8") as wcf:
            wcf.write(json.dumps(serialize_config(_config_obj), indent=2))

    with open(_config_file_name, "r", encoding="UTF-8") as cf:
        _cfobj = json.loads(cf.read())
        deserialize_config(_cfobj)

    logging.basicConfig(
        level=logging.DEBUG if is_debugging() else logging.INFO,
        format="%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s",
        force=True
    )
    logging.debug(get_config_object(serialized=True))
    set_request_headers(is_debugging())
    logging.debug(get_request_headers())


def get_config_object(serialized=False) -> dict:
    global _config
    if serialized:
        return serialize_config(_config)
    return _config


def get_item(*keys) -> ConfigItem | None:
    assert len(keys) > 0
    _c = get_config_object()

    r = None
    for key in keys:
        try:
            o = _c[key]

        except KeyError:
            r = None
            logging.warning(f"Key \"{key}\" does not exist.")
            break

        if isinstance(o, ConfigItem):
            r = o
            if isinstance(o.value, dict):
                _c = o.value

    return r


def set_item(*keys, value):
    get_item(*keys).value = value


def get_proxies() -> dict[str, str]:
    return {
        "http": get_item("proxy", "http_proxy").value,
        "https": get_item("proxy", "https_proxy").value
    }


def get_automation_id() -> str:
    return get_item("automate").value


def get_start_spot() -> str:
    return get_item("crawler", "start_spot").value


def get_import_json() -> str:
    return get_item("import_json").value


def is_debugging() -> bool:
    return get_item("debug").value


def get_crawling_method() -> str:
    return get_item("crawler", "crawling_method").value


_request_headers = {}


def set_request_headers(debug: bool):
    global _request_headers
    _request_headers = {
        "host": "laby.net",
        "user-agent":
            "Mozilla/5.0 (compatible; LabynetFriendNetworkGraph/beta-0.1.3; +https://github.com/CrimsonEdgeHope)"
            if not debug
            else "Mozilla/5.0 (compatible; LabynetFriendNetworkGraph/beta-dev; +https://github.com/CrimsonEdgeHope)",
        "accept": "*/*"
    }


def get_request_headers() -> dict:
    global _request_headers
    return _request_headers


CRAWLING_DEPTH_FIRST = "1"
CRAWLING_BREADTH_FIRST = "2"

AUTOMATION_START_FROM_UUID = "1"
AUTOMATION_IMPORT_RESULT = "2"

# for testing purpose
if __name__ == "__main__":
    load_config()
    print("DEBUG", is_debugging())
    print("PROXY", get_proxies())
    print("START_SPOT", get_start_spot())
    print("IMPORT_JSON", get_import_json())
    print("CRAWLING METHOD", get_crawling_method())
    print("REQUEST_HEADERS", get_request_headers())
    print("AUTOMATION_ID", get_automation_id())
