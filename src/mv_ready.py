#!/usr/bin/env python

import transmissionrpc
import paramiko
import argparse
import configparser
import os
import subprocess

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
    required=True,
    metavar="",
    dest="series_list",
    help="config file to know which folders we keep an eye on"
)

if __name__ == "__main__":

    args = parser.parse_args()

    config = configparser.ConfigParser()

    config.read(args.series_list[0])

    user_ssh = ""

    if config.getboolean("DEFAULT", "remote_ssh_user"):

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

    list_dirs = []

    for section in config.sections():

        list_dirs.append(config.get(section, "remote_path"))

    tc = transmissionrpc.Client("localhost", port=9091, timeout=1)

    for _ in tc.get_files():

        t = tc.get_files()[_]

        if len(t.keys()) > 1:
            continue
        else:
            t = t[0]

        if t["completed"] == t["size"]:
            print("\n Completed is... {} \n".format(t["name"]))

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

                if ssh_stderr:
                    print("\n find ended with errors:")

                    for _ in ssh_stderr:
                        print("\t {}".format(_))

                    exit()

                if stdout.readline():
                    if config.getboolean("DEFAULT", "local_delete"):
                        print("\n\t already downloaded, DELETE is YES... \n")

                        tc.remove_torrent(_, delete_data=True)
                    else:
                        print("\n\t already downloaded, DELETE is NO... \n")
                else:

                    stdin, stdout, stderr = ssh.exec_command(
                        "find {} -type f -name {}* | head -n1".format(
                            " ".join(list_dirs),
                            t["name"].split("E")[0].strip().replace(" ", "\ ")
                        )
                    )

                    ssh_stderr = stderr.readlines()

                    if ssh_stderr:
                        print("\n dirname ended with error, \n\t {} \n".format(ssh_stderr))
                        exit()
                    else:
                        rpath_cp = os.path.dirname(stdout.readline())

                        if os.path.commonprefix([*list_dirs, rpath_cp ]):
                            print("\n\t will copy it to... {}".format(rpath_cp))
                        else:
                            print("\n\t not part of Series... {}".format(rpath_cp))
                            continue

                        lpath_cp = os.path.expanduser(
                            os.path.join(
                                "~",
                                config.get("DEFAULT", "local_folder"),
                                t["name"]
                            )
                        )

                        p = subprocess.Popen( [
                            "scp",
                            lpath_cp,
                            "{}:{}".format(
                                config.get("DEFAULT", "remote_host"),
                                rpath_cp
                            )
                        ] )

                        sts = os.waitpid(p.pid, 0)
        else:
            print("\n NOT completed is... {} \n".format(t["name"]))

