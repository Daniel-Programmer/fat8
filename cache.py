import collections
from block import Block
from virtual_drive import VirtualDrive


class Cache:
    """Cache for virtual drive"""
    def __init__(self, drive, capacity):
        if capacity < 1:
            raise ValueError("Not enough capacity")
        if not isinstance(drive, VirtualDrive):
            raise TypeError("Drive is not instance of VirtualDrive")
        self.drive = drive
        self.capacity = capacity
        self.queue = collections.deque()

    def write(self, block_id, data):
        """Write data to cache and then to disk"""
        new_block = Block(block_id, False, data)

        if self.is_full():
            self.create_space()

        if self.is_in_cache(block_id):
            self.remove_from_cache(new_block)

        self.queue.appendleft(new_block)
        self.drive.write(new_block)

    def read(self, block_id):
        """Read block from cache, if it is not there then read from virtual drive"""
        if 0 <= block_id < self.capacity and self.is_in_cache(block_id):
            index = self.queue.index(Block(block_id, False, False))
            block = self.queue[index]
            self.queue.remove(block)
            block.ready_to_delete = False
            self.queue.appendleft(block)
            return block

        new_block = Block(block_id, False, self.drive.read(block_id))
        self.queue.appendleft(new_block)
        return new_block

    def is_empty(self):
        return len(self.queue) == 0

    def is_full(self):
        return len(self.queue) == self.capacity

    def is_in_cache(self, block_id):
        return self.queue.count(Block(block_id)) == 1

    def create_space(self):
        """Second chance - Create empty space for block in cache"""
        while True:
            candidate = self.queue.pop()
            if candidate.ready_to_delete:
                return
            candidate.ready_to_delete = True
            self.queue.appendleft(candidate)

    def remove_from_cache(self, block_id):
        self.queue.remove(block_id)

    def clear_cache(self):
        self.queue.clear()

    def show_cache(self):
        return self.queue

    def drv_stat(self):
        """Return size of virtual drive"""
        return self.drive.size
