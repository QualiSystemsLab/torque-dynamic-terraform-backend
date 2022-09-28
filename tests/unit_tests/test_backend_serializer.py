import os.path
from unittest import TestCase

from unittest.mock import Mock, patch, ANY, mock_open, call

from backend.backend_serializer import BackendSerializer


class TestBackendSerializer(TestCase):

    def test_create_backend_override_file(self):
        # arrange
        backend_handler = Mock()
        backend_handler_provider = Mock()
        backend_handler_provider.get_handler.return_value = backend_handler
        test_file_dir = Mock()
        sandbox_id = Mock()
        backend_serializer = BackendSerializer(backend_handler_provider, test_file_dir, sandbox_id)
        override_file_path = Mock()
        backend_serializer._get_backend_config_override_file_path = Mock(return_value=override_file_path)
        backend_config = Mock()
        m = mock_open()

        # act
        with patch('builtins.open', m):
            backend_serializer.create_backend_config_override_file(backend_config)

        # assert
        backend_serializer._get_backend_config_override_file_path.assert_called_once()
        m.return_value.write.assert_called_with(backend_handler.format_backend_to_hcl.return_value)

    def test_get_override_file_path(self):
        # arrange
        test_file_dir = os.path.join("/", "test1", "test2")
        sandbox_id = Mock()
        backend_serializer = BackendSerializer(Mock(), test_file_dir, sandbox_id)

        # act
        result = backend_serializer._get_backend_config_override_file_path()

        # assert
        self.assertEqual(result, os.path.join(test_file_dir, f"torque_backend_{sandbox_id}_override.tf"))

    def test_create_backend_remote_state_datasource_override_file(self):
        # arrange
        backend_handler = Mock()
        backend_handler_provider = Mock()
        backend_handler_provider.get_handler_by_type.return_value = backend_handler
        tf_dir = str(Mock())
        sandbox_id = str(Mock())
        serializer = BackendSerializer(backend_handler_provider, tf_dir, sandbox_id)
        m = mock_open()
        datasources_list = [Mock(), Mock()]

        # act
        with patch('builtins.open', m):
            serializer.create_backend_remote_state_datasource_override_file(datasources_list)

        # assert
        calls = [call(backend_handler.format_remote_state_data_source_with_uid.return_value),
                 call(backend_handler.format_remote_state_data_source_with_uid.return_value)]
        m.return_value.write.assert_has_calls(calls, any_order=True)
