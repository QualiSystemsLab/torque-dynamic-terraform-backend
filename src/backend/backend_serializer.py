import json
import os
from typing import List

from backend.backend_handler_provider import BackendHandlerProvider
from models.terraform_data_source import TerraformRemoteStateDataSource
from utils.logger import LoggerHelper


class BackendSerializer:
    def __init__(self, backend_handler_provider: BackendHandlerProvider, tf_dir: str, sandbox_id: str):
        self._backend_handler_provider = backend_handler_provider
        self._tf_dir = tf_dir
        self._sandbox_id = sandbox_id

    def _get_backend_config_override_file_path(self):
        return os.path.join(self._tf_dir, f"torque_backend_{self._sandbox_id}_override.tf")

    def _get_remote_state_data_source_override_file_path(self):
        return os.path.join(self._tf_dir, f"torque_remotestate_datasource_{self._sandbox_id}_override.tf")

    def create_backend_config_override_file(self, backend_config: dict):
        backend_handler = self._backend_handler_provider.get_handler(backend_config)
        if not backend_handler:
            raise ValueError(f"Handler not found for backend: {json.dumps(backend_config)}")

        updated_backend_config = backend_handler.add_uid_to_tfstate_for_backend_config(backend_config, self._sandbox_id)
        backend_config_hcl_string = backend_handler.format_backend_to_hcl(updated_backend_config)

        override_file_path = self._get_backend_config_override_file_path()
        with (open(override_file_path, 'w')) as override_tf_file:
            override_tf_file.write(backend_config_hcl_string)

        LoggerHelper.write_info(f"Override file was created for backend located in file {override_file_path}")

    def create_backend_remote_state_datasource_override_file(self,
                                                             backend_remote_state_list:
                                                             List[TerraformRemoteStateDataSource]):
        override_file_path = self._get_remote_state_data_source_override_file_path()
        with (open(override_file_path, 'w')) as override_tf_file:
            for tf_remote_state in backend_remote_state_list:
                backend_handler = self._backend_handler_provider.get_handler_by_type(tf_remote_state.backend_type)
                if not backend_handler:
                    raise ValueError(f"Handler not found for backend: {tf_remote_state.backend_type}")
                remote_state_data_source_hcl_string =\
                    backend_handler.format_remote_state_data_source_with_uid(tf_remote_state, self._sandbox_id)
                override_tf_file.write(remote_state_data_source_hcl_string)
