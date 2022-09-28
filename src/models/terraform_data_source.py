class TerraformDataSource:
    def __init__(self, data_source_type: str, data_source_name: str, props: dict):
        self.data_source_type = data_source_type
        self.data_source_name = data_source_name
        self.props = props

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.data_source_name == other.data_source_name and self.props == other.props
        return False


class TerraformRemoteStateDataSource(TerraformDataSource):
    def __init__(self, data_source_name: str, props: dict):
        super().__init__("terraform_remote_state", data_source_name, props)
        self.backend_type = props["backend"]
        self.config = props["config"]
