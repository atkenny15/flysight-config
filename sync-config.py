#!/usr/bin/env python3

import argparse
import re
import shlex
import subprocess
import sys

from typing import List


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
        default="/mnt/temp1",
        type=str,
        help="destination directory",
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

    if not args.mount:
        run_command(
            shlex.split(f"sudo mount -o umask=000 '{args.device}' '{args.dest}'")
        )

    try:
        rx = re.compile("^Firmware version: ([\w-]+)\s*$")

        fw_ver = None
        with open(f"{args.dest}/FLYSIGHT.TXT") as fh:
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
                f"rsync -iva {dry_run} --progress --stats --no-o --no-g --no-p CONFIG.TXT config '{args.dest}/'"
            )
        )
    finally:
        if not args.mount:
            run_command(shlex.split(f"sudo umount '{args.dest}'"))


def run_command(cmd: List[str]):
    print(shlex.join(cmd))
    subprocess.run(cmd, check=True)


def config_is_perf() -> bool:
    with open("CONFIG.TXT") as fh:
        for line in fh:
            if re.search("^\s*Time_After_Exit", line):
                return True
    return False


if __name__ == "__main__":
    main(sys.argv[1:])
