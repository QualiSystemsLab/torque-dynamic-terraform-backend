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

        return None
