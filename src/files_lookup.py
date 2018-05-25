#!/usr/bin/env python

import argparse

_ssh_pswdless = "http://www.linuxproblem.org/art_9.html"
_ssh_paramiko = "https://www.minvolai.com/how-to-ssh-in-python-using-paramiko/"

parser = argparse.ArgumentParser(
    description="Look up already downloaded files on the remote machine"
    "\n\t it uses ssh by the paramiko module"
    "\n\t it logs as root user and password with '-p'"
    "\n\t boolean, it trys to retrieve private key files from user home folder"
    "\n\t for paswordless ssh check here {}"
    "\n\t for paramiko check here {}".format(_ssh_pswdless, _ssh_paramiko)
)

#~ remote machine address
parser.add_argument(
    "-r", "--remote",
    action="store",
    nargs=1,
    type=str,
    required=True,
    metavar="",
    dest="rhost",
    help="the remote host ip or alias if added in /etc/hosts"
)

#~ path to where to look up
parser.add_argument(
    "-rp", "--rpath",
    action="store",
    nargs=1,
    type=str,
    required=True,
    metavar="",
    dest="rhost_path",
    help="the path on remote host, where to lookup of the latest downloaded file"
)

#~ path to where to look up
parser.add_argument(
    "-rpath_s", "--rpath_season",
    action="store",
    nargs=1,
    type=int,
    required=False,
    metavar="",
    dest="rhost_path_season",
    help="the current season, if not present presumes no seasons and will not"
    "search for folder with name of type Season_02 in rhost_path"
)

#~ boolean variable wheter to use user local .ssh folder
parser.add_argument(
    "-us", "--user_ssh",
    action="store",
    nargs=1,
    type=bool,
    required=False,
    metavar="",
    dest="user_ssh",
    help=(
        "try to use the user .ssh to discover private keys"
        "\n\t cannot be used with '-p'"
        "\n\t required if '-p' missing"
    )
)

#~ password for the user
parser.add_argument(
    "-p", "--password",
    action="store",
    nargs=1,
    type=str,
    required=False,
    metavar="password to use for the ssh",
    dest="passwd",
    help=(
        "the root password for the remote hosts"
        "\n\t cannot be used with '-sp'"
        "\n\t required if '-sp' missing"
    )
)

def get_ep_full_list(user_ssh, paramiko_connect, rpath):
    """
    get the full list of the episodes contained in an remote directory using
    paramiko module; depending or n the contented in <usr_ssh> it will connect
    either by username/password or attempting to use known private key

    Parameters
    ----------
    user_ssh: string
        if string is not empty, should point to users .ssh and will attempt to
        automatically connect by using pre done private/pub key to the remote
        server

        if string is empty, then username/password method is used

    paramiko_connect: dic
        if <user_ssh> string is empty, the string should look like this:
            {
                "hostname": <hostname>,
                "username": <username",
                "password": <password>
            }

        if <user_ssh> points to valid .ssh with known_hosts file should like this
            {
                "hostname": <hostname>,
                "username": <username>,
                "look_for_keys: True

    rpath: string
        the remote path containing all episodes to retrive

    Returns
    -------
    : list
        list of file names containing on remote server
    """


    import paramiko

    with paramiko.SSHClient() as ssh:

        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if user_ssh:
            ssh.load_host_keys(user_ssh)

        ssh.connect(**paramiko_connect)

        stdin, stdout, stderr = ssh.exec_command(
            "find {} -type f -exec basename {{}} \;".format(rpath)
        )

        return stdout.readlines()

def get_ep_latest(ep_list):
    """
    for provided <ep_list>, it will find the latest episode, which means the one
    with the biggest number; it works by searching something like S01E12, and
    will return Name_of_episode_S01E12 and its number E12

    Parameters
    ----------
    ep_list: list
        list of all episodes of single season

    Returns
    -------
    : tuple
        : string
            the name of the latest episode

        : string
            the episode number in the form E10
    """

    import re

    rexp = re.compile("(?:[Ss]\d+)?([Ee]\d+)")

    latest_ep_num = 0
    latest_ep_i = 0

    for i, val in enumerate(ep_list):

        m = rexp.search(val)

        _, *__ = m.groups()

        if latest_ep_num < int(_[1:]):
            latest_ep_num = int(_[1:])
            ep_num = _
            latest_ep_i = i

    return ep_list[latest_ep_i], ep_num

def get_ep_next(ep_latest, ep_num):
    """
    for provided episode name and number return which should be the next episode

    Parameters
    ----------
    ep_latest: string
        the full name of the episode

    ep_num: the current episode number

    Returns
    -------
    : string
        the name of the next episode, just incremeted number after E

    """
    _ = ep_latest.split(ep_num)

    ep_num = "{}{:02d}".format(ep_num[0], int(ep_num[1:])+1)

    return "".join(_[:1] + [ep_num] + _[1:]), ep_num

if __name__ == "__main__":

    import os

    args = parser.parse_args()

    user_ssh = ""

    if args.user_ssh and args.passwd:
        print("\n Cannot use both '-sp' and '-p' \n")
        exit()
    elif args.user_ssh:

        user_ssh = os.path.expanduser(os.path.join("~", ".ssh", "known_hosts"))

        paramiko_connect = {
            "hostname": args.rhost[0],
            "username": "root",
            "look_for_keys": True
        }

    elif args.passwd:
        paramiko_connect = {
            "hostname": args.rhost[0],
            "username": "root",
            "password": args.passwd[0]
        }
    else:
        print("\n One of '-k' or '-p' required \n")
        exit()

    if args.rhost_path_season:
        rhost_path = os.path.join(
            args.rhost_path[0],
            "Season_{:02d}".format(args.rhost_path_season[0])
        )
    else:
        rhost_path = args.rhost_path[0]

    ep_list = get_ep_full_list(user_ssh, paramiko_connect, rhost_path)
    ep_latest, ep_num = get_ep_latest(ep_list)
    ep_next_name, ep_next_num = get_ep_next(ep_latest, ep_num)
