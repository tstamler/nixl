#!/bin/bash

# buf sizes
# 33554432
# 16777216

python3 nixl_p2p_storage_example.py --fileprefix /raid/scratch/testfiles/client --role client --agents_file agent_file.in --name client1 --batch_size 32 --buf_size 33554432
