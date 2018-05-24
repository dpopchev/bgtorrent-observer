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

def _get_ep_full_list(user_ssh, paramiko_connect, rpath):

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

def _get_ep_latest(ep_list):

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

def _get_ep_next(ep_latest, ep_num):

    _ = ep_latest.split(ep_num)

    ep_num = "{}{}".format(ep_num[0], int(ep_num[1:])+1)

    return "".join(_[:1] + [ep_num] + _[1:]), ep_num

if __name__ == "__main__":

    args = parser.parse_args()

    user_ssh = ""

    if args.user_ssh and args.passwd:
        print("\n Cannot use both '-sp' and '-p' \n")
        exit()
    elif args.user_ssh:
        import os

        user_ssh = os.path.expanduser(os.path.join("~", ".ssh", "known_hosts"))

        paramiko_connect = {
            "hostname": args.rhost[0],
            "username": "root",
            "allow_agent": True
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

    ep_list = _get_ep_full_list(user_ssh, paramiko_connect, args.rhost_path[0])
    ep_latest, ep_num = _get_ep_latest(ep_list)
    ep_next_name, ep_next_num = _get_ep_next(ep_latest, ep_num)
