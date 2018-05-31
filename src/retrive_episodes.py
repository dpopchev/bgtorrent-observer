#!/usr/bin/env python

import argparse
import configparser
import os
#~ my local modules
import files_lookup
import torrent_download
import logging
import logging.handlers

logger = logging.getLogger("myLogger")
logger.setLevel(logging.INFO)

fh = logging.handlers.TimedRotatingFileHandler(
    filename="Torrent_dw_mv.log",
    when="W1",
    backupCount=2
)
fh.setLevel(logging.INFO)
fh.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s/%(module)s - %(message)s")
)

logger.addHandler(fh)

parser = argparse.ArgumentParser(
    description="Retrieve which should be the next episode number"
    "try to find it on the tracker, and if it is there start downloading it"
)

#~ config file
parser.add_argument(
    "-sc", "--series_config",
    action="store",
    nargs=1,
    type=str,
    required=False,
    metavar="",
    default="retrive_episodes.config",
    dest="series_list",
    help="config from where to load info about series names, aliases and etc"
)

if __name__ == "__main__":

    args = parser.parse_args()

    config = configparser.ConfigParser()

    if type(args.series_list) is str:
        config.read(args.series_list)
    elif len(args.series_list) == 1:
        config.read(args.series_list[0])
    else:
        logger.error("Cannot load the series config file, terminating...")
        exit()

    user_ssh = ""

    if config.getboolean("DEFAULT", "remote_ssh_user"):

        user_ssh = os.path.expanduser(os.path.join("~", ".ssh", "known_hosts"))

        logger.info("Will look for keys for known hosts here {}".format(user_ssh))

        paramiko_connect = {
            "hostname": config.get("DEFAULT", "remote_host"),
            "username": config.get("DEFAULT", "remote_user"),
            "look_for_keys": True
        }
    else:

        logger.info("Will use username and password")

        paramiko_connect = {
            "hostname": config.get("DEFAULT", "remote_host"),
            "username": config.get("DEFAULT", "remote_user"),
            "password": config.get("DEFAULT", "remote_passwd")
        }

    for section in config.sections():

        rhost_path = ""

        if config.get(section, "season"):

            logger.info(
                "Checking for... {} S{:02d}".format(
                config.get(section, "name"),
                config.getint(section, "season")
            ) )

            rhost_path = os.path.join(
                config.get(section, "remote_path"),
                "Season_{:02d}".format(config.getint(section, "season"))
            )

        else:
            logger.info(
                "Checking for... {}".format(
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

        logger.info(
            "searching next in tracker with number {}".format(
                ep_next_num
            )
        )

        tname_search = ""

        if config.get(section, "season"):
            tname_search = "{} S{:02d} {}".format(
                (
                    config.get(section,"alias")
                    if config.get(section,"alias")
                    else config.get(section, "name")
                ),
                config.getint(section, "season"),
                ep_next_num
            )
        else:
            tname_search = "{} {}".format(
                (
                    config.get(section,"alias")
                    if config.get(section,"alias")
                    else config.get(section, "name")
                ),
                ep_next_num
            )

        tname, tid = torrent_download.torrent_search(
            config.get("DEFAULT", "tracker_user"),
            config.get("DEFAULT", "tracker_passwd"),
            config.get("DEFAULT", "tracker_url"),
            tname_search
        )

        if tname and tid:

            logger.info(
                "torrent found with name {} and id {}".format(tname, tid)
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

            logger.info(
                "torrent {} NOT found... ".format(tname)
            )
