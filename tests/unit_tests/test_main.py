import os
from unittest import TestCase
from unittest.mock import Mock, patch, ANY

import consts
from backend.handlers.s3_handler import S3BackendHandler
from main import torqify_terraform_backend, main
from models.file_info import FileInfo


class TestMain(TestCase):

    def setUp(self) -> None:
        self.patcher = patch('main.LoggerHelper')
        self.mock_logger = self.patcher.start()

    def tearDown(self) -> None:
        self.patcher.stop()

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
        backend_serializer_class_mock.assert_called_once_with(update_backend_config, ANY, ANY, sandbox_id)
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

    @patch("main.torqify_terraform_backend")
    def test_main_entrypoint_with_sandbox_id_arg(self, torqify_terraform_backend_mock):
        # arrange
        sandbox_id = Mock()
        testargs = ["prog", sandbox_id]

        # act
        with patch("sys.argv", testargs):
            main()

        # assert
        self.mock_logger.init_logging.assert_called_once()
        torqify_terraform_backend_mock.assert_called_once_with(sandbox_id)

    @patch("main.torqify_terraform_backend")
    def test_main_entrypoint_with_catch_all(self, torqify_terraform_backend_mock):
        # arrange
        testargs = ["prog", Mock()]
        torqify_terraform_backend_mock.side_effect = ValueError("mock err msg")

        # act
        with self.assertRaises(ValueError):
            with patch("sys.argv", testargs):
                main()

        # assert
        self.mock_logger.write_error.assert_called_once_with("mock err msg")
