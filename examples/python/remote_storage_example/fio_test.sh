#!/bin/bash

fio --name=sequential_write_test --rw=read --bs=4k --numjobs=1 --size=1G --filename=/workspace/testfiles/fio_test --iodepth=1
