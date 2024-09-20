import struct
from math import ceil, floor

from cache import Cache
from constants import *


class Fat8:
    """FAT8 - file system"""
    def __init__(self):
        self.cache = None                   # virtual drive
        self.blocks_per_clust = None        # number of blocks in one cluter
        self.root_directory_blocks = None   # number of blocks in root directory
        self.data_blocks = None             # number of blocks which can be used
        self.size = None                    # size of file system

    def __repr__(self):
        return (f"Fat8: (blocks_per_clust: {self.blocks_per_clust}, root_directory_blocks: {self.root_directory_blocks}, "
                f"data_blocks: {self.data_blocks}, size: {self.size}, fs_blocks: {self.fs_size_blocks()})")

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def _empty_fat():
        fat = bytearray([0xff] * 254)
        return fat.ljust(BLOCK_SIZE, b'\0')

    @staticmethod
    def _empty_block():
        return bytearray([0x00] * BLOCK_SIZE)

    @staticmethod
    def _root_directory_blocks():
        return ceil(DIR_ENTRY_SIZE * FAT_MAX_CLUSTERS / BLOCK_SIZE)

    @staticmethod
    def first_root_directory_block():
        return BOOT_BLOCK_SIZE + FAT_BLOCK_SIZE

    def _data_blocks_size(self):
        """Return number of all blocks for data"""
        return self.cache.drive.number_of_blocks - self.root_directory_blocks - BOOT_BLOCK_SIZE - FAT_BLOCK_SIZE

    def _blocks_per_cluster(self):
        return floor(self._data_blocks_size() / FAT_MAX_CLUSTERS)

    def _actual_data_block_size(self):
        """Return number of blocks remaining for the data"""
        return self._blocks_per_cluster() * FAT_MAX_CLUSTERS

    def _first_data_block(self):
        return (BOOT_BLOCK_SIZE + FAT_BLOCK_SIZE + self.root_directory_blocks) * self.blocks_per_clust

    def _convert_boot_block_to_bin(self):
        """
        Return boot block in binary
        1 byte - blocks per cluter, 4 byty - size of file system
        4 byty - size of root directory, 4 byty - size of data blocks
        """
        return struct.pack(f'BIII', self.blocks_per_clust, self.size, self.root_directory_blocks, self.data_blocks)

    def _read_boot_block(self):
        boot_block = self.cache.read(0)
        return boot_block.data[:STRUCT_BUFFER]

    def _load_boot_block_from_bin(self):
        boot_block_data = self._read_boot_block()
        self.blocks_per_clust, self.size, self.root_directory_blocks, self.data_blocks = struct.unpack(f'BIII', boot_block_data)

    def _write_boot_block(self, data):
        """Write boot block to virtual drive"""
        self.cache.write(0, data)

    def _read_fat_block(self):
        """Read fat block from virtual drive from binary data"""
        fat_block = self.cache.read(1)
        fat_block_data = fat_block.data[:FAT_MAX_CLUSTERS]
        return bytearray(fat_block_data)

    def _write_fat_block(self, data):
        """Write fat block to virtual drive"""
        self.cache.write(1, data)

    def _empty_root_block(self):
        root_block_id_start = BOOT_BLOCK_SIZE + FAT_BLOCK_SIZE
        for block_id in range(root_block_id_start, root_block_id_start + self.root_directory_blocks):
            self.cache.write(block_id, self._empty_block())

    def _empty_data_block(self):
        data_block_id_start = BOOT_BLOCK_SIZE + FAT_BLOCK_SIZE + self.root_directory_blocks
        for block_id in range(data_block_id_start, data_block_id_start + self.data_blocks):
            self.cache.write(block_id, self._empty_block())

    def get_empty_cluster(self):
        """Return empty cluster in FAT table"""
        fat_block = self._read_fat_block()
        if EMPTY_CLUSTER in fat_block:
            return fat_block.index(EMPTY_CLUSTER)
        return None

    def get_empty_clusters(self):
        """Return all empty clusters in FAT table"""
        fat_block = self._read_fat_block()
        if EMPTY_CLUSTER in fat_block:
            return [idx for idx, el in enumerate(fat_block) if el == EMPTY_CLUSTER]
        return None

    def get_next_cluster(self, cluster_id):
        """Return cluster_id of next cluster"""
        return self._read_fat_block()[cluster_id]

    def get_last_cluster(self, first_cluster):
        """Return last cluster of virtual drive"""
        clusters = self.get_file_clusters(first_cluster)
        return clusters[len(clusters) - 1]

    def get_file_clusters(self, first_cluster):
        """Return cluster index list of virtual drive"""
        clusters = [first_cluster]
        current_cluster_id = first_cluster
        next_cluster = self.get_next_cluster(current_cluster_id)

        while next_cluster != EOC_CLUSTER:
            current_cluster_id = next_cluster
            clusters += [next_cluster]
            next_cluster = self.get_next_cluster(current_cluster_id)

        return clusters

    def write_value_to_cluster(self, cluster_id, value):
        """Write value to cluster in FAT"""
        fat_block = self._read_fat_block()
        fat_block[cluster_id] = value
        self._write_fat_block(fat_block)

    def write_next_cluster_to_cluster(self, cluster_id, new_clusted_id):
        """Write value of next cluster to current cluster"""
        if not 0 <= new_clusted_id <= FAT_MAX_CLUSTERS:
            raise ValueError("Not valid new cluster id")
        self.write_value_to_cluster(cluster_id, new_clusted_id)

    def data_block_read(self, block_id, count):
        data = bytearray()
        for idx in range(block_id, block_id + count):
            block = self.cache.read(idx)
            data.extend(block.data)
        return data

    def data_cluster_read(self, cluster_id):
        offset_block_id = (cluster_id * self.blocks_per_clust) + self._first_data_block()
        return self.data_block_read(offset_block_id, self.blocks_per_clust)

    def data_block_write(self, block_id, count, data):
        data_index_start = 0
        data_index_end = BLOCK_SIZE
        for idx in range(block_id, block_id + count):
            self.cache.write(idx, data[data_index_start:data_index_end])
            data_index_start += data_index_end
            data_index_end += BLOCK_SIZE

    def data_cluster_write(self, cluster_id, data):
        offset_block_id = (cluster_id * self.blocks_per_clust) + self._first_data_block()
        return self.data_block_write(offset_block_id, self.blocks_per_clust, data)

    def fs_size_blocks(self):
        return BOOT_BLOCK_SIZE + FAT_BLOCK_SIZE + self._root_directory_blocks() + self.data_blocks

    def fs_size(self):
        return self.fs_size_blocks() * BLOCK_SIZE

    def format(self, drive):
        if not isinstance(drive, Cache):
            raise TypeError("Choosed drive is not instance of Cache")
        self.cache = drive

        self.root_directory_blocks = self._root_directory_blocks()
        self.blocks_per_clust = self._blocks_per_cluster()
        self.data_blocks = self._actual_data_block_size()
        self.size = self.fs_size()

        # zapis boot bloku na disk
        # write boot block to virtual drive
        self._write_boot_block(self._convert_boot_block_to_bin())
        # set FAT block
        self._write_fat_block(self._empty_fat())
        # empty rest of virtual drive
        self._empty_root_block()
        self._empty_data_block()
        # clear cache
        self.cache.clear_cache()

    def open(self, drive):
        self.cache = drive
        self._load_boot_block_from_bin()

    def show_cache(self):
        return self.cache.show_cache()
