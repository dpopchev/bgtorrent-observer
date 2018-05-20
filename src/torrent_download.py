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

def torrent_search( user, passwd, url, tname ):
    """
    search for <tname> torrent in <url> as <user> with password <passwd> and
    return the latest uploaded torrent name and id (found in as the second row in the
    second table)

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
    : list
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
            print("\n connection established \n")

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
                "\n\t Found\t {} \t with id \t {} \n".format(torrent_name, torrent_id)
            )
        else:
            print(
                "\n\t Nothing found for \t {} \n".format(tname)
            )

if __name__ == "__main__":

    args = parser.parse_args()

    torrent_search(args.uname[0], args.passwd[0], args.url[0], args.tname[0])





