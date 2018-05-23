#!/usr/bin/env python

import argparse

parser = argparse.ArgumentParser(
    description="Look up already downloaded files on the remote machine"
    "\n\t it uses ssh by the paramiko module"
    "\n\t it logs as root user and password with '-p'"
    "\n\t it logs as root user and public key with '-key'"
)

#~ remote machine address
parser.add_argument(
    "-r", "--remote",
    action="store",
    nargs=1,
    type=str,
    required=True,
    metavar="remote host ip",
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
    metavar="remote host path to files",
    dest="rhost_path",
    help="the path on remote host, where to lookup of the latest downloaded file"
)

#~ local path to public key
parser.add_argument(
    "-k", "--key",
    action="store",
    nargs=1,
    type=str,
    required=False,
    metavar="local path to public key",
    dest="ssh_key",
    help=(
        "the path to public key for password less ssh"
        "\n\t cannot be used with '-p'"
    )
)

#~ local path to public key
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
        "\n\t cannot be used with '-k'"
    )
)

if __name__ == "__main__":

    args = parser.parse_args()

    print(args)
