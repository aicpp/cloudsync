import time
from typing import Union

from dropbox import Dropbox
from dropbox.files import Metadata, FileMetadata, FolderMetadata

from .file_handler import FileHandler, FileType


class DropboxFileHandler(FileHandler):

    __metadata: Union[Metadata, FileMetadata, FolderMetadata, None] = None

    def __init__(self, db_obj: Dropbox):
        self.dbx = db_obj

    def __get_metadata(self):
        if self.__metadata is None:
            self.__metadata = self.dbx.files_get_metadata(str(self.file))
        return self.__metadata

    @property
    def mod_time(self):
        metadata = self.dbx.files_get_metadata(str(self.file))
        assert isinstance(metadata, FileMetadata)

        client_modify = time.mktime(metadata.client_modified.timetuple())
        server_modify = time.mktime(metadata.server_modified.timetuple())

        if client_modify > server_modify:
            return client_modify
        return server_modify

    def create(self):
        pass

    def delete(self):
        self.dbx.files_delete_v2(str(self.file))

    def hash(self):
        metadata = self.dbx.files_get_metadata(str(self.file))
        assert isinstance(metadata, FileMetadata)

        return metadata.content_hash

    def size(self) -> int:
        return self.__get_metadata().size

    def type(self) -> FileType:
        metadata = self.__get_metadata()

        if isinstance(metadata, FileMetadata):
            return FileType.FILE

        elif isinstance(metadata, FolderMetadata):
            return FileType.FOLDER

        else:
            raise Exception(f"unknown type: {type(metadata)}")
