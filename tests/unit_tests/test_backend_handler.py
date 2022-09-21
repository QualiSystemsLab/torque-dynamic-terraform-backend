from unittest import TestCase
from unittest.mock import Mock

from backend.handlers.azurerm_handler import AzureRMBackendHandler
from backend.handlers.gcs_handler import GCSBackendHandler
from backend.handlers.s3_handler import S3BackendHandler


class TestBackendHandler(TestCase):

    def test_s3_backend_handler_add_uid_to_tfstate(self):
        # arrange
        handler = S3BackendHandler()
        backend_config = {'s3': {'bucket': 'my-bucket', 'key': 'path/to/my/key', 'region': 'us-west-2'}}
        sandbox_id = Mock()

        # act
        result = handler.add_uid_to_tfstate_for_backend_config(backend_config, str(sandbox_id))

        # check original backend config wasn't changed
        self.assertEqual(backend_config,
                         {'s3': {'bucket': 'my-bucket', 'key': 'path/to/my/key', 'region': 'us-west-2'}})
        # check result contains unique key
        self.assertEqual(result, {
            's3': {'bucket': 'my-bucket', 'key': 'path/to/my/key-' + str(sandbox_id), 'region': 'us-west-2'}})

    def test_s3_backend_handler_add_uid_to_tfstate_raises_when_tfstate_prop_not_found(self):
        # arrange
        handler = S3BackendHandler()
        backend_config = {'s3': {'bucket': 'my-bucket'}}
        sandbox_id = Mock()

        # act
        with self.assertRaisesRegex(ValueError, "property wasn't found in .* backend configurations"):
            handler.add_uid_to_tfstate_for_backend_config(backend_config, str(sandbox_id))

    def test_azurerm_backend_handler_add_uid_to_tfstate(self):
        # arrange
        handler = AzureRMBackendHandler()
        backend_config = {'azurerm': {'resource_group_name': 'SA-RG', 'storage_account_name': 'abc1234',
                                      'container_name': 'tfstate', 'key': 'prod.tfstate'}}
        sandbox_id = Mock()

        # act
        result = handler.add_uid_to_tfstate_for_backend_config(backend_config, str(sandbox_id))

        # assert
        # check original backend config wasn't changed
        self.assertEqual(backend_config, {'azurerm': {'resource_group_name': 'SA-RG', 'storage_account_name': 'abc1234',
                                                      'container_name': 'tfstate', 'key': 'prod.tfstate'}})
        # check result contains unique key
        self.assertEqual(result, {'azurerm': {'resource_group_name': 'SA-RG', 'storage_account_name': 'abc1234',
                                              'container_name': 'tfstate', 'key': f'prod-{str(sandbox_id)}.tfstate'}})

    def test_azurerm_backend_handler_add_uid_to_tfstate_raises_when_tfstate_prop_not_found(self):
        # arrange
        handler = AzureRMBackendHandler()
        backend_config = {'azurerm': {'resource_group_name': 'SA-RG'}}
        sandbox_id = Mock()

        # act
        with self.assertRaisesRegex(ValueError, "property wasn't found in .* backend configurations"):
            handler.add_uid_to_tfstate_for_backend_config(backend_config, str(sandbox_id))

    def test_gcs_backend_handler_add_uid_to_tfstate(self):
        # arrange
        handler = GCSBackendHandler()
        backend_config = {'gcs': {'bucket': 'my-bucket', 'prefix': 'terraform/state'}}
        sandbox_id = Mock()

        # act
        result = handler.add_uid_to_tfstate_for_backend_config(backend_config, str(sandbox_id))

        # assert
        # check original backend config wasn't changed
        self.assertEqual(backend_config, {'gcs': {'bucket': 'my-bucket', 'prefix': 'terraform/state'}})
        # check result contains unique key
        self.assertEqual(result, {'gcs': {'bucket': 'my-bucket', 'prefix': f'terraform/state-{str(sandbox_id)}'}})

    def test_gcs_backend_handler_add_uid_to_tfstate_raises_when_tfstate_prop_not_found(self):
        # arrange
        handler = GCSBackendHandler()
        backend_config = {'gcs': {'bucket': 'my-bucket'}}
        sandbox_id = Mock()

        # act
        with self.assertRaisesRegex(ValueError, "property wasn't found in .* backend configurations"):
            handler.add_uid_to_tfstate_for_backend_config(backend_config, str(sandbox_id))

    def test_s3_backend_handeler_format_backend_to_hcl(self):
        # arrange
        handler = S3BackendHandler()
        backend_config = {'s3': {'bucket': 'my-bucket', 'key': 'path/to/my/key', 'region': 'us-west-2'}}

        # act
        result = handler.format_backend_to_hcl(backend_config)

        # assert
        expected_result = """terraform {
\tbackend "s3" {
\t\tbucket = "my-bucket"
\t\tkey = "path/to/my/key"
\t\tregion = "us-west-2"
\t}
}
"""
        self.assertEqual(expected_result, result)

    def test_azurerm_backend_handeler_format_backend_to_hcl(self):
        # arrange
        handler = AzureRMBackendHandler()
        backend_config = {'azurerm': {'resource_group_name': 'SA-RG', 'storage_account_name': 'abc1234',
                                      'container_name': 'tfstate', 'key': 'prod.tfstate'}}

        # act
        result = handler.format_backend_to_hcl(backend_config)

        # assert
        expected_result = """terraform {
\tbackend "azurerm" {
\t\tresource_group_name = "SA-RG"
\t\tstorage_account_name = "abc1234"
\t\tcontainer_name = "tfstate"
\t\tkey = "prod.tfstate"
\t}
}
"""
        self.assertEqual(expected_result, result)

    def test_gcs_backend_handeler_format_backend_to_hcl(self):
        # arrange
        handler = GCSBackendHandler()
        backend_config = {'gcs': {'bucket': 'my-bucket', 'prefix': 'terraform/state'}}

        # act
        result = handler.format_backend_to_hcl(backend_config)

        # assert
        expected_result = """terraform {
\tbackend "gcs" {
\t\tbucket = "my-bucket"
\t\tprefix = "terraform/state"
\t}
}
"""
        self.assertEqual(expected_result, result)
