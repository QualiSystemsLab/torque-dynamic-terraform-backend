#######################################
# Notes:
# - supports Terraform 0.12.0 and above
# - supported backend types: S3 Bucket(s3), Azure Storage (azurerm), Goggle Cloud Storage (gcs), Artifactory
# - to add support for additional backends implement abstract class BaseBackendHandler and register new handler in
#   BackendHandlerProviderFactory
#

import json
import os
import sys

from typing import List

from backend.backend_handler_provider_factory import BackendHandlerProviderFactory
from backend.backend_serializer import BackendSerializer
import consts
from models.file_info import FileInfo
from models.terraform_data_source import TerraformRemoteStateDataSource
from parsers.hcl_parser import Hcl2Parser
from utils.file_helpers import FilesHelper
from utils.logger import LoggerHelper


def validate_tf_main_dir_exists() -> None:
    if not os.path.exists(consts.TF_MAIN_DIR):
        raise ValueError(f"Path {consts.TF_MAIN_DIR} does not exist")


def torqify_terraform_backend_data_source(sandbox_id: str, all_tf_files: List[FileInfo],
                                          exclude_data_source_names: List[str]):
    LoggerHelper.write_info(f"Searching for remote backend data sources")
    remote_state_data_sources = []
    for tf_file in all_tf_files:
        data_sources = Hcl2Parser.get_tf_all_remote_state_data_sources(tf_file.file_path)
        data_sources_to_exclude = list(filter(lambda x: x.data_source_name in exclude_data_source_names, data_sources))
        if data_sources_to_exclude:
            data_source_names_to_exclude = list(map(lambda x: x.data_source_name, data_sources_to_exclude))
            LoggerHelper.write_info(f"Excluding remote backend data sources {','.join(data_source_names_to_exclude)} "
                                    f"in TF file {tf_file.file_path}")
        data_source_to_torqify = set(data_sources) - set(data_sources_to_exclude)
        remote_state_data_sources.extend(list(data_source_to_torqify))

    if not remote_state_data_sources:
        LoggerHelper.write_info("No remote backend data sources found")

    backend_handler_provider = BackendHandlerProviderFactory().create()
    backend_serializer = BackendSerializer(backend_handler_provider, consts.TF_MAIN_DIR, sandbox_id)
    backend_serializer.create_backend_remote_state_datasource_override_file(remote_state_data_sources)

    LoggerHelper.write_info("Successfully finish creating override file for backend remote state data sources\n")


def torqify_terraform_remote_backend(sandbox_id: str, all_tf_files: List[FileInfo]):
    LoggerHelper.write_info(f"Searching for backend configurations")
    backend_config = {}
    # backend configuration can appear only one time so we are searching for the first occurrence
    for tf_file in all_tf_files:
        backend_config = Hcl2Parser.get_tf_backend_configuration(tf_file.file_path)
        if backend_config:
            LoggerHelper.write_info(f"Found backend configurations in file '{tf_file.file_path}': "
                                    f"{json.dumps(backend_config)}")
            break

    if not backend_config:
        LoggerHelper.write_info("Backend configuration not found in all TF files")
        return

    backend_handler_provider = BackendHandlerProviderFactory().create()
    backend_serializer = BackendSerializer(backend_handler_provider, consts.TF_MAIN_DIR, sandbox_id)
    backend_serializer.create_backend_config_override_file(backend_config)

    LoggerHelper.write_info("Successfully finish creating override file for backend files\n")


def main():
    validate_tf_main_dir_exists()

    # todo - handle case when argv[1] is not provided
    sandbox_id = sys.argv[1]
    # todo - get from argv
    torqify_data_terraform_remote_state = True
    # list of data source names from type terraform_remote_state to omit when torqifing. if empty will torqify all.
    omit_torqify_data_source_name = ["network"]

    LoggerHelper.init_logging(consts.LOG_PATH)
    try:
        LoggerHelper.write_info(f"Searching for all .tf files in directory {consts.TF_MAIN_DIR}")
        all_tf_files = FilesHelper.get_all_files(consts.TF_MAIN_DIR, ".tf")
        torqify_terraform_remote_backend(sandbox_id, all_tf_files)

        if torqify_data_terraform_remote_state:
            torqify_terraform_backend_data_source(sandbox_id, all_tf_files, omit_torqify_data_source_name)

    except Exception as exc:
        # log exception and re-raise original exception
        LoggerHelper.write_error(str(exc))
        raise


if __name__ == '__main__':
    main()
