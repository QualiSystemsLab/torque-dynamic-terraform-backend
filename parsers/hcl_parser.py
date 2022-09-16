import hcl2

from utils.logger import LoggerHelper


class Hcl2Parser:
    @staticmethod
    def get_tf_file_as_dict(tf_file_path: str) -> dict:
        try:
            with(open(tf_file_path, 'r')) as client_tf_file:
                return hcl2.load(client_tf_file)
        except:
            # logging the file path that encountered the error
            LoggerHelper.write_error(f"Failed to parse tf file '{tf_file_path}'")
            # re-raising the exception so it will break the flow and its details are logged by the ExceptionWrapper
            raise

    @staticmethod
    def get_tf_backend_configuration(tf_file_path: str) -> dict:
        """
        :return: returns dict representing backend configuration in provided .tf file. Or none is returned if backend
        isn't found
        """
        backend_config = None  # type: dict
        tf_as_dict = Hcl2Parser.get_tf_file_as_dict(tf_file_path)
        for tf_configurations in tf_as_dict.get("terraform", []):
            backend_config = tf_configurations.get("backend", None)
            if backend_config:
                return next(iter(backend_config))

        return None
