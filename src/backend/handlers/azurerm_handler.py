from backend.handlers.base import BaseBackendHandler


class AzureRMBackendHandler(BaseBackendHandler):

    @property
    def backend_type(self):
        return "azurerm"

    @property
    def tf_state_prop_name(self):
        return "key"
