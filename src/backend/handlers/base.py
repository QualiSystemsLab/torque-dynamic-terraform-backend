import json
import os
from abc import ABC, abstractmethod
from copy import deepcopy

from models.terraform_data_source import TerraformRemoteStateDataSource
from utils.logger import LoggerHelper


# all backend handlers need to be stateless
class BaseBackendHandler(ABC):

    @property
    @abstractmethod
    def backend_type(self) -> str:
        return NotImplemented

    @property
    @abstractmethod
    def tf_state_prop_name(self) -> str:
        return NotImplemented

    def can_handle(self, backend_config: dict = None, backend_type: str = "") -> bool:
        if backend_config and self.backend_type in backend_config:
            LoggerHelper.write_info(f"{self.backend_type} backend detected")
            return True
        if backend_type and self.backend_type == backend_type:
            return True
        return False

    def _get_backend_config_template(self) -> str:
        return """terraform {{
\tbackend \"{BACKEND_TYPE}\" {{
{BACKEND_PROPS}
\t}}
}}
"""

    def _get_remote_state_data_source_template(self) -> str:
        return """data "terraform_remote_state" "{DATA_SOURCE_NAME}" {{
\tbackend = "{BACKEND_TYPE}"
\tconfig = {{
\t\t{PROP_KEY} = \"{PROP_VALUE}\"
\t}}
}}"""

    def _get_backend_config_with_props_template(self, props: dict):
        prop_template = '\t\t{PROP_KEY} = \"{PROP_VALUE}\"'
        formatted_props_list = []
        for key, val in props.items():
            formatted_props_list.append(
                prop_template.format(PROP_KEY=key, PROP_VALUE=val))
        formatted_props_str = "\n".join(formatted_props_list)

        return self._get_backend_config_template().format(BACKEND_TYPE=self.backend_type,
                                                          BACKEND_PROPS=formatted_props_str)

    def add_uid_to_tfstate_for_backend_config(self, backend_config: dict, sandbox_id: str) -> dict:
        backend_config_copy = deepcopy(backend_config)
        backend = backend_config_copy[self.backend_type]
        if self.tf_state_prop_name in backend:
            unique_key = self._torqify_tf_state_prop(backend[self.tf_state_prop_name], sandbox_id)
            LoggerHelper.write_info(f"Created new unique value for tfstate key in {self.backend_type} "
                                    f"backend config: {unique_key}")
            backend[self.tf_state_prop_name] = unique_key
        else:
            raise ValueError(f"'{self.tf_state_prop_name}' property wasn't found in {self.backend_type} "
                             f"backend configurations")

        return backend_config_copy

    def _torqify_tf_state_prop(self, tf_state_prop: str, sandbox_id: str) -> str:
        filename, file_extension = os.path.splitext(tf_state_prop)
        unique_key = f"{filename}-{sandbox_id}"
        if file_extension:
            unique_key = f"{unique_key}{file_extension}"
        return unique_key

    def format_backend_to_hcl(self, backend_config: dict) -> str:
        if self.backend_type not in backend_config:
            raise ValueError(f"Expected backend type '{self.backend_type}' but received different backend "
                             f"type '{json.dumps(backend_config)}'")
        backend_props = backend_config[self.backend_type]
        if not isinstance(backend_props, dict):
            raise ValueError(
                f"Expected map in {self.backend_type} backend config but got type {type(backend_props)}")

        backend_hcl_str = self._get_backend_config_with_props_template(backend_props)

        return backend_hcl_str

    def format_remote_state_data_source_with_uid(self, tf_remote_state: TerraformRemoteStateDataSource,
                                                 sandbox_id: str) -> str:
        if self.tf_state_prop_name not in tf_remote_state.config:
            raise ValueError(f"Prop '{self.tf_state_prop_name}' doesn't exist in config section in "
                             f"remote state '{tf_remote_state.data_source_name}'")
        torqified_key = self._torqify_tf_state_prop(tf_remote_state.config[self.tf_state_prop_name], sandbox_id)
        LoggerHelper.write_info(
            f"Created new unique value {self.tf_state_prop_name} = {torqified_key} for remote state "
            f"data source '{tf_remote_state.data_source_name}' of type '{self.backend_type}' ")
        return self._get_remote_state_data_source_template().format(DATA_SOURCE_NAME=tf_remote_state.data_source_name,
                                                                    BACKEND_TYPE=tf_remote_state.backend_type,
                                                                    PROP_KEY=self.tf_state_prop_name,
                                                                    PROP_VALUE=torqified_key)
