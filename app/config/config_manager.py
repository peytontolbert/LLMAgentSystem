import os
from typing import Any, Dict
import yaml
from dotenv import load_dotenv

class ConfigManager:
    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        load_dotenv()  # Load environment variables from .env file
        self.load_config()
        self.environment = os.getenv("ENVIRONMENT", "development")

    def load_config(self):
        with open(self.config_file, 'r') as file:
            self.config = yaml.safe_load(file)

    def get(self, key: str, default: Any = None) -> Any:
        # First, check if the key exists as an environment variable
        env_value = os.getenv(key.upper())
        if env_value is not None:
            return env_value

        # If not, look in the YAML config
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k, {})
        return value or default

    def set(self, key: str, value: Any):
        self.config[key] = value

    def save_config(self):
        with open(self.config_file, 'w') as file:
            yaml.dump(self.config, file)

    def get_env(self, key: str, default: Any = None) -> Any:
        return os.getenv(key, default)

    def get_environment(self) -> str:
        return self.environment

class EnvironmentManager:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager

    def get_environment(self) -> str:
        return self.config_manager.get_environment()

    def set_environment(self, environment: str):
        os.environ["ENVIRONMENT"] = environment
        self.config_manager.environment = environment

    def get_config_for_environment(self) -> Dict[str, Any]:
        env_config = self.config_manager.get(self.config_manager.get_environment(), {})
        return {**self.config_manager.get("default", {}), **env_config}

    def get_database_url(self) -> str:
        env_config = self.get_config_for_environment()
        return env_config.get("database_url", "")

    def get_api_key(self) -> str:
        env_config = self.get_config_for_environment()
        return env_config.get("api_key", "")