# Automate the process of downloading new series and moving them to my storage for viewing pleasure

The scirpts look up for "retrive_episodes.config" in the src directory.

In it you can try to set remote host, username, password and ssh user - which are used for moving the files to the remote host/storage. If password left empty it presumes that there is automatic ssh login procedure (the storage has the id pub key of the host)

It will look up at local_folder, and if loca_delete is set to yes, will delete every old downloaded episode.

It will attempt to log at tracker_url with tracker_user and tracker_passwd. Search for name + season and increment by 1 the latest uploaded (sort by time) episode at remote_path. If new torrent is present, add it to transmission, check regular intervals if it has finished, and sent it to remote_path.

The script doing the first part is torrent_download, the script moving the episode is retrive_episodes