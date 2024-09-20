class Block:
    """Data block for cache"""
    def __init__(self, block_id, ready_to_delete=False, data=None):
        self.data = data
        self.block_id = block_id
        self.ready_to_delete = ready_to_delete

    def __eq__(self, other):
        if isinstance(other, Block):
            return self.block_id == other.block_id
        return False

    def put_single_data(self, index, data):
        arr = bytearray(self.data)
        for i in range(len(data)):
            arr[index + i] = data[i]
        self.data = bytes(arr)

