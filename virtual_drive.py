import os
from constants import BLOCK_SIZE


class VirtualDrive:
    """Class of virtual drive with name and size"""
    def __init__(self, file_name, size):
        self.file_name = file_name
        self.number_of_blocks = size
        if size == 0:
            raise ValueError("No size of drive")
        self.size = size * BLOCK_SIZE

    @staticmethod
    def manufacture(file_name, size=0):
        """Create instance of virtual drive"""
        if size == 0:
            raise ValueError("No size of drive")

        os.open(file_name, os.O_CREAT)
        fd = os.open(file_name, os.O_RDWR)
        os.ftruncate(fd, size)
        os.close(fd)

    @classmethod
    def open(cls, file_name):
        """Open virtual drive and return instance of VirtualDrive class"""
        file_stats = os.stat(file_name)
        return cls(file_name, file_stats.st_size)

    def read(self, block_id):
        """Read one block from virtual drive"""
        if 0 <= block_id < self.number_of_blocks:
            with open(self.file_name, 'rb') as file:
                file.seek((block_id * BLOCK_SIZE))
                data = file.read(BLOCK_SIZE)
                return data
        else:
            return ValueError("Block id is not in range of file")

    def write(self, block):
        """Write block to virtual drive"""
        if 0 <= block.block_id < self.number_of_blocks:
            with open(self.file_name, 'r+b') as file:
                position = block.block_id * BLOCK_SIZE
                file.seek(position)
                file.write(block.data)
        else:
            return ValueError("Block id is not in range of file")

    def stat(self):
        """Return size of virtual drive"""
        return self.size

