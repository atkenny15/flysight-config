#!/usr/bin/env python3

import argparse
import re
import shlex
import sys

from typing import List

from common import mount_device, get_mount_destination, run_command, unmount_device


def main(argv: List[str]) -> None:
    parser = argparse.ArgumentParser(description="Sync flysight configs to device")
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
    parser.add_argument(
        "--dry-run",
        "-n",
        default=False,
        action="store_true",
        help="dry run",
    )
    args = parser.parse_args(argv)

    dry_run = ""
    if args.dry_run:
        dry_run = "--dry-run"

    mount_dest = None
    if not args.mount:
        mount_dest = mount_device(args.device)

    if mount_dest is None:
        mount_dest = get_mount_destination()

    try:
        rx = re.compile("^Firmware version: ([\w-]+)\s*$")

        fw_ver = None
        with mount_dest.joinpath("FLYSIGHT.TXT").open() as fh:
            for line in fh:
                print(line.rstrip())
                matches = rx.search(line)
                if matches:
                    fw_ver = matches.group(1)

        if fw_ver is None:
            raise Exception("Could not determine firmware version")

        if fw_ver.endswith("pos-leds"):
            if not config_is_perf():
                raise Exception("Expected a performance config")
        else:
            if config_is_perf():
                raise Exception("Did not expect a performance config")

        run_command(
            shlex.split(
                f"rsync -iva {dry_run} --progress --stats --no-o --no-g --no-p CONFIG.TXT config '{mount_dest}/'"
            )
        )
    finally:
        if not args.mount:
            unmount_device(args.device)


def config_is_perf() -> bool:
    with open("CONFIG.TXT") as fh:
        for line in fh:
            if re.search("^\s*Time_After_Exit", line):
                return True
    return False


if __name__ == "__main__":
    main(sys.argv[1:])
