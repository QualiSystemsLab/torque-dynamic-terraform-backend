import os


class FileInfo:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.file_dir = os.path.dirname(file_path)

    def __str__(self):
        return self.file_name

    def __repr__(self):
        return self.file_name
