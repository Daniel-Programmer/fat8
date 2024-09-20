from fat_dir_entry import FatDirEntry
from fat_fd import FatFd


class FatFile:
    """Assign file system and file name to FAT file"""
    def __init__(self, fs, file_name):
        self.fs = fs
        self.file_name = file_name
        self.fat_dir_entry = None
        self.fat_fd = None

    def is_open(self):
        return isinstance(self.fat_fd, FatFd)

    def open(self):
        """Find/Create FatDirEntry in FAT table and return instance of FatFd to work with file"""
        if self.is_open():
            return

        self.fat_dir_entry = FatDirEntry.open(self.fs, self.file_name)
        self.fat_fd = FatFd(self.fs, self.fat_dir_entry)

        return self.fat_fd

    def close(self):
        self.fat_fd = None
        self.fat_dir_entry = None

    def delete(self):
        FatDirEntry.file_delete(self.fs, self.file_name)
        self.close()





