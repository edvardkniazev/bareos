import httpx
import configparser
import os
import logging
from datetime import datetime


config_file = "etc/config.ini"


class Config:
    def __init__(self, config_file: str):
        config = configparser.ConfigParser()
        config.read(config_file)

        self.hostname = config.get("Common", "hostname")
        self.port = config.get("Common", "port")
        self.storage = config.get("Common", "storage")
        self.logfile = config.get("Common", "logfile")

        self.username = config.get("Authentication", "username")
        self.password = config.get("Authentication", "password")


class Url:
    def __init__(self, cfg: Config):
        self.base = f"http://{cfg.hostname}:{cfg.port}"
        self.token = f"{self.base}/token"
        self.control_volumes = f"{self.base}/control/volumes"
        self.control_jobs = f"{self.base}/control/jobs"
        self.path = cfg.storage


class Authorization():
    def __init__(self, cfg: Config):
        self.auth_data = {
                "username": cfg.username,
                "password": cfg.password
                }

    def login(self, url: str):
        auth_response = httpx.post(f"{url}", data=self.auth_data)
        access_token = auth_response.json()["access_token"]
        self.headers = {
                "Authorization": f"Bearer {access_token}"
                }
        return self.headers


class Volumes():
    def __init__(self, url: Url, headers: dict):
        self.purged_volumes = []
        self.used_volumes = []
        self.obsolete_files = []
        self.url = url
        self.headers = headers

    def request_purged_volumes(self):
        response = httpx.get(
                url=self.url.control_volumes,
                headers=self.headers
                )
        all_volumes = response.json()["volumes"]

        for pool in all_volumes.values():
            pd = [
                    vol["volumename"]
                    for vol in pool
                    if vol["volstatus"] == 'Purged'
                    ]
            self.purged_volumes.extend(pd)
        self.obsolete_files = self.purged_volumes.copy()

    def request_used_volumes(self):
        response = httpx.get(
                url=self.url.control_jobs,
                headers=self.headers)
        all_jobs = response.json()["jobs"]
        self.used_volumes = [
                f"{job['poolname']}-{job['jobid']}"
                for job in all_jobs
                ]

    def set_requests(self):
        return [
                f"{self.url.control_volumes}/{v}"
                for v in self.purged_volumes
                ]

    def complete_filenames(self):
        return [
                os.path.join(self.url.path, file)
                for file in self.obsolete_files
                ]

    def remove_volumes(self):
        for request in self.set_requests():
            response = httpx.delete(url=request, headers=headers)
            if response.status_code == 204:
                logging.info(f"Removed successfully {request}")
            else:
                logging.error(f"{response.status_code} {request}")

    def remove_files(self):
        for file in self.complete_filenames():
            try:
                os.remove(file)
                logging.info(f"Removed successfully {file}")
            except OSError as e:
                logging.error(f"{e.strerror} {file}")

    def fs_walk(self):
        files = [
                files
                for root, _, files in os.walk(self.url.path)
                if root == self.url.path
                ]
        return files[0]

    def add_extra(self):
        extra_files = list(set(self.fs_walk()) - set(self.used_volumes))
        self.obsolete_files.extend(extra_files)


if __name__ == "__main__":

    start = datetime.now()

    cfg = Config(config_file)

    logging.basicConfig(filename=cfg.logfile, level=logging.INFO)
    logging.info(f'Start time: {start.strftime("%Y-%m-%d %H:%M:%S")}')

    url = Url(cfg)
    auth = Authorization(cfg)
    headers = auth.login(url.token)
    volumes = Volumes(url, headers)

    volumes.request_purged_volumes()
    volumes.request_used_volumes()
    volumes.add_extra()
    volumes.remove_volumes()
    volumes.remove_files()

    end = datetime.now()
    elapsed = end - start
    logging.info(f'End time: {end.strftime("%Y-%m-%d %H:%M:%S")}')
    logging.info(f'Elapsed time: {elapsed}')
