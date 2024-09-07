from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class DIContainer:
    def __init__(self):
        self._services: Dict[str, Any] = {}

    def register(self, name: str, service: Any) -> None:
        self._services[name] = service
        logger.info(f"Registered service: {name}")

    def get(self, name: str) -> Any:
        service = self._services.get(name)
        if service is None:
            logger.error(f"Service not found: {name}")
            raise KeyError(f"Service not found: {name}")
        return service

container = DIContainer()