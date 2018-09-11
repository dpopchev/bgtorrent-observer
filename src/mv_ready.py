#!/usr/bin/env python

import transmissionrpc
import paramiko
import argparse
import configparser
import os
import subprocess
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
    description="Check for finished downloads, if any and they are not moved,"
    "move them and clean"
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
    help="config file to know which folders we keep an eye on"
)

if __name__ == "__main__":

    args = parser.parse_args()

    config = configparser.ConfigParser()

    if type(args.series_list) is str:
        config.read(args.series_list)
        logger.debug("Using default config file {}".format(args.series_list))

    elif len(args.series_list) == 1:
        config.read(args.series_list[0])
        logger.debug("Using config file {}".format(args.series_list[0]))

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

    list_dirs = []

    for section in config.sections():

        list_dirs.append(config.get(section, "remote_path"))

    tc = transmissionrpc.Client("localhost", port=9091, timeout=1)

    for _ in tc.get_files():

        t = tc.get_files()[_]

        if len(t.keys()) > 1:
            logger.warning(
                "Torrent {} has more than 1 file, unlikely to be series".format(
                    len(t.keys())
                )
            )
            continue
        else:
            t = t[0]

        if t["completed"] == t["size"]:
            logger.info("Torrent {} is completed".format(t["name"]))

            with paramiko.SSHClient() as ssh:

                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                if user_ssh:
                    ssh.load_host_keys(user_ssh)

                ssh.connect(**paramiko_connect)

                stdin, stdout, stderr = ssh.exec_command(
                    "find {} -type f -name {}".format(
                        " ".join(list_dirs), t["name"].strip().replace(" ", "\ ")
                    )
                )

                ssh_stderr = stderr.readlines()

                #~ read the first line only, as it is the one containing path
                ssh_stdout = stdout.readline()

                if ssh_stderr:

                    logger.error("SSH find ended with errors, line by line they are:")

                    for _, __ in enumerate(ssh_stderr):
                        logger.error("{}. {}".format(_, __))

                    logger.error(
                        "skipping rest of actions for torrent {}".format(
                            _
                        )
                    )

                    continue

                if ssh_stdout:

                    logger.info("SSH find got this file {}".format(ssh_stdout))

                    if config.getboolean("DEFAULT", "local_delete"):

                        logger.info("Remove local files is YES, removing...")

                        tc.remove_torrent(_, delete_data=True)
                    else:
                        logger.info("Remove local files is NO, preserving...")
                else:

                    logger.info("SSH find did not found any file")

                    stdin, stdout, stderr = ssh.exec_command(
                        "find {} -type f -name {}* | head -n1".format(
                            " ".join(list_dirs),
                            t["name"].split("E")[0].strip().replace(" ", "\ ")
                        )
                    )

                    ssh_stderr = stderr.readlines()
                    #~ read the first line only, as it is the one containing path
                    #~ it will get only the directory path
                    rpath_cp = os.path.dirname(stdout.readline())

                    #~ if it has any errors
                    if ssh_stderr:
                        logger.error("SSH find ended with errors, line by line they are:")

                        for _, __ in enumerate(ssh_stderr):
                            logger.error("\t {}. {}".format(_, __))

                        logger.error("skipping rest of actions for this torrent")

                        continue

                    #~ if there is an remote path, not something like empty string
                    elif rpath_cp:

                        #~ get the common prefix of the list dirs in the config
                        #~ and remote path, if there is any, the torrent should
                        #~ go to series, if not - no
                        _commonprefix = os.path.commonprefix([*list_dirs, rpath_cp ])

                        if _commonprefix:

                            logger.info(
                                "Torrent {} can go to {}".format(
                                    _, rpath_cp
                                )
                            )

                        else:
                            logger.warning(
                                "Torrent {} not part of series, skip next actions".format(
                                    _
                                )
                            )
                            continue

                        lpath_cp = os.path.expanduser(
                            os.path.join(
                                "~",
                                config.get("DEFAULT", "local_folder"),
                                t["name"]
                            )
                        )

                        logger.info(
                            "Torrent {} will copy local file at {} to {}"
                            "using scp right now".format(
                                _, lpath_cp, rpath_cp
                            )
                        )

                        p = subprocess.Popen( [
                            "scp",
                            "-q",
                            lpath_cp,
                            "{}:{}".format(
                                config.get("DEFAULT", "remote_host"),
                                rpath_cp
                            )
                        ] )

                        sts = os.waitpid(p.pid, 0)
        else:
            logger.info(
                "Torrent {} with name {} is not completed".format(
                    _, t["name"]
                )
            )
