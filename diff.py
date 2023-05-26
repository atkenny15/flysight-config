#!/usr/bin/env python3

import argparse
import pathlib
import subprocess
import sys

from typing import List

from common import mount_device, get_mount_destination, unmount_device


def main(argv: List[str]) -> None:
    parser = argparse.ArgumentParser(description="Diff flysight configs with device")
    parser.add_argument(
        "--device",
        "-d",
        default="/dev/sdb1",
        type=str,
        help="flysight device",
    )
    parser.add_argument(
        "--mount",
        "-m",
        default=False,
        action="store_true",
        help="skip mount/umount",
    )
    args = parser.parse_args(argv)

    dest = None
    if not args.mount:
        dest = mount_device(args.device)

    if dest is None:
        dest = get_mount_destination()

    try:
        filenames = ["CONFIG.TXT"]
        for config_file in pathlib.Path("config").iterdir():
            filenames.append(str(config_file))

        for filename in filenames:
            subprocess.run(
                [
                    "git",
                    "--no-pager",
                    "diff",
                    "--no-index",
                    f"{dest}/{filename}",
                    filename,
                ]
            )
    finally:
        if not args.mount:
            unmount_device(args.device)


if __name__ == "__main__":
    main(sys.argv[1:])
