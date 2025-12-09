#!/usr/bin/env python3

# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import argparse

import torch

from nixl._api import nixl_agent, nixl_agent_config
from nixl.logging import get_logger
import nixl_utils as nixl_utils

logger = get_logger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, required=True)
    parser.add_argument("--port", type=int, default=5555)
    parser.add_argument("--use_cuda", type=bool, default=False)
    parser.add_argument(
        "--mode",
        type=str,
        default="initiator",
        help="Local IP in target, peer IP (target's) in initiator",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # initiator use default port
    listen_port = args.port
    if args.mode != "target":
        listen_port = 0

    if args.use_cuda:
        torch.set_default_device("cuda:0")
    else:  # To be sure this is the default
        torch.set_default_device("cpu")

    config = nixl_agent_config(True, True, listen_port)

    # Allocate memory and register with NIXL
    agent = nixl_agent(args.mode, config)

    # Use a single 2D tensor with 10 tensors of size 16
    if args.mode == "target":
        tensor = [(nixl_utils.malloc_passthru(10 * 16 * 4), 10 * 16 * 4, 0, "test")]
        logger.info(
            "Running test with tensor shape %s in mode %s", tensor[0][1], args.mode
        )
    else:
        tensor = torch.ones((10, 16), dtype=torch.float32)
        logger.info(
            "Running test with tensor shape %s in mode %s", tuple(tensor.shape), args.mode
        )

    # Register the single 2D tensor
    reg_descs = agent.register_memory(tensor)
    if not reg_descs:
        logger.error("Memory registration failed.")
        exit(1)

    # Target code
    if args.mode == "target":
        ready = False

        # Build transfer descriptors by unraveling first dim into list of row tensors
        target_rows = [tensor[i, :] for i in range(tensor.shape[0])]
        target_descs = agent.get_xfer_descs(target_rows)
        if not target_descs:
            logger.error("Failed to build target transfer descriptors.")
            exit(1)
        target_desc_str = agent.get_serialized_descs(target_descs)

        # Send desc list to initiator when metadata is ready
        while not ready:
            ready = agent.check_remote_metadata("initiator")
        agent.send_notif("initiator", target_desc_str)

        logger.info("Waiting for transfer")

        # Waiting for transfer
        while True:
            notifs = agent.get_new_notifs()
            if "initiator" in notifs and b"Done_reading" in notifs["initiator"]:
                logger.info("Transfer done, verifying data")
                nixl_utils.verify_transfer(tensor, 1, 10 * 16 * 4)
                logger.info("Data verification passed")
                break

    # Initiator code
    else:
        logger.info("Initiator sending to %s", args.ip)
        agent.fetch_remote_metadata("target", args.ip, args.port)
        agent.send_local_metadata(args.ip, args.port)

        notifs = agent.get_new_notifs()
        while len(notifs) == 0:
            notifs = agent.get_new_notifs()
        target_descs = agent.deserialize_descs(notifs["target"][0])

        # Build local transfer descriptors by unraveling first dim into list of row tensors
        initiator_rows = [tensor[i, :] for i in range(tensor.shape[0])]
        initiator_descs = agent.get_xfer_descs(initiator_rows)
        if not initiator_descs:
            logger.error("Initiator's local descriptors creation failed.")
            exit(1)

        # Ensure remote metadata has arrived from fetch
        ready = False
        while not ready:
            ready = agent.check_remote_metadata("target")

        logger.info("Ready for transfer")

        xfer_handle = agent.initialize_xfer(
            "WRITE", initiator_descs, target_descs, "target", "Done_writing"
        )

        # Should block until transfer is done
        state = agent.device_transfer(xfer_handle)
        if state == "ERR":
            logger.error("Posting transfer failed.")
            exit(1)

    # Tear down
    if args.mode != "target":
        agent.remove_remote_agent("target")
        agent.release_xfer_handle(xfer_handle)
        agent.invalidate_local_metadata(args.ip, args.port)

    agent.deregister_memory(reg_descs)

    logger.info("Test Complete.")
