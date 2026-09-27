"""Small app-local encrypted-session database, never a shared account store."""
from contextlib import contextmanager
import os
from pathlib import Path
import sqlite3
import stat


class Database:
    def __init__(self, path):
        self.path = Path(path)
        parent = self.path.parent
        info = parent.stat()
        if parent.is_symlink() or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise ValueError('private_state_directory_required')
        fd = os.open(self.path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077 or info.st_nlink != 1:
                raise ValueError('private_database_required')
        finally:
            os.close(fd)

    @contextmanager
    def db(self):
        connection = sqlite3.connect(str(self.path), timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute('PRAGMA synchronous=FULL')
        try:
            yield connection
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()
