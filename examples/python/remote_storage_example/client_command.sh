#!/bin/bash

# buf sizes
# 33554432
# 16777216
# 8388608
# 4194304
# 2097152
# 1048576
# 524288

export CUFILE_ENV_PATH_JSON="/workspace/nixl-tim/examples/python/remote_storage_example/cufile.json"

python3 nixl_p2p_storage_example.py --fileprefix /raid/scratch/testfiles/client --role client --agents_file agent_file.in --name client1 --batch_size 128 --buf_size 2097152
