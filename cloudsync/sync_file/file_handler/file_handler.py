from abc import ABC, abstractmethod
from pathlib import Path

from ..filters import FilterParameters


class FileHandler(ABC):
    """
    Generic class that facilitates reading file metadata,
    creating, deleting and modifying files.
    """

    _file: Path = ""

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, new_file: Path):
        self._file = new_file

    @property
    @abstractmethod
    def mod_time(self):
        pass

    @property
    @abstractmethod
    def hash(self):
        pass

    @property
    @abstractmethod
    def size(self):
        pass

    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def delete(self):
        pass

    def filter(self, params: FilterParameters) -> bool:
        return params.filter_days(self.mod_time) or params.filter_name(str(self.file))
