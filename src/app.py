import httpx
import configparser
from pprint import pprint   # only for debug purpose


config_file="config.ini"


def get_config_data(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)

    hostname = config.get("Common", "hostname")
    port = config.get("Common", "port")
    
    config_data = {
        "hostname": hostname,
        "port": port
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


if __name__ == "__main__":
    config_data = get_config_data(config_file)
    auth_data = get_auth_data(config_file)
    url = get_url(config_data)
    headers = login(url, auth_data)

    total_volumes = httpx.get(f"{url}/control/volumes", headers=headers)
    volumes = total_volumes.json()["volumes"]
    

    for pool in volumes.values():
        for vol in pool:
            #if vol["recycle"]:
            if vol["volumename"] == "Wal-31421":
                volume_id = vol["mediaid"]
                volume_name = vol["volumename"]
    
                read_volume = httpx.delete(f"{url}/control/volumes/{volume_name}", headers=headers)
                pprint(str(read_volume.content))
