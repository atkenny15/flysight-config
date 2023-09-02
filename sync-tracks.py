#!/usr/bin/env python3

import argparse
import os
import pathlib
import re
import subprocess
import sys

from typing import List

from common import mount_device, get_mount_destination, unmount_device


def main(argv: List[str]) -> None:
    parser = argparse.ArgumentParser(description="Template")
    parser.add_argument(
        "--device",
        "-d",
        default="/dev/sdb1",
        type=str,
        help="flysight device",
    )
    parser.add_argument(
        "--dest",
        default="~/flysight/tracks",
        type=str,
        help="destinatino directory",
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
    parser.add_argument(
        "--source",
        "-s",
        default="2",
        type=str,
        help="source string to copy",
    )
    args = parser.parse_args(argv)

    mount_dest = None
    if not args.mount:
        mount_dest = mount_device(args.device)

    if mount_dest is None:
        mount_dest = get_mount_destination()

    try:
        fs1_rx = re.compile("^Processor serial number: (\w+)\s*$")
        fs2_rx = re.compile("^Device_ID:\s+(\w+)\s*$")
        flysight_text_path = mount_dest / "FLYSIGHT.TXT"

        serial_number = None
        with flysight_text_path.open() as fh:
            for line in fh:
                matches = fs1_rx.search(line)
                if matches:
                    serial_number = matches.group(1)
                matches = fs2_rx.search(line)
                if matches:
                    serial_number = matches.group(1)

        if serial_number is None:
            raise Exception("Could not determine serial number")

        dest = pathlib.Path(os.path.expanduser(args.dest))

        if not dest.exists():
            dest.mkdir()

        dry_run = ""
        if args.dry_run:
            dry_run = "--dry-run"

        cmd = f'rsync {dry_run} --archive --verbose --partial --progress "{mount_dest}"/{args.source}* "{dest}/{serial_number}/"'

        display_file(flysight_text_path)
        print(cmd)
        subprocess.run(cmd, check=True, shell=True)
        display_file(flysight_text_path)
    finally:
        if not args.mount:
            unmount_device(args.device)


def display_file(path: pathlib.Path) -> None:
    with path.open() as fh:
        print(f"==> {path} <==")
        print(fh.read())


if __name__ == "__main__":
    main(sys.argv[1:])
