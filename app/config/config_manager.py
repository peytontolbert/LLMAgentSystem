import os
from typing import Any, Dict
import yaml
from dotenv import load_dotenv

class ConfigManager:
    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self.load_config()
        load_dotenv()  # Load environment variables from .env file

    def load_config(self):
        with open(self.config_file, 'r') as file:
            self.config = yaml.safe_load(file)

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        self.config[key] = value

    def save_config(self):
        with open(self.config_file, 'w') as file:
            yaml.dump(self.config, file)

    def get_env(self, key: str, default: Any = None) -> Any:
        return os.getenv(key, default)

class EnvironmentManager:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.current_environment = self.config_manager.get_env("ENVIRONMENT", "development")

    def get_environment(self) -> str:
        return self.current_environment

    def set_environment(self, environment: str):
        self.current_environment = environment
        os.environ["ENVIRONMENT"] = environment

    def get_config_for_environment(self) -> Dict[str, Any]:
        env_config = self.config_manager.get(self.current_environment, {})
        return {**self.config_manager.config.get("default", {}), **env_config}

    def get_database_url(self) -> str:
        env_config = self.get_config_for_environment()
        return env_config.get("database_url", "")

    def get_api_key(self) -> str:
        env_config = self.get_config_for_environment()
        return env_config.get("api_key", "")