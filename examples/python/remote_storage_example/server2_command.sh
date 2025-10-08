#!/bin/bash

# buf sizes
# 33554432
# 16777216
# 8388608
# 4194304
# 2097152
# 1048576
# 524288

python3 nixl_p2p_storage_example.py --fileprefix /raid/scratch/testfiles/target2 --role server --port 8889 --name target2 --batch_size 32 --buf_size 33554432
