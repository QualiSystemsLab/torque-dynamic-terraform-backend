import os
from abc import ABC, abstractmethod
from copy import deepcopy

from utils.logger import LoggerHelper


# all backend handlers need to be stateless
class BaseBackendHandler(ABC):

    def __init__(self):
        pass

    @property
    @abstractmethod
    def backend_type(self) -> str:
        return NotImplemented

    @property
    @abstractmethod
    def tf_state_prop_name(self) -> str:
        return NotImplemented

    def can_handle(self, backend_config: dict) -> bool:
        if self.backend_type in backend_config:
            LoggerHelper.write_info(f"{self.backend_type} backend detected")
            return True
        else:
            return False

    def _get_base_template(self) -> str:
        return """terraform {{
    backend \"{BACKEND_TYPE}\" {{
{BACKEND_PROPS}
    }}
}}
"""

    def _get_backend_with_props_template(self, props: dict):
        prop_template = '\t\t{PROP_KEY} = \"{PROP_VALUE}\"'
        formatted_props_list = []
        for key, val in props.items():
            formatted_props_list.append(
                prop_template.format(PROP_KEY=key, PROP_VALUE=val))
        formatted_props_str = "\n".join(formatted_props_list)

        return self._get_base_template().format(BACKEND_TYPE=self.backend_type, BACKEND_PROPS=formatted_props_str)

    def add_uid_to_tfstate(self, backend_config: dict, sandbox_id: str) -> dict:
        backend_config_copy = deepcopy(backend_config)
        backend = backend_config_copy[self.backend_type]
        if self.tf_state_prop_name in backend:
            filename, file_extension = os.path.splitext(backend[self.tf_state_prop_name])
            unique_key = f"{filename}-{sandbox_id}"
            if file_extension:
                unique_key = f"{unique_key}.{file_extension}"
            LoggerHelper.write_info(f"Created new unique value for tfstate key in {self.backend_type} "
                                    f"backend config: {unique_key}")
            backend[self.tf_state_prop_name] = unique_key
        else:
            raise ValueError(f"'{self.tf_state_prop_name}' property wasn't found in {self.backend_type} "
                             f"backend configurations")

        return backend_config_copy

    def format_backend_to_hcl(self, backend_config: dict) -> str:
        backend_props = backend_config[self.backend_type]
        if not isinstance(backend_props, dict):
            raise ValueError(
                f"Expected map in {self.backend_type} backend config but got type {type(backend_props)}")

        backend_hcl_str = self._get_backend_with_props_template(backend_props)

        return backend_hcl_str


