import pytest
from app.config.config_manager import ConfigManager, EnvironmentManager
import os

@pytest.fixture
def config_manager():
    return ConfigManager("tests/test_config.yaml")

@pytest.fixture
def environment_manager(config_manager):
    return EnvironmentManager(config_manager)

def test_config_manager_load(mocker):
    mock_config = {'LOGGING': {'LEVEL': 'DEBUG'}}
    mock_open = mocker.mock_open(read_data="LOGGING:\n  LEVEL: DEBUG")
    mocker.patch('builtins.open', mock_open)
    mocker.patch('yaml.safe_load', return_value=mock_config)
    config_manager = ConfigManager('config.yaml')
    assert config_manager.get('LOGGING', 'LEVEL') == 'DEBUG'

def test_config_manager_get_env(config_manager):
    os.environ["TEST_ENV_VAR"] = "test_value"
    assert config_manager.get_env("TEST_ENV_VAR") == "test_value"

def test_environment_manager_get_environment(environment_manager):
    assert environment_manager.get_environment() in ["development", "production", "testing"]

def test_environment_manager_set_environment(environment_manager):
    environment_manager.set_environment("testing")
    assert environment_manager.get_environment() == "testing"
    assert os.getenv("ENVIRONMENT") == "testing"

def test_environment_manager_get_config_for_environment(environment_manager):
    environment_manager.set_environment("development")
    config = environment_manager.get_config_for_environment()
    assert config["database_url"] == "sqlite:///./dev.db"
    assert config["api_key"] == "dev_api_key"