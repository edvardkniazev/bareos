import httpx
import configparser
import os
import logging
from datetime import datetime


config_file="etc/config.ini"


def get_config_data(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)

    return {
        "hostname": config.get("Common", "hostname"),
        "port":     config.get("Common", "port"),
        "storage":  config.get("Common", "storage"),
        "logfile":  config.get("Common", "logfile")
        }


def get_auth_data(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)

    username = config.get("Authentication", "username")
    password = config.get("Authentication", "password")
    
    return {
        "username": username,
        "password": password
        }
    

def get_url(config_data):
    hostname = config_data["hostname"]
    port = config_data["port"]
    return f"http://{hostname}:{port}"


def login(url, auth_data):
    auth_response = httpx.post(f"{url}/token", data=auth_data)
    access_token = auth_response.json()["access_token"]
    return {
        "Authorization": f"Bearer {access_token}"
        }


def list_volumes_to_remove(url, headers):
    response = httpx.get(url=url, headers=headers)
    volumes = response.json()["volumes"]
    volumes_to_remove = []

    for pool in volumes.values():
        v_to_d = [vol["volumename"] for vol in pool if vol["volstatus"] == 'Purged']
        volumes_to_remove.extend(v_to_d)
    return volumes_to_remove


def make_requests_to_remove(url, volumes):
    return [f"{url}/{v}" for v in volumes]


def add_path_to_files(path, files):
    return [os.path.join(path, file) for file in files]


def remove_volumes(requests, headers, files):
    for request, file in zip(requests, files):
        response = httpx.delete(url=request, headers=headers)
        if response.status_code == 204:
            logging.info(f"Removed successfully {request}")
            try:
                os.remove(file)
                logging.info(f"Removed successfully {file}")
            except OSError as e:
                logging.error(f"{e.strerror} {file}")
        else:
            logging.error(f"{response.status_code} {request}")


if __name__ == "__main__":

    start = datetime.now()

    config_data = get_config_data(config_file)
    auth_data = get_auth_data(config_file)

    logging.basicConfig(filename=config_data["logfile"], level=logging.INFO)
    logging.info(f'Start time: {start.strftime("%Y-%m-%d %H:%M:%S")}')

    url = get_url(config_data)
    headers = login(url, auth_data)

    volumes = list_volumes_to_remove(f"{url}/control/volumes", headers)
    requests = make_requests_to_remove(f"{url}/control/volumes", volumes)
    files = add_path_to_files(config_data["storage"], volumes)

    remove_volumes(requests, headers, files)

    end = datetime.now()
    elapsed = end - start
    logging.info(f'End time: {end.strftime("%Y-%m-%d %H:%M:%S")}')
    logging.info(f'Elapsed time: {elapsed}')
