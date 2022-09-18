from backend.handlers.base import BaseBackendHandler


class GCSBackendHandler(BaseBackendHandler):

    @property
    def backend_type(self):
        return "gcs"

    @property
    def tf_state_prop_name(self):
        return "prefix"
