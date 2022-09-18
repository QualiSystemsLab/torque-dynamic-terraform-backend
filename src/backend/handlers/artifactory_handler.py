from backend.handlers.base import BaseBackendHandler


class ArtifactoryBackendHandler(BaseBackendHandler):

    @property
    def backend_type(self):
        return "artifactory"

    @property
    def tf_state_prop_name(self):
        return "subpath"
