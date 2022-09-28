import json
from typing import List

from backend.handlers.base import BaseBackendHandler


class BackendHandlerProvider:
    def __init__(self):
        self._handlers = []  # type: List[BaseBackendHandler]

    def register(self, handler: BaseBackendHandler) -> None:
        self._handlers.append(handler)

    def get_handler(self, backend_config: dict) -> BaseBackendHandler:
        for handler in self._handlers:
            if handler.can_handle(backend_config):
                return handler
        raise ValueError(f"Handler not found for backend: {json.dumps(backend_config)}")

    def get_handler_by_type(self, backend_type: str) -> BaseBackendHandler:
        for handler in self._handlers:
            if handler.can_handle(backend_type=backend_type):
                return handler
        raise ValueError(f"Handler not found for backend: {backend_type}")
