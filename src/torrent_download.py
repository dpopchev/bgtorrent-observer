#!/usr/bin/env python

import argparse

parser = argparse.ArgumentParser(
    description="Create connection to http://alien.org/ with provided credentials"
    "search for latests episodes and add the to transmission to be downloaded"
)

#~ username
parser.add_argument(
    "-u", "--user",
    action="store",
    nargs=1,
    type=str,
    required=True,
    metavar="username",
    dest="uname",
    help="user name to be used"
)

#~ password
parser.add_argument(
    "-p", "--password",
    action="store",
    nargs=1,
    type=str,
    required=True,
    metavar="password",
    dest="passwd",
    help="password for the user"
)

#~ url for the site
parser.add_argument(
    "-s", "--site",
    action="store",
    nargs=1,
    type=str,
    required=True,
    metavar="http://tracker.url/",
    dest="url",
    help="url of the tracker"
)

#~ torrent name to search
parser.add_argument(
    "-t", "--torrent",
    action="store",
    nargs=1,
    type=str,
    required=True,
    metavar="torrent name",
    dest="tname",
    help="url of the tracker"
)


def torrent_search(user, passwd, url, tname):
    """
    search for <tname> torrent in <url> as <user> with password <passwd> and
    return the latest uploaded torrent name and id (found in as the second
    row in the second table)

    Parameteres
    -----------
    user: string
        the user name

    passwd: string
        the password

    url: string
        the tracker url

    tname: string
        the torrent name to be searched for

    Returns
    -------
    : tuple
        [0]: string
            the torrent name found, if nothing found it will be empty string

        [1]: string
            the id of the found torrent, if nothing found it will be empty string
    """

    import requests

    from lxml import html
    from urllib.parse import urlparse, parse_qs

    with requests.Session() as s:

        #~ login with credentials
        p = s.post(
            url,
            params={
                "page": "login"
            },
            data={
                "uid": user,
                "pwd": passwd
            }
        )

        if p.status_code != requests.codes.ok:
            print("\n DID NOT CONNECT TO SITE \n")
            exit()
        else:
            print("\n connection established, torrent search \n")

        #~ make a search for the latest uploaded torrent
        p = s.get(
            url,
            params={
                "page": "torrents",
                "search": tname,
                "active": "1",
                "order": "3",
                "by": "2"
            }
        )

        tree = html.fromstring(p.content)

        try:
            torrent_name = tree.xpath("//tr[2]/td[2]/a/text()")[0]

            torrent_id = parse_qs(
                urlparse(
                    tree.xpath("//tr[2]/td[2]/a/@href")[0]
                ).query
            ).get("id", [""])[0]
        except:
            torrent_name = ""
            torrent_id = ""

        if torrent_name and torrent_id:
            print(
                "\n\t Found \t {} \t with id \t {} \n".format(
                    torrent_name, torrent_id)
            )
        else:
            print(
                "\n\t Nothing found for \t {} \n".format(tname)
            )

        return torrent_name, torrent_id


def torrent_download(user, passwd, url, tname, tid):
    """
    download the torrent with <tname> and id <tid> from tracker <url>
    as user <user> with password <passwd>

    Parameters
    ----------
    user: string
        the user

    passwd: string
        the password

    url: string
        the tracker url

    tname: string
        torrent name

    tid: string
        torrent id

    Returns
    -------
    : string
      Return the full path to the torrent
    """
    import requests

    with requests.Session() as s:

        #~ login with credentials
        p = s.post(
            url,
            params={
                "page": "login"
            },
            data={
                "uid": user,
                "pwd": passwd
            }
        )

        if p.status_code != requests.codes.ok:
            print("\n DID NOT CONNECT TO SITE \n")
            exit()
        else:
            print("\n connection established, torrent download \n")

        p = s.get(
            url + "download.php",
            params={
                "id": tid,
                "f": tname + ".torrent"
            }
        )

        with open("/tmp/{}.torrent".format(tname), "wb") as f:
            f.write(p.content)

        print("\n\t Find file at /tmp/{}.torrent \n".format(tname))

        return "/tmp/{}.torrent".format(tname)


def torrent_start(fpath):

    import transmissionrpc
    import os

    tc = transmissionrpc.Client("localhost", port=9091, timeout=1)

    tc.add_torrent(fpath)

    try:
        os.remove(fpath)
    except OSError:
        pass


if __name__ == "__main__":

    args = parser.parse_args()

    tname, tid = torrent_search(
        args.uname[0], args.passwd[0], args.url[0], args.tname[0]
    )

    if tname and tid:
        fpath = torrent_download(
            args.uname[0], args.passwd[0], args.url[0], tname, tid
        )

        torrent_start(fpath)
