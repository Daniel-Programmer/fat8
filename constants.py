BLOCK_SIZE = 512

FILE_NAME_MAX_SIZE = 11
DIR_ENTRY_SIZE = FILE_NAME_MAX_SIZE + 5     # file name + id of first cluster (1B) + size of file (4B)

BOOT_BLOCK_SIZE = 1

FAT_BLOCK_SIZE = 1

EMPTY_CLUSTER = 0xff
# end of chain
EOC_CLUSTER = 0xfe
FAT_MAX_CLUSTERS = 254

STRUCT_BUFFER = 16

