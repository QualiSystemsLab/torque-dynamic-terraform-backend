import hcl2

from utils.logger import LoggerHelper


class Hcl2Parser:
    @staticmethod
    def get_tf_file_as_dict(tf_file_path: str) -> dict:
        with (open(tf_file_path, 'r')) as client_tf_file:
            return hcl2.load(client_tf_file)

    @staticmethod
    def get_tf_backend_configuration(tf_file_path: str) -> dict:
        """
        :return: returns dict representing backend configuration in provided .tf file. Or none is returned if backend
        isn't found
        """
        tf_as_dict = Hcl2Parser.get_tf_file_as_dict(tf_file_path)
        for tf_configurations in tf_as_dict.get("terraform", []):
            backend_config = tf_configurations.get("backend", None)
            if backend_config:
                return next(iter(backend_config))

        return None
