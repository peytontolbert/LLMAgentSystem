import logging
from typing import Dict, Any
from collections import OrderedDict
import hashlib

logger = logging.getLogger(__name__)

class NLPCache:
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: OrderedDict[str, Any] = OrderedDict()
        logger.info(f"Initialized NLPCache with max size: {max_size}")

    def _hash_input(self, input_text: str) -> str:
        return hashlib.md5(input_text.encode()).hexdigest()

    def get(self, input_text: str) -> Any:
        try:
            key = self._hash_input(input_text)
            if key in self.cache:
                self.cache.move_to_end(key)
                logger.debug(f"Cache hit for key: {key[:8]}...")
                return self.cache[key]
            logger.debug(f"Cache miss for key: {key[:8]}...")
            return None
        except Exception as e:
            logger.error(f"Error in NLPCache.get: {str(e)}")
            return None

    def put(self, input_text: str, value: Any) -> None:
        try:
            key = self._hash_input(input_text)
            if key in self.cache:
                self.cache.move_to_end(key)
            elif len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)
            self.cache[key] = value
            logger.debug(f"Added/updated key in cache: {key[:8]}...")
        except Exception as e:
            logger.error(f"Error in NLPCache.put: {str(e)}")

    def clear(self) -> None:
        try:
            self.cache.clear()
            logger.info("NLPCache cleared")
        except Exception as e:
            logger.error(f"Error in NLPCache.clear: {str(e)}")

    def __len__(self) -> int:
        return len(self.cache)

    def __contains__(self, input_text: str) -> bool:
        return self._hash_input(input_text) in self.cache