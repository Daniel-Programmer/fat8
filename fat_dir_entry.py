import struct
from math import floor

from constants import *


class FatDirEntry:
    def __init__(self, file_name, fst_cluster_id, size):
        if len(file_name) > FILE_NAME_MAX_SIZE:
            raise ValueError("File name is longer than expected")
        self.file_name = file_name

        if not (0 <= fst_cluster_id <= FAT_MAX_CLUSTERS):
            raise ValueError("Cluster id is not valid")
        self.fst_cluster_id = fst_cluster_id
        self.size = size  # number of clusters

    def __repr__(self):
        return f"FatDirEntry({self.file_name}, {self.fst_cluster_id}, {self.size})"

    def __str__(self):
        return self.__repr__()

    def __eq__(self, file_name):
        return self.file_name == file_name

    @classmethod
    def from_binary(cls, binary_data):
        file_name_bytes, fst_cluster_id, size = struct.unpack(f'{FILE_NAME_MAX_SIZE}sBI', binary_data)
        file_name = file_name_bytes.decode('utf8').rstrip('\0')
        return cls(file_name, fst_cluster_id, size)

    def to_binary(self):
        return struct.pack(f'{FILE_NAME_MAX_SIZE}sBI', self.file_name.encode('utf-8').ljust(FILE_NAME_MAX_SIZE, b'\0'),
                           self.fst_cluster_id, self.size)

    @staticmethod
    def read_single_fat_dir_entry(start, end, data):
        return data[start:end]

    @staticmethod
    def get_entries_from_root_block(root_dir_block):
        """Return list of FatDirEntry in one block in root directory"""
        entries = []
        max_files = 0

        for file_dir_entry in range(0, BLOCK_SIZE, DIR_ENTRY_SIZE):

            # if number of files is same as number of possible clusters
            if max_files is FAT_MAX_CLUSTERS:
                break

            binary_file_data = FatDirEntry.read_single_fat_dir_entry(file_dir_entry, file_dir_entry + DIR_ENTRY_SIZE,
                                                                     root_dir_block.data)

            # if next file does not contain bytes
            if binary_file_data == bytearray([0x00] * DIR_ENTRY_SIZE) or binary_file_data == b'':
                continue

            entries += [FatDirEntry.from_binary(binary_file_data)]
            max_files += 1

        return entries

    @staticmethod
    def read_root_dir(fs):
        """Return all FatDirEntry in root directory"""
        root_dir_block_id = BOOT_BLOCK_SIZE + FAT_BLOCK_SIZE  # first block of root dir
        root_dir_end_block_id = root_dir_block_id + fs.root_directory_blocks  # last block of root dir

        root_dir_block = fs.cache.read(root_dir_block_id)
        entries = []

        while root_dir_block_id < root_dir_end_block_id:
            # read all entries of each block of size DIR_ENTRY_SIZE
            entries += FatDirEntry.get_entries_from_root_block(root_dir_block)

            root_dir_block_id += 1
            root_dir_block = fs.cache.read(root_dir_block_id)

        return entries

    @staticmethod
    def get_index_and_block_for_new_fde(fs):
        """Return block and index in block with empty space for write new file"""
        root_dir_block_id = BOOT_BLOCK_SIZE + FAT_BLOCK_SIZE  # first block of root dir
        root_dir_end_block_id = root_dir_block_id + fs.root_directory_blocks  # last block of root dir
        root_dir_block = fs.cache.read(root_dir_block_id)

        while root_dir_block_id < root_dir_end_block_id:
            max_files = 0

            for file_dir_entry in range(0, BLOCK_SIZE, DIR_ENTRY_SIZE):
                # if number of files is same as number of possible clusters
                if max_files is FAT_MAX_CLUSTERS:
                    break

                binary_file_data = FatDirEntry.read_single_fat_dir_entry(file_dir_entry,
                                                                         file_dir_entry + DIR_ENTRY_SIZE,
                                                                         root_dir_block.data)

                # if next file does not contain bytes
                if binary_file_data == bytearray([0x00] * DIR_ENTRY_SIZE):
                    return file_dir_entry, root_dir_block_id

                max_files += 1

            root_dir_block_id += 1
            root_dir_block = fs.cache.read(root_dir_block_id)
        return None

    @staticmethod
    def read_dir(fs):
        """Return list of files in (root) directory"""
        files = FatDirEntry.read_root_dir(fs)
        return [entry.file_name for entry in files]

    @staticmethod
    def get_fat_entry(fs, file_name):
        """Return one FatDirEntry"""
        entries = FatDirEntry.read_root_dir(fs)
        fat_entry = [entry for entry in entries if entry == file_name]
        if len(fat_entry) > 0:
            return fat_entry[0]

    @staticmethod
    def create_new_fat_dir_entry(fs, file_name):
        """Create instance of FatDirEntry"""

        # find empty position for cluster
        new_cluster_id = fs.get_empty_cluster()
        if new_cluster_id is None:
            return
        # write EOC to new cluster
        fs.write_next_cluster_to_cluster(new_cluster_id, EOC_CLUSTER)
        fde = FatDirEntry(file_name, new_cluster_id, 1)

        # find block and empty position for FatDirEntry in it
        free_idx, block_with_free_place = FatDirEntry.get_index_and_block_for_new_fde(fs)

        root_block = fs.cache.read(block_with_free_place)       # read root block
        root_block.put_single_data(free_idx, fde.to_binary())   # write new FatDirEntry to root block
        fs.cache.write(block_with_free_place, root_block.data)  # write new block to virtual drive

        return fde

    @staticmethod
    def open(fs, file_name):
        fde = FatDirEntry.get_fat_entry(fs, file_name)
        return fde if fde is not None else FatDirEntry.create_new_fat_dir_entry(fs, file_name)

    @staticmethod
    def delete_fde_from_root_directory(fs, fat_dir_entry):
        entries = FatDirEntry.read_root_dir(fs)
        if not fat_dir_entry in entries:
            return
        fde_index = entries.index(fat_dir_entry)
        # number of fat_dir_entries in one block
        files_for_one_block = int(BLOCK_SIZE / DIR_ENTRY_SIZE)
        # index of the block in which fde is
        index_of_block = fs.first_root_directory_block() + floor(fde_index / files_for_one_block)
        # index of byte from where we will start deleting
        index_in_block = DIR_ENTRY_SIZE * (fde_index % files_for_one_block)

        empty_dir = bytearray([0] * DIR_ENTRY_SIZE)

        root_block = fs.cache.read(index_of_block)              # read root block
        root_block.put_single_data(index_in_block, empty_dir)   # write new empty FatDirEntry
        fs.cache.write(index_of_block, root_block.data)         # write new block to virtual drive

    @staticmethod
    def file_delete(fs, file_name):
        """Set bytes in the data block to zero and deletes file from FAT block"""
        fde = FatDirEntry.get_fat_entry(fs, file_name)

        if not fde:
            return

        file_clusters = fs.get_file_clusters(fde.fst_cluster_id)
        empty_data_for_cluster = bytearray([0] * fs.blocks_per_clust * BLOCK_SIZE)

        for cluster in file_clusters:
            fs.data_cluster_write(cluster, empty_data_for_cluster)
            fs.write_value_to_cluster(cluster, EMPTY_CLUSTER)

        FatDirEntry.delete_fde_from_root_directory(fs, fde)

