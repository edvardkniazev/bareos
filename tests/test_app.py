from bin.app import *


config_file = "etc/config.ini"


def test_get_config_data():
    config_data = get_config_data(config_file)
    assert "hostname" in config_data.keys()
    assert "port" in config_data.keys()
    assert config_data["hostname"] is not None
    assert config_data["port"] is not None


def test_get_auth_data():
    auth_data = get_auth_data(config_file)
    assert "username" in auth_data.keys()
    assert "password" in auth_data.keys()
    assert auth_data["username"] is not None
    assert auth_data["password"] is not None


def test_get_url():
    config_data = {
        "hostname": "www.example.com",
        "port": 80
        }
    assert get_url(config_data) == "http://www.example.com:80"
