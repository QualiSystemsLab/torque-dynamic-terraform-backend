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

from backend.backend_handler_provider_factory import BackendHandlerProviderFactory
from backend.backend_serializer import BackendSerializer
import consts
from parsers.hcl_parser import Hcl2Parser
from utils.file_helpers import FilesHelper
from utils.logger import LoggerHelper


def torqify_terraform_backend(sandbox_id: str):
    main_tf_dir = consts.TF_MAIN_DIR
    if not os.path.exists(main_tf_dir):
        raise ValueError(f"Path {main_tf_dir} does not exist")

    LoggerHelper.write_info(f"Searching for backend configurations in directory {main_tf_dir}")
    all_tf_files = FilesHelper.get_all_files(main_tf_dir, ".tf")
    backend_config = {}
    tf_file_backend = None
    # backend configuration can appear only one time so we are searching for the first occurrence
    for tf_file in all_tf_files:
        backend_config = Hcl2Parser.get_tf_backend_configuration(tf_file.file_path)
        if backend_config:
            tf_file_backend = tf_file
            LoggerHelper.write_info(f"Found backend configurations in file '{tf_file.file_path}': "
                                    f"{json.dumps(backend_config)}")
            break

    if not backend_config:
        LoggerHelper.write_info("Backend configuration not found in all TF files")
        return

    backend_handler = BackendHandlerProviderFactory().create()\
        .get_handler(backend_config)
    if not backend_handler:
        raise ValueError(f"Handler not found for backend: {json.dumps(backend_config)}")

    updated_backend_config = backend_handler.add_uid_to_tfstate(backend_config, sandbox_id)

    backend_serializer = BackendSerializer(updated_backend_config, backend_handler, tf_file_backend)
    backend_serializer.create_backend_override_file()

    LoggerHelper.write_info("Successfully finish creating override file for backend files\n")


def main():
    # todo - handle case when argv[1] is not provided
    sandbox_id = sys.argv[1]

    LoggerHelper.init_logging(consts.LOG_PATH)
    try:
        torqify_terraform_backend(sandbox_id)
    except Exception as exc:
        # log exception and re-raise original exception
        LoggerHelper.write_error(str(exc))
        raise


if __name__ == '__main__':
    main()
