import httpx
import configparser
import os
import logging
from datetime import datetime
from pprint import pprint   # only for debug purpose


config_file="config.ini"


def get_config_data(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)

    config_data = {
        "hostname": config.get("Common", "hostname"),
        "port":     config.get("Common", "port"),
        "storage":  config.get("Common", "storage"),
        "logfile":  config.get("Common", "logfile")
        }
    return config_data


def get_auth_data(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)

    username = config.get("Authentication", "username")
    password = config.get("Authentication", "password")
    
    auth_data = {
        "username": username,
        "password": password
        }
    return auth_data
    

def get_url(config_data):
    hostname = config_data["hostname"]
    port = config_data["port"]
    url = f"http://{hostname}:{port}"
    return url 


def login(url, auth_data):
    auth_response = httpx.post(f"{url}/token", data=auth_data)
    access_token = auth_response.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {access_token}"
        }
    return headers


def list_volumes_to_remove(url, headers):
    response = httpx.get(url=url, headers=headers)
    volumes = response.json()["volumes"]
    volumes_to_remove = []

    for pool in volumes.values():
        v_to_d = [vol["volumename"] for vol in pool if vol["volstatus"] == 'Purged']
        volumes_to_remove.extend(v_to_d)
    return volumes_to_remove


def make_requests_to_remove(url, volumes):
    requests = [f"{url}/{v}" for v in volumes]
    return requests


def add_path_to_files(path, files):
    files = [os.path.join(path, file) for file in files]
    return files


def remove_volumes(requests, headers, files):
    for request, file in zip(requests, files):
        #httpx.delete(url=request, headers=headers)
        logging.debug(request)
        #os.remove(file)
        logging.debug(file)


if __name__ == "__main__":

    config_data = get_config_data(config_file)
    auth_data = get_auth_data(config_file)

    logging.basicConfig(filename=config_data["logfile"], level=logging.DEBUG)

    url = get_url(config_data)
    headers = login(url, auth_data)

    volumes = list_volumes_to_remove(url=f"{url}/control/volumes", headers=headers)
    requests = make_requests_to_remove(url=f"{url}/control/volumes", volumes=volumes)
    files = add_path_to_files(config_data["storage"], volumes)

    remove_volumes(requests, headers, files)
