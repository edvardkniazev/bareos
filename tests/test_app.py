from src.app import *


def test_get_config_data():
    config_data = get_config_data()
    assert "hostname" in config_data.keys()
    assert "port" in config_data.keys()
    assert config_data["hostname"] is not None
    assert config_data["port"] is not None


def test_get_auth_data():
    auth_data = get_auth_data()
    assert "username" in auth_data.keys()
    assert "password" in auth_data.keys()
    assert auth_data["username"] is not None
    assert auth_data["password"] is not None
