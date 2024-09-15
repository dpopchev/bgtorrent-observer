from __future__ import annotations

from dataclasses import dataclass, replace
from typing import NamedTuple, Optional


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
