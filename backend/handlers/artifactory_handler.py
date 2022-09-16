import os
from copy import deepcopy

from backend.handlers.base import BaseBackendHandler
from utils.logger import LoggerHelper


class ArtifactoryBackendHandler(BaseBackendHandler):

    @property
    def backend_type(self):
        return "artifactory"

    @property
    def tf_state_prop_name(self):
        return "subpath"
