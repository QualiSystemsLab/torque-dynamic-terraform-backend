import os
from unittest import TestCase
from unittest.mock import Mock, patch, ANY

import consts
from backend.handlers.s3_handler import S3BackendHandler
from main import torqify_terraform_remote_backend, main, validate_tf_main_dir_exists, \
    torqify_terraform_backend_data_source
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
        tf_file = Mock(file_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              "..", "test_data", "tf_s3_backend", "main.tf"))

        # act
        torqify_terraform_remote_backend(sandbox_id, [tf_file])

        # assert
        update_backend_config = {'s3': {'bucket': 'my-bucket',
                                        'key': 'path/to/my/key',
                                        'region': 'us-west-2'}}
        backend_serializer_class_mock.return_value.create_backend_config_override_file. \
            assert_called_once_with(update_backend_config)

    def test_validate_tf_main_dir_exists_raises(self):
        # arrange
        consts.TF_MAIN_DIR = str(Mock())

        # act
        with self.assertRaisesRegex(ValueError, "does not exist"):
            validate_tf_main_dir_exists()

    def test_validate_tf_main_dir_exists_passes(self):
        # arrange
        consts.TF_MAIN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          "..", "test_data", "tf_no_backend")

        # act
        validate_tf_main_dir_exists()

    @patch("main.BackendSerializer")
    def test_torqify_terraform_backend_with_no_backend(self, backend_serializer_class_mock):
        sandbox_id = Mock()
        tf_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "test_data", "tf_no_backend", "main.tf")
        tf_file = FileInfo(tf_file_path)

        # act
        torqify_terraform_remote_backend(sandbox_id, [tf_file])

        # assert
        backend_serializer_class_mock.assert_not_called()

    @patch("main.FilesHelper")
    @patch("main.torqify_terraform_backend_data_source")
    @patch("main.torqify_terraform_remote_backend")
    def test_main_entrypoint_with_sandbox_id_arg(self, torqify_terraform_backend_mock,
                                                 torqify_terraform_backend_data_source_mock, files_helper_mock):
        # arrange
        sandbox_id = str(Mock())
        testargs = ["prog", sandbox_id]
        consts.TF_MAIN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          "..", "test_data", "tf_s3_backend")

        # act
        with patch("sys.argv", testargs):
            main()

        # assert
        self.mock_logger.init_logging.assert_called_once()
        torqify_terraform_backend_mock.assert_called_once_with(sandbox_id, files_helper_mock.get_all_files.return_value)
        torqify_terraform_backend_data_source_mock.assert_not_called()

    @patch("main.validate_tf_main_dir_exists")
    @patch("main.torqify_terraform_remote_backend")
    def test_main_entrypoint_with_catch_all(self, torqify_terraform_backend_mock, validate_tf_main_dir_mock):
        # arrange
        testargs = ["prog", str(Mock())]
        torqify_terraform_backend_mock.side_effect = ValueError("mock err msg")

        # act
        with self.assertRaises(ValueError):
            with patch("sys.argv", testargs):
                main()

        # assert
        self.mock_logger.write_error.assert_called_once_with("mock err msg")

    @patch("main.FilesHelper")
    @patch("main.torqify_terraform_backend_data_source")
    def test_main_entrypoint_with_datasource_arg(self, torqify_terraform_backend_datasource_mock, files_helper_mock):
        # arrange
        sandbox_id = str(Mock())
        testargs = ["prog", sandbox_id, "-d"]
        consts.TF_MAIN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          "..", "test_data", "tf_s3_backend")

        # act
        with patch("sys.argv", testargs):
            main()

        # assert
        torqify_terraform_backend_datasource_mock. \
            assert_called_once_with(sandbox_id, files_helper_mock.get_all_files.return_value, [])

    @patch("main.FilesHelper")
    @patch("main.torqify_terraform_backend_data_source")
    def test_main_entrypoint_with_exclude_arg(self, torqify_terraform_backend_datasource_mock, files_helper_mock):
        # arrange
        sandbox_id = str(Mock())
        testargs = ["prog", sandbox_id, "-d", "-e", "network", "config"]
        consts.TF_MAIN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          "..", "test_data", "tf_s3_backend")

        # act
        with patch("sys.argv", testargs):
            main()

        # assert
        torqify_terraform_backend_datasource_mock. \
            assert_called_once_with(sandbox_id, files_helper_mock.get_all_files.return_value, ["network", "config"])

    @patch("main.BackendSerializer")
    def test_torqify_terraform_backend_data_source_no_excludes(self, backend_serializer_class_mock):
        # arrange
        sandbox_id = str(Mock())
        main_tf_file = Mock(file_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                   "..", "test_data", "tf_s3_backend", "main.tf"))
        data_tf_file = Mock(file_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                   "..", "test_data", "tf_s3_backend", "data.tf"))

        # act
        torqify_terraform_backend_data_source(sandbox_id, [main_tf_file, data_tf_file], [])

        # assert
        # assert that the main method was called and with the correct number of arguments
        method_to_assert = \
            backend_serializer_class_mock.return_value.create_backend_remote_state_datasource_override_file
        method_to_assert.assert_called_once()
        self.assertEqual(len(method_to_assert.call_args_list), 1)
        self.assertEqual(len(method_to_assert.call_args_list[0].args[0]), 2)

    @patch("main.BackendSerializer")
    def test_torqify_terraform_backend_data_source_with_exclude(self, backend_serializer_class_mock):
        # arrange
        sandbox_id = str(Mock())
        main_tf_file = Mock(file_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                   "..", "test_data", "tf_s3_backend", "main.tf"))
        data_tf_file = Mock(file_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                   "..", "test_data", "tf_s3_backend", "data.tf"))

        # act
        torqify_terraform_backend_data_source(sandbox_id, [main_tf_file, data_tf_file], ["compute"])

        # assert
        # assert that the main method was called and with the correct number of arguments
        method_to_assert = \
            backend_serializer_class_mock.return_value.create_backend_remote_state_datasource_override_file
        method_to_assert.assert_called_once()
        self.assertEqual(len(method_to_assert.call_args_list), 1)
        self.assertEqual(len(method_to_assert.call_args_list[0].args[0]), 1)


    @patch("main.BackendSerializer")
    def test_torqify_terraform_backend_data_source_no_datasources_found(self, backend_serializer_class_mock):
        # arrange
        sandbox_id = str(Mock())
        main_tf_file = Mock(file_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                   "..", "test_data", "tf_s3_backend", "main.tf"))

        # act
        torqify_terraform_backend_data_source(sandbox_id, [main_tf_file], [])

        # assert
        backend_serializer_class_mock.return_value.\
            create_backend_remote_state_datasource_override_file.assert_not_called()

