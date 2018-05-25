#!/usr/bin/env python

import argparse
import configparser
import os

#~ my local modules
import files_lookup
import torrent_download

parser = argparse.ArgumentParser(
    description="Retrieve which should be the next episode number"
    "try to find it on the tracker, and if it is there start downloading it"
)

#~ config file
parser.add_argument(
    "-sc", "--series_config",
    action="store",
    nargs="+",
    type=str,
    required=True,
    metavar="",
    dest="series_list",
    help="config from where to load info about series names, aliases and etc"
)

if __name__ == "__main__":

    args = parser.parse_args()

    config = configparser.ConfigParser()

    config.read(args.series_list[0])

    user_ssh = ""

    if config.getboolean("DEFAULT", "remote_ssh_user"):
        import os

        user_ssh = os.path.expanduser(os.path.join("~", ".ssh", "known_hosts"))

        paramiko_connect = {
            "hostname": config.get("DEFAULT", "remote_host"),
            "username": config.get("DEFAULT", "remote_user"),
            "look_for_keys": True
        }
    else:
        paramiko_connect = {
            "hostname": config.get("DEFAULT", "remote_host"),
            "username": config.get("DEFAULT", "remote_user"),
            "password": config.get("DEFAULT", "remote_passwd")
        }

    for section in config.sections():

        rhost_path = ""

        if config.get(section, "season"):
            print(
                "\n Checking for... {} S{:02d}".format(
                config.get(section, "name"),
                config.getint(section, "season")
            ) )

            rhost_path = os.path.join(
                config.get(section, "remote_path"),
                "Season_{:02d}".format(config.getint(section, "season"))
            )

        else:
            print(
                "\n Checking for... {}".format(
                config.get(section, "name"),
            ) )

            rhost_path = os.path.join(
                config.get(section, "remote_path")
            )

        ep_list = files_lookup.get_ep_full_list(
            user_ssh, paramiko_connect, rhost_path
        )

        ep_latest, ep_num = files_lookup.get_ep_latest(ep_list)

        ep_next_name, ep_next_num = files_lookup.get_ep_next(ep_latest, ep_num)

        print(
            "\n\t next should be... {}"
            "\n\t searching in tracker... \n".format(
                ep_next_num
            )
        )

        tname_search = ""

        if config.get(section, "season"):
            tname_search = "{} S{:02d} {}".format(
                config.get(section, "name"),
                config.getint(section, "season"),
                ep_next_num
            )
        else:
            tname_search = "{} {}".format(
                config.get(section, "name"),
                ep_next_num
            )

        tname, tid = torrent_download.torrent_search(
            config.get("DEFAULT", "tracker_user"),
            config.get("DEFAULT", "tracker_passwd"),
            config.get("DEFAULT", "tracker_url"),
            tname_search
        )

        if tname and tid:

            print(
                "\n\t torrent found... "
                "\n\t\t name: {}"
                "\n\t\t id: {}".format(tname, tid)
            )

            fpath = torrent_download.torrent_download(
                config.get("DEFAULT", "tracker_user"),
                config.get("DEFAULT", "tracker_passwd"),
                config.get("DEFAULT", "tracker_url"),
                tname,
                tid
            )

            torrent_download.torrent_start(fpath)
        else:

            print(
                "\n\t torrent NOT found... "
            )
