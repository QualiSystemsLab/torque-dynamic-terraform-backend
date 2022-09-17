import os

from backend.handlers.base import BaseBackendHandler
from models.file_info import FileInfo
from utils.logger import LoggerHelper


class BackendSerializer:
    def __init__(self, backend_config: dict, backend_handler: BaseBackendHandler, tf_file_info: FileInfo):
        self._backend_config = backend_config
        self._backend_handler = backend_handler
        self._tf_file_info = tf_file_info

    def _get_override_file_path(self):
        (file_without_ext, ext) = os.path.splitext(self._tf_file_info.file_name)
        override_file_path = os.path.join(self._tf_file_info.file_dir, f"{file_without_ext}_override.tf")
        return override_file_path

    def create_backend_override_file(self):
        backend_config_hcl_string = self._backend_handler.format_backend_to_hcl(self._backend_config)

        override_file_path = self._get_override_file_path()
        with(open(override_file_path, 'w')) as override_tf_file:
            override_tf_file.write(backend_config_hcl_string)

        LoggerHelper.write_info(f"Override file was created for backend located in file {self._tf_file_info.file_path}")