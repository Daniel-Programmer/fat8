from math import ceil

from constants import *


class FatFd:
    """File decriptor for working with FatFile"""
    def __init__(self, fs, fat_dir_entry):
        self.fs = fs
        self.fat_dir_entry = fat_dir_entry
        self.current_cluster = self.fat_dir_entry.fst_cluster_id

        self.file_size = self.fat_dir_entry.size * self.fs.blocks_per_clust * BLOCK_SIZE  # size of file in bytes
        self.file_offset = 0     # current position in file = position

        self.buffer = None       # buffer with loaded data
        self._load_file_to_buffer()

    def _load_file_to_buffer(self):
        self.buffer = bytearray()
        fst_cluster_id = self.fat_dir_entry.fst_cluster_id
        clusters = self.fs.get_file_clusters(fst_cluster_id)
        for cluster in clusters:
            self.buffer.extend(self.fs.data_cluster_read(cluster))

    def _write_buffer_to_drive(self):
        if len(self.buffer) != self.file_size:
            raise BufferError('Buffer is not same length as file, please update file length')
        file_clusters = self.fs.get_file_clusters(self.fat_dir_entry.fst_cluster_id)
        data_index_start = 0
        data_index_end = BLOCK_SIZE * self.fs.blocks_per_clust
        data = self.buffer
        for cluster in file_clusters:
            self.fs.data_cluster_write(cluster, data[data_index_start:data_index_end])
            data_index_start += data_index_end
            data_index_end += BLOCK_SIZE * self.fs.blocks_per_clust

    def _extend_clusters(self, current_clusters, new_clusters):
        number_of_clusters_to_add = new_clusters - current_clusters

        last_cluster = self.fs.get_last_cluster(self.fat_dir_entry.fst_cluster_id)
        empty_clusters = self.fs.get_empty_clusters()

        for idx in range(number_of_clusters_to_add):
            self.fs.write_next_cluster_to_cluster(last_cluster, empty_clusters[idx])
            last_cluster = empty_clusters[idx]

        self.fs.write_next_cluster_to_cluster(last_cluster, EOC_CLUSTER)
        self.fat_dir_entry.size = new_clusters
        self.file_size = new_clusters * self.fs.blocks_per_clust * BLOCK_SIZE

    def _shrink_clusters(self, current_clusters, new_clusters):
        number_of_clusters_to_remove = current_clusters - new_clusters

        file_clusters = self.fs.get_file_clusters(self.fat_dir_entry.fst_cluster_id)
        clusters_to_remove = file_clusters[len(file_clusters) - number_of_clusters_to_remove:]
        new_eoc_cluster_id = file_clusters[len(file_clusters) - number_of_clusters_to_remove - 1]

        # empty clusters
        for index in range(number_of_clusters_to_remove):
            self.fs.write_value_to_cluster(clusters_to_remove[index], EMPTY_CLUSTER)
        # set end of chain
        self.fs.write_value_to_cluster(new_eoc_cluster_id, EOC_CLUSTER)

        self.fat_dir_entry.size = new_clusters
        self.file_size = new_clusters * self.fs.blocks_per_clust * BLOCK_SIZE

    def truncate(self, size):
        current_cluster_count = int(self.file_size / (self.fs.blocks_per_clust * BLOCK_SIZE))
        new_cluster_count = ceil(size / (self.fs.blocks_per_clust * BLOCK_SIZE))

        if current_cluster_count < new_cluster_count:
            self._extend_clusters(current_cluster_count, new_cluster_count)
            return self._load_file_to_buffer()
        elif current_cluster_count > new_cluster_count:
            self._shrink_clusters(current_cluster_count, new_cluster_count)
            return self._load_file_to_buffer()
        return None

    def seek(self, position):
        if position > self.file_size or position < 0:
            raise IndexError("Position is out of range of file")
        self.file_offset = position

    def stat(self):
        return self.file_size

    def tell(self):
        return self.file_offset

    def read(self, size):
        offset = self.file_offset
        if size > self.file_size - offset:
            return ''
        self.file_offset += size
        return self.buffer[offset: offset + size].decode('utf-8').rstrip('\0')

    def write(self, data):
        position = self.file_offset
        remaining_file_space = self.file_size - position
        data_len = len(data)
        if remaining_file_space < data_len:
            data_len - remaining_file_space
            # extend file with data that overflows
            self.truncate(self.file_size + data_len - remaining_file_space)
            self.file_offset = position

        idx = self.file_offset
        # insert data to do buffer
        byte_array = bytearray(data, 'utf-8')
        for byte in byte_array:
            self.buffer[idx] = byte
            idx += 1
        # write data from buffer to virtual drive
        self._write_buffer_to_drive()
