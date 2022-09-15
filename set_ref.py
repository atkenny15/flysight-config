#!/usr/bin/env python3

import argparse
import pathlib
import re
import sys

from typing import List

FILE_PATH = pathlib.Path(__file__).resolve().parent


def main(argv: List[str]) -> None:
    parser = argparse.ArgumentParser(description="Template")
    parser.add_argument(
        "name",
        default=None,
        type=str,
        help="delete messages where From matches regex",
    )
    parser.add_argument(
        "lat_lon",
        default=None,
        nargs="?",
        type=str,
        help="delete messages where From matches regex",
    )
    args = parser.parse_args(argv)

    scale = 1e7

    # 41.13584680086071, -80.17918302239264
    lat = None
    lon = None
    if args.lat_lon is not None:
        split = args.lat_lon.split(",")
        if len(split) != 2:
            raise Exception(f"Invalid lat/lon: '{args.lat_lon}'")
        lat = int(round(float(split[0].strip()) * scale))
        lon = int(round(float(split[1].strip()) * scale))

    config_path = FILE_PATH / "CONFIG.TXT"
    with config_path.open() as fh:
        lines = fh.readlines()

    ref_rx = re.compile(";\s*ref_name\s*:\s+(.+?)\s*$")
    lat_lon_rx = re.compile("^\s*;?\s*Reference_(Lat|Lon)\s*:\s*(-?\d+)(?:\s+.*?)?$")

    found = False
    last_ref = -1

    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        name_matches = ref_rx.search(line)
        new_lines.append(line)
        i += 1

        if name_matches:
            print(line)

            name_match = name_matches.group(1) == args.name
            if name_match:
                found = True

            while i < len(lines):
                lat_lon_matches = lat_lon_rx.search(lines[i])

                if not lat_lon_matches:
                    break

                s = ""
                if not name_match:
                    s = ";"

                val = int(lat_lon_matches.group(2))

                if name_match:
                    if lat_lon_matches.group(1) == "Lat":
                        if lat is not None:
                            val = lat
                    if lat_lon_matches.group(1) == "Lon":
                        if lon is not None:
                            val = lon

                temp = "{}Reference_{}: {:10}".format(s, lat_lon_matches.group(1), val)
                new_lines.append(temp)
                print(temp)

                i += 1

            last_ref = len(new_lines)

    if not found:
        if lat is None or lon is None:
            raise Exception(
                f"Missing lat/lon argument for new reference point '{args.name}'"
            )

        if last_ref < 0:
            raise Exception("Could not find any reference points")

        backup = new_lines
        new_lines = []

        i = 0
        while i < len(backup):
            new_lines.append(backup[i])
            i += 1
            if i == last_ref:
                add = [
                    "",
                    f"; ref_name: {args.name}",
                    f"Reference_Lat: {lat:10}",
                    f"Reference_Lon: {lon:10}",
                ]
                print("\n".join(add))
                new_lines.extend(add)

    with config_path.open("w") as fh:
        fh.write("\n".join(new_lines) + "\n")


if __name__ == "__main__":
    main(sys.argv[1:])
