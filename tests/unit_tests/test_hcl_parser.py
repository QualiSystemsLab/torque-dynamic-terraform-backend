import os
from unittest import TestCase

from parsers.hcl_parser import Hcl2Parser


class TestHclParser(TestCase):

    def test_get_tf_file_as_dict(self):
        # arrange
        current_dir = os.path.dirname(os.path.abspath(__file__))
        tf_file_path = os.path.join(current_dir, "../test_data/tf_s3_backend/main.tf")

        # act
        tf_as_dict = Hcl2Parser.get_tf_file_as_dict(tf_file_path)

        # assert - check that dict contains top level elements "terraform", "provider", "resource", "data"
        self.assertIn("terraform", tf_as_dict)
        self.assertIn("provider", tf_as_dict)
        self.assertIn("resource", tf_as_dict)
        self.assertIn("data", tf_as_dict)

    def test_get_tf_backend_configuration(self):
        # arrange
        current_dir = os.path.dirname(os.path.abspath(__file__))
        tf_file_path = os.path.join(current_dir, "../test_data/tf_s3_backend/main.tf")

        # act
        backend_config = Hcl2Parser.get_tf_backend_configuration(tf_file_path)

        # assert
        self.assertIsNotNone(backend_config)
        self.assertIsInstance(backend_config, dict)
        self.assertIn("s3", backend_config)

    def test_get_tf_backend_configuration_no_backend(self):
        # arrange
        current_dir = os.path.dirname(os.path.abspath(__file__))
        tf_file_path = os.path.join(current_dir, "../test_data/tf_no_backend/main.tf")

        # act
        backend_config = Hcl2Parser.get_tf_backend_configuration(tf_file_path)

        # assert
        self.assertIsNone(backend_config)
