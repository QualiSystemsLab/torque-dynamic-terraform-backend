import os
from unittest import TestCase
from unittest.mock import Mock, patch, ANY

import consts
from backend.handlers.s3_handler import S3BackendHandler
from main import torqify_terraform_backend
from models.file_info import FileInfo
from utils.logger import LoggerHelper


# todo - add tests cases for azurerm and gcs backends
class TestMain(TestCase):

    def setUp(self) -> None:
        LoggerHelper = Mock()


    @patch("main.BackendSerializer")
    def test_torqify_terraform_backend_with_s3_backend(self, backend_serializer_class_mock):
        # arrange
        sandbox_id = Mock()
        consts.TF_MAIN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          "..", "test_data", "tf_s3_backend")

        # act
        torqify_terraform_backend(sandbox_id)

        # assert
        update_backend_config = {'s3': {'bucket': 'my-bucket',
                                        'key': 'path/to/my/key' + "-" + str(sandbox_id),
                                        'region': 'us-west-2'}}
        backend_serializer_class_mock.assert_called_once_with(update_backend_config, ANY, ANY)
        self.assertIsInstance(backend_serializer_class_mock.call_args[0][1], S3BackendHandler)
        self.assertIsInstance(backend_serializer_class_mock.call_args[0][2], FileInfo)
        backend_serializer_class_mock.return_value.create_backend_override_file.assert_called_once()

    def test_torqify_terraform_backend_main_tf_dir_not_found(self):
        # arrange
        consts.TF_MAIN_DIR = str(Mock())

        # act
        with self.assertRaisesRegex(ValueError, "does not exist"):
            torqify_terraform_backend(Mock())

    @patch("main.BackendSerializer")
    def test_torqify_terraform_backend_with_no_backend(self, backend_serializer_class_mock):
        sandbox_id = Mock()
        consts.TF_MAIN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          "..", "test_data", "tf_no_backend")

        # act
        torqify_terraform_backend(sandbox_id)

        # assert
        backend_serializer_class_mock.assert_not_called()

    @patch("main.BackendSerializer")
    def test_torqify_terraform_backend_with_unsupported_backend(self, backend_serializer_class_mock):
        sandbox_id = Mock()
        consts.TF_MAIN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          "..", "test_data", "tf_unsupported_backend")

        # act
        with self.assertRaisesRegex(ValueError, "Handler not found for backend"):
            torqify_terraform_backend(sandbox_id)
