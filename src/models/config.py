from typing import List


class ExecConfig:
    def __init__(self):
        self.sandbox_id: str = ""
        self.data: bool = False
        self.exclude: List[str] = []
