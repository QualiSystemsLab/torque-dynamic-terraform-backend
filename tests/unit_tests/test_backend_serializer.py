import os.path
from unittest import TestCase

from unittest.mock import Mock, patch, ANY, mock_open

from backend.backend_serializer import BackendSerializer


class TestBackendSerializer(TestCase):

    def test_create_backend_override_file(self):
        # arrange
        backend_config = Mock()
        backend_handler = Mock()
        tf_file_info = Mock()
        backend_serializer = BackendSerializer(backend_config, backend_handler, tf_file_info, Mock())
        override_file_path = Mock()
        backend_serializer._get_override_file_path = Mock(return_value=override_file_path)
        m = mock_open()

        # act
        with patch('builtins.open', m):
            backend_serializer.create_backend_override_file()

        # assert
        backend_handler.format_backend_to_hcl.assert_called_once_with(backend_config)
        backend_serializer._get_override_file_path.assert_called_once()
        m.return_value.write.assert_called_with(backend_handler.format_backend_to_hcl.return_value)

    def test_get_override_file_path(self):
        # arrange
        test_file_dir = os.path.join("/", "test1", "test2")
        tf_file_info = Mock(file_name="test.tf", file_dir=test_file_dir)
        sandbox_id = Mock()
        backend_serializer = BackendSerializer(Mock(), Mock(), tf_file_info, sandbox_id)

        # act
        result = backend_serializer._get_override_file_path()

        # assert
        self.assertEqual(result, os.path.join(test_file_dir, f"torque_backend_{sandbox_id}_override.tf"))
1