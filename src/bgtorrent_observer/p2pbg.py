from __future__ import annotations

import re
from typing import TYPE_CHECKING, Optional, cast
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import bs4
import requests

from bgtorrent_observer.observer import RequestArguments, RequestCredentials

if TYPE_CHECKING:
    from pathlib import Path

    from requests import Session

P2PBG = 'www.p2pbg.com'
P2PBG_INDEX = 'http://www.p2pbg.com/index.php'
P2PBG_DOWNLOAD = 'http://www.p2pbg.com/download.php'


def _make_login_kwargs(user: str, password: str) -> dict:
    """request keyword arguments for login"""
    return {
        'params': {'page': 'login'},
        'data': {'uid': user, 'pwd': password},
    }


def make_login_args(credentials: RequestCredentials) -> RequestArguments:
    """request arguments for login"""
    return RequestArguments(
        P2PBG_INDEX,
        _make_login_kwargs(credentials.user, credentials.password)
    )


def _make_search_kwargs(episode: str, credentials: RequestCredentials) -> dict:
    """request keyword arguments for search"""
    return {
        'params': {
            'page': 'torrents',
            'search': episode,
            'active': '1',
            'hidexxx': 'on',
        },
        'cookies': {
            'PHPSESSID': credentials.session
        },
    }


def make_search_args(episode: str, credentials: RequestCredentials) -> RequestArguments:
    """request arguments for search"""
    return RequestArguments(
        P2PBG_INDEX,
        _make_search_kwargs(episode, credentials)
    )


def _make_download_info_kwargs(torrent_id: str, credentials: RequestCredentials) -> dict:
    """request keyword arguments for search"""
    return {
        'params': {
            'page': 'torrent-details',
            'id': torrent_id
        },
        'cookies': {
            'PHPSESSID': credentials.session
        },
    }


def make_download_info_args(torrent_id: str, credentials: RequestCredentials) -> RequestArguments:
    """request arguments for download info page"""
    return RequestArguments(
        P2PBG_INDEX,
        _make_download_info_kwargs(torrent_id, credentials)
    )


def torrent_tag_filter(tag: bs4.Tag) -> bool:
    """beautiful soup filter for tag holding torrent id"""
    return tag.has_attr('onclick') and 'showPreview' in tag['onclick']


def _get_tag_attr_value(tag: bs4.Tag, attr: str) -> str:
    """get attribute value as string; function returns the first element when list"""
    if isinstance(tag[attr], list):
        return tag[attr][0]
    return tag[attr]  # type: ignore


def get_torrent_id(tag: bs4.Tag) -> Optional[str]:
    """return the torrent id from the tag"""
    onclick: str = _get_tag_attr_value(tag, 'onclick')
    show_preview: Optional[re.Match] = re.search(
        r"^showPreview\('([^']*)'\)$", onclick)
    if not show_preview:
        return None
    return show_preview.group(1)


def download_tag_filter(tag: bs4.Tag) -> bool:
    """beautiful soup filter for tag """
    return tag.name == 'a' and tag.has_attr('href') and 'download.php?' in _get_tag_attr_value(tag, 'href')


def get_download_filename(tag: bs4.Tag) -> str:
    """get the torrent filename"""
    return parse_qs(urlparse(_get_tag_attr_value(tag, 'href')).query).get('f', [None])[0]  # type: ignore


def _make_torrent_download_url(id: str, name: str) -> str:
    query = urlencode({'id': id, 'f': name})
    return urlunparse(('http', P2PBG, '/download.php', '', query, ''))


def make_download_args(torrent_id: str, torrent_name: str, credentials: RequestCredentials) -> RequestArguments:
    """download request arguments"""
    return RequestArguments(
        _make_torrent_download_url(torrent_id, torrent_name),
        {'cookies': {'PHPSESSID': credentials.session}}
    )


def download_torrent(s: Session,
                     episode: str,
                     credentials: RequestCredentials,
                     downloaddir: Path) -> None:
    """using requests session and credentials search for episode and download it if found"""
    login_args = make_login_args(credentials)
    r = s.post(login_args.url, **login_args.kwargs)
    credentials = credentials.update(
        session=requests.utils.dict_from_cookiejar(s.cookies)['PHPSESSID'])
    search_args = make_search_args(episode, credentials)
    r = s.get(search_args.url, **search_args.kwargs)
    soup = bs4.BeautifulSoup(r.content.decode(
        'utf-8', 'ignore'), 'html.parser')

    tag = cast(bs4.Tag, soup.find(torrent_tag_filter))
    torrent_id = get_torrent_id(tag)
    download_info_args = make_download_info_args(
        torrent_id, credentials)  # type: ignore
    r = s.get(download_info_args.url, **download_info_args.kwargs)
    soup = bs4.BeautifulSoup(r.content.decode(
        'utf-8', 'ignore'), 'html.parser')
    tag = cast(bs4.Tag, soup.find(download_tag_filter))
    torrent_name = get_download_filename(tag).replace("/", "_")
    download_args = make_download_args(
        torrent_id, torrent_name, credentials)  # type: ignore
    r = s.get(download_args.url, **download_args.kwargs, allow_redirects=True)
    downloaddir.joinpath(torrent_name).write_bytes(r.content)
