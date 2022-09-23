#######################################
# Notes:
# - supports Terraform 0.12.0 and above
# - supported backend types: S3 Bucket(s3), Azure Storage (azurerm), Goggle Cloud Storage (gcs)
# - to add support for additional backends implement abstract class BaseBackendHandler and register new handler in
#   BackendHandlerProviderFactory
#
import argparse
import json
import os
from typing import List

import consts
from backend.backend_handler_provider_factory import BackendHandlerProviderFactory
from backend.backend_serializer import BackendSerializer
from models.config import ExecConfig
from models.file_info import FileInfo
from parsers.hcl_parser import Hcl2Parser
from utils.file_helpers import FilesHelper
from utils.logger import LoggerHelper


def validate_tf_main_dir_exists() -> None:
    if not os.path.exists(consts.TF_MAIN_DIR):
        raise ValueError(f"Path {consts.TF_MAIN_DIR} does not exist")


def torqify_terraform_backend_data_source(sandbox_id: str, all_tf_files: List[FileInfo],
                                          exclude_data_source_names: List[str]):
    LoggerHelper.write_info("Searching for remote backend data sources")
    remote_state_data_sources = []
    for tf_file in all_tf_files:
        data_sources = Hcl2Parser.get_tf_all_remote_state_data_sources(tf_file.file_path)
        if not data_sources:
            continue
        data_sources_to_exclude = list(filter(lambda x: x.data_source_name in exclude_data_source_names, data_sources))
        if data_sources_to_exclude:
            data_source_names_to_exclude = list(map(lambda x: x.data_source_name, data_sources_to_exclude))
            LoggerHelper.write_info(f"Excluding remote backend data sources {','.join(data_source_names_to_exclude)} "
                                    f"in TF file {tf_file.file_path}")
        data_source_to_torqify = list(filter(lambda x: x.data_source_name not in exclude_data_source_names, data_sources))
        remote_state_data_sources.extend(list(data_source_to_torqify))

    if not remote_state_data_sources:
        LoggerHelper.write_info("No remote backend data sources found")

    backend_handler_provider = BackendHandlerProviderFactory().create()
    backend_serializer = BackendSerializer(backend_handler_provider, consts.TF_MAIN_DIR, sandbox_id)
    backend_serializer.create_backend_remote_state_datasource_override_file(remote_state_data_sources)

    LoggerHelper.write_info("Successfully finish creating override file for backend remote state data sources\n")


def torqify_terraform_remote_backend(sandbox_id: str, all_tf_files: List[FileInfo]):
    LoggerHelper.write_info("Searching for backend configurations")
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


def parse_args() -> ExecConfig:
    config = ExecConfig()
    parser = argparse.ArgumentParser(description="Automatically add sandbox id to terraform remote backend",)
    parser.add_argument("sandbox_id", help="The Torque sandbox ID. This value will be used for uniqueness.")
    parser.add_argument('-d', '--data', action='store_true',
                        help="If this flag is provided, will also add sandbox id to all remote_state data sources."
                             "To exclude certain remote_state data sources use the '-e' option.")
    parser.add_argument('-e', '--exclude', type=str, action="extend", nargs='*',
                        help="Use this flag to provide a list of names of remote_state data sources to exclude from "
                             "adding the sandbox id automatically. If this flag is provided without also specifying "
                             "the '-d'/'--data' flag then it will be ignored.")
    return parser.parse_args(namespace=config)


def main():
    validate_tf_main_dir_exists()

    args = parse_args()

    LoggerHelper.init_logging(consts.LOG_PATH)
    try:
        LoggerHelper.write_info(f"Searching for all .tf files in directory {consts.TF_MAIN_DIR}")
        all_tf_files = FilesHelper.get_all_files(consts.TF_MAIN_DIR, ".tf")
        torqify_terraform_remote_backend(args.sandbox_id, all_tf_files)

        if args.data:
            torqify_terraform_backend_data_source(args.sandbox_id, all_tf_files, args.exclude)

    except Exception as exc:
        # log exception and re-raise original exception
        LoggerHelper.write_error(str(exc))
        raise


if __name__ == '__main__':
    main()
