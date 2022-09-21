import os
from unittest import TestCase
from unittest.mock import Mock

from typing import List

from models.terraform_data_source import TerraformRemoteStateDataSource
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

    def test_get_tf_data_source_remote_state(self):
        # arrange
        current_dir = os.path.dirname(os.path.abspath(__file__))
        tf_file_path = os.path.join(current_dir, "../test_data/tf_s3_backend/data.tf")
        datasource1 = Mock(spec=TerraformRemoteStateDataSource, data_source_name="network",
                           props={'backend': 's3', 'config': {'bucket': 'torque-terraform-backend-network',
                                                              'key': 'network/terraform.tfstate',
                                                              'region': 'us-east-1'}})
        datasource2 = Mock(spec=TerraformRemoteStateDataSource, data_source_name="compute",
                           props={'backend': 's3', 'config': {'bucket': 'torque-terraform-backend-compute',
                                                              'key': 'compute/terraform.tfstate',
                                                              'region': 'us-west-2'}})

        # act
        results = Hcl2Parser.get_tf_all_remote_state_data_sources(tf_file_path)

        # assert
        self.assertCountEqual([datasource2, datasource1], results)

    def test_get_tf_data_source_remote_state_nothing_found(self):
        # arrange
        current_dir = os.path.dirname(os.path.abspath(__file__))
        tf_file_path = os.path.join(current_dir, "../test_data/tf_s3_backend/main.tf")

        # act
        results = Hcl2Parser.get_tf_all_remote_state_data_sources(tf_file_path)

        # assert
        self.assertIsInstance(results, List)
        self.assertFalse(results)
