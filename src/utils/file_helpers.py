import os
from typing import List

from models.file_info import FileInfo


class FilesHelper:
    @staticmethod
    def get_all_files(dir_path: str, file_extension: str = None) -> List[FileInfo]:
        files: List[FileInfo] = []
        for root, directories, file_names in os.walk(dir_path):
            for file_name in file_names:
                if file_extension:
                    if file_name.endswith(file_extension):
                        files.append(FileInfo(os.path.join(root, file_name)))
                else:
                    files.append(FileInfo(os.path.join(root, file_name)))
        return files
