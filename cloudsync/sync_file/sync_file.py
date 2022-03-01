from pathlib import Path

from .file_handler import LocalFileHandler
from .filters import FilterParameters


class SyncFile:
    """
    File object for easy comparison between local and Dropbox files.
    Allows operations (such as equality checking) to be done independently
    of the file source.
    """

    def __init__(self, raw_file: Path, file_handler=None):
        self.file_handler = file_handler if file_handler is not None else LocalFileHandler()
        self.file_handler.file = raw_file
        self._name = raw_file

    @property
    def mod_time(self):
        return self.file_handler.mod_time

    @property
    def name(self):
        return self._name.name

    @property
    def hash(self):
        return self.file_handler.hash()

    @property
    def size(self):
        return self.file_handler.size()

    def filter(self, params: FilterParameters) -> bool:
        return self.file_handler.filter(params)

    def delete(self):
        self.file_handler.delete()

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.name)

    def __eq__(self, other: 'SyncFile'):
        if other.name != self.name:
            return False

        if other.size != self.size:
            return False

        if self.mod_time < other.mod_time:
            return self.hash == other.hash

        return False

    def __ne__(self, other):
        return not self == other
