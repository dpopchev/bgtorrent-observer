from __future__ import annotations

import enum
import tomllib
from dataclasses import dataclass, replace
from typing import Any, NamedTuple, Optional


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


def make_tracker_credentials(tracker: Tracker, config: dict[str, Any]) -> RequestCredentials:
    """make tracker credentials using configuration representation"""
    return RequestCredentials(*(config[tracker.value]['credentials'][e]
                                for e in ('user', 'password')))
