import time

from dropbox import Dropbox
from dropbox.files import FileMetadata

from .file_handler import FileHandler


class DropboxFileHandler(FileHandler):

    def __init__(self, db_obj: Dropbox):
        self.dbx = db_obj

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

    def size(self):
        metadata = self.dbx.files_get_metadata(str(self.file))
        assert isinstance(metadata, FileMetadata)

        return metadata.size
