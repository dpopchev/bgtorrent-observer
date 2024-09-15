from typing import Any, Callable, Final

import pytest

from bgtorrent_observer import observer

CONFIG_NAME: Final[str] = "observer.config"


@pytest.fixture
def credentials(shared_datadir) -> dict[str, Any]:
    return observer.parse_config(shared_datadir.joinpath(CONFIG_NAME).read_text())


@pytest.fixture
def make_expected_user() -> Callable[[str], str]:
    def factory(tracker: str) -> str:
        return f"{tracker}user"
    return factory


@pytest.fixture
def make_expected_password() -> Callable[[str], str]:
    def factory(tracker: str) -> str:
        return f"{tracker}password"
    return factory


@pytest.mark.parametrize('tracker', observer.Tracker, ids=(e.name for e in observer.Tracker))
class TestTrackerCredentialAttributes:
    def test_user(self, credentials: dict[str, Any], tracker: observer.Tracker, make_expected_user):
        expected: observer.RequestCredentials = observer.make_tracker_credentials(
            tracker, credentials)
        assert expected.user == make_expected_user(tracker.value)

    def test_password(self, credentials: dict[str, Any], tracker: observer.Tracker, make_expected_password):
        expected: observer.RequestCredentials = observer.make_tracker_credentials(
            tracker, credentials)
        assert expected.password == make_expected_password(tracker.value)
