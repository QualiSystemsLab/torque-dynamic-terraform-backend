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

    def test_get_tf_remote_state_data_source_safely_not_raises(self):
        # empty data source object
        datasource_object = {}
        result = Hcl2Parser.get_tf_remote_state_data_source_safely(datasource_object)
        self.assertIsNone(result)

        # wrong type for 'terraform_remote_state' value
        datasource_object = {"terraform_remote_state": "mock"}
        result = Hcl2Parser.get_tf_remote_state_data_source_safely(datasource_object)
        self.assertIsNone(result)

        # multiple values in terraform_remote_state prop
        datasource_object = {"terraform_remote_state": {"a": "b", "c": "d"}}
        result = Hcl2Parser.get_tf_remote_state_data_source_safely(datasource_object)
        self.assertIsNone(result)

        # terraform_remote_state data source name has wrong type
        datasource_object = {"terraform_remote_state": {"some_name": "mock"}}
        result = Hcl2Parser.get_tf_remote_state_data_source_safely(datasource_object)
        self.assertIsNone(result)

        # terraform_remote_state data source missing 'backend'
        datasource_object = {"terraform_remote_state": {"some_name": {"config": ""}}}
        result = Hcl2Parser.get_tf_remote_state_data_source_safely(datasource_object)
        self.assertIsNone(result)

        # terraform_remote_state data source missing 'config'
        datasource_object = {"terraform_remote_state": {"some_name": {"backend": ""}}}
        result = Hcl2Parser.get_tf_remote_state_data_source_safely(datasource_object)
        self.assertIsNone(result)

        # terraform_remote_state data source is correct
        datasource_object = {"terraform_remote_state": {"some_name": {"backend": "", "config": ""}}}
        result = Hcl2Parser.get_tf_remote_state_data_source_safely(datasource_object)
        self.assertIsInstance(result, TerraformRemoteStateDataSource)
