import hashlib
import os

from .file_handler import FileHandler

DROPBOX_HASH_CHUNK_SIZE = 4*1024*1024


class LocalFileHandler(FileHandler):

    @property
    def mod_time(self):
        return int(os.path.getmtime(self.file))

    def create(self):
        self.file.open("a+")

    def delete(self):
        self.file.unlink()

    def hash(self):
        with open(self.file, 'rb') as f:
            block_hashes = b''
            while True:
                chunk = f.read(DROPBOX_HASH_CHUNK_SIZE)
                if not chunk:
                    break
                block_hashes += hashlib.sha256(chunk).digest()
            return hashlib.sha256(block_hashes).hexdigest()

    def size(self):
        return self.file.stat().st_size


