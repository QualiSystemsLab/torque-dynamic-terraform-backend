import json

import hcl2
from typing import List, Union

from models.terraform_data_source import TerraformRemoteStateDataSource
from utils.logger import LoggerHelper


class Hcl2Parser:
    @staticmethod
    def get_tf_file_as_dict(tf_file_path: str) -> dict:
        with (open(tf_file_path, 'r')) as client_tf_file:
            return hcl2.load(client_tf_file)

    @staticmethod
    def get_tf_backend_configuration(tf_file_path: str) -> Union[dict, None]:
        """
        :return: returns dict representing backend configuration in provided .tf file. Or none is returned if backend
        isn't found
        """
        tf_as_dict = Hcl2Parser.get_tf_file_as_dict(tf_file_path)
        for tf_configurations in tf_as_dict.get("terraform", []):
            backend_config = tf_configurations.get("backend", None)
            if backend_config:
                return next(iter(backend_config))

        return None

    @staticmethod
    def get_tf_remote_state_data_source_safely(datasource_object: dict) -> Union[TerraformRemoteStateDataSource, None]:
        if "terraform_remote_state" not in datasource_object:
            return None

        terraform_remote_state_dict = datasource_object["terraform_remote_state"]
        keys = list(datasource_object["terraform_remote_state"].keys())
        if len(keys) != 1:
            LoggerHelper.write_info(f"Skipping data source. Expected 1 data source name but got {len(keys)}. "
                                    f"Data source: f{json.dumps(terraform_remote_state_dict)} ")
            return None
        data_source_name = keys[0]
        props = terraform_remote_state_dict[data_source_name]
        if "backend" not in props or "config" not in props:
            LoggerHelper.write_info(f"Skipping data source. Expected 'backend' and 'config' props in data "
                                    f"source but one or both were not found. "
                                    f"Data source: {json.dumps(terraform_remote_state_dict)}")
            return None

        return TerraformRemoteStateDataSource(data_source_name, props)

    @staticmethod
    def get_tf_all_remote_state_data_sources(tf_file_path: str) -> List[TerraformRemoteStateDataSource]:
        remote_state_data_sources: List[TerraformRemoteStateDataSource] = []
        tf_as_dict = Hcl2Parser.get_tf_file_as_dict(tf_file_path)
        for datasource_object in tf_as_dict.get("data", []):
            tf_remote_state_data_source = Hcl2Parser.get_tf_remote_state_data_source_safely(datasource_object)
            if tf_remote_state_data_source:
                remote_state_data_sources.append(tf_remote_state_data_source)

        return remote_state_data_sources
