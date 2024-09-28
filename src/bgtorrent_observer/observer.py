from __future__ import annotations

import enum
import tomllib
from dataclasses import dataclass, replace
from typing import Any, Final, Iterable, NamedTuple, Optional

CREDENTIALS_FIELD: Final[str] = 'credentials'
USER_CREDENTIAL_FIELD: Final[str] = 'user'
PASSWORD_CREDENTIAL_FIELD: Final[str] = 'password'


class Tracker(enum.StrEnum):
    P2PBG = "p2pbg"
    ARENABG = "arenabg"


class RequestArguments(NamedTuple):
    """record holding arguments to make http request"""
    url: str
    kwargs: dict


@dataclass(frozen=True)
class RequestCredentials:
    """record holding session credentials"""
    user: str
    password: str
    session: Optional[str] = None

    def update(self, **changes) -> RequestCredentials:
        return replace(self, **changes)


def parse_config(config: str) -> dict[str, Any]:
    """process the configuration into dictionary"""
    return tomllib.loads(config)


def _get_credentials(entry: dict[str, str]) -> tuple[str, str]:
    """return credentials from config entry the order user, password"""
    return entry[USER_CREDENTIAL_FIELD], entry[PASSWORD_CREDENTIAL_FIELD]


def make_tracker_credentials(tracker: Tracker, config: dict[str, Any]) -> RequestCredentials:
    """make tracker credentials using configuration representation"""
    return RequestCredentials(*_get_credentials(config[tracker.value][CREDENTIALS_FIELD]))
