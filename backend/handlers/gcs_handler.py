import os
from copy import deepcopy

from backend.handlers.base import BaseBackendHandler
from utils.logger import LoggerHelper


class GCSBackendHandler(BaseBackendHandler):

    @property
    def backend_type(self):
        return "gcs"

    @property
    def tf_state_prop_name(self):
        return "prefix"
