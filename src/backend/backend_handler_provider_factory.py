from backend.backend_handler_provider import BackendHandlerProvider
from backend.handlers.azurerm_handler import AzureRMBackendHandler
from backend.handlers.gcs_handler import GCSBackendHandler
from backend.handlers.s3_handler import S3BackendHandler


class BackendHandlerProviderFactory:
    @staticmethod
    def create():
        provider = BackendHandlerProvider()

        # add new backend handlers here: provider.register(MyBackendHandler())
        provider.register(S3BackendHandler())
        provider.register(GCSBackendHandler())
        provider.register(AzureRMBackendHandler())

        return provider
