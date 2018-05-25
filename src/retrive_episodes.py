#!/usr/bin/env python

import argparse
import configparser

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

    print(args.series_list[0])

    config.read(args.series_list[0])

    for _, __ in config["DEFAULT"].items():
        print(_, __)
