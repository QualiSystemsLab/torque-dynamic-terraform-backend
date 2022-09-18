from backend.handlers.base import BaseBackendHandler


class S3BackendHandler(BaseBackendHandler):

    @property
    def backend_type(self):
        return "s3"

    @property
    def tf_state_prop_name(self):
        return "key"
