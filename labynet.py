__all__ = [
    "friend_or_alt",
    "profile",
    "user_endpoint"
]

import json
import logging
from json import JSONDecodeError
from typing import Literal
from uuid import UUID
import requests
from config import get_request_headers
from util import uuid_to_str


def friend_or_alt(session: requests.Session,
                  uuid: UUID,
                  mode: Literal["friends", "accounts"] = "friends",
                  **kwargs):
    _res = user_endpoint(session=session, uuid=uuid, mode=mode, **kwargs)
    _r = []
    if _res.status_code == 200:
        try:
            _r = json.loads(_res.text)
            assert isinstance(_r, list)
        except JSONDecodeError:
            _r = []
        except AssertionError:
            _r = []
    _pr = []
    for i in _r:
        _pr.append({
            "uuid": UUID(i["uuid"]),
            "user_name": i["user_name"]
        })
    return _res, _pr


def profile(session: requests.Session, uuid: UUID, full: bool = False, **kwargs):
    _res = user_endpoint(session=session, uuid=uuid, mode="profile", **kwargs)
    _r = {}
    if _res.status_code == 200:
        try:
            _r = json.loads(_res.text)
            assert isinstance(_r, dict)
            _uuid = _r["uuid"]
            _username = _r.get("username", _uuid)
            if not _username:
                _username = _uuid
            if not full:
                _r = {
                    "uuid": UUID(_uuid),
                    "username": _username
                }
            else:
                _r["uuid"] = UUID(_uuid)
                _r["username"] = _username
        except JSONDecodeError:
            _r = {}
        except AssertionError:
            _r = {}
    return _res, _r


def user_endpoint(session: requests.Session,
                  uuid: UUID,
                  mode: Literal["friends", "profile", "accounts"] = "friends",
                  **kwargs) -> requests.Response:
    _rh = get_request_headers()
    _url = "https://{}/api/v3/user/{}/{}".format(_rh["host"], uuid, mode)
    logging.info(_url)
    res = session.get(_url, proxies=kwargs["proxies"], headers=_rh)
    if res.status_code != 200:
        logging.warning(f"Remote host returned {res.status_code}")
    if res.status_code == 403:
        logging.error(f"Remote host returned 403 FORBIDDEN whilst fetching {mode} data at {uuid_to_str(uuid)}")
    if res.status_code >= 500:
        logging.warning(f"Remote host reported an internal error. ({res.status_code})")
    logging.debug(res.headers)
    logging.debug(res.text)
    return res
