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
        nargs="?",
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
        lat = float(split[0].strip())
        lon = float(split[1].strip())

    config_path = FILE_PATH / "CONFIG.TXT"
    with config_path.open() as fh:
        lines = fh.readlines()

    ref_rx = re.compile(";\s*ref_name\s*:\s+(?P<name>.+?)\s*$")
    lat_lon_rx = re.compile(
        "^\s*(?P<disabled>;)?\s*Reference_(?P<lat_lon>Lat|Lon)F?\s*:\s*(?P<value>-?[\d.]+)(?:\s+.*?)?$"
    )

    found = False
    last_ref = -1

    is_first = True
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        name_matches = ref_rx.search(line)
        new_lines.append(line)
        i += 1

        if name_matches:
            disp = [line]

            name_match = None
            if args.name is not None:
                name_match = name_matches.group("name") == args.name
                if name_match:
                    found = True

            is_disabled = False
            while i < len(lines):
                lat_lon_matches = lat_lon_rx.search(lines[i])

                if not lat_lon_matches:
                    break

                if name_match is None:
                    s = ""
                    if lat_lon_matches.group("disabled"):
                        s = ";"
                else:
                    s = ""
                    if not name_match:
                        s = ";"

                is_disabled = False
                if s == ";":
                    is_disabled = True

                val = lat_lon_matches.group("value")

                if name_match:
                    if lat_lon_matches.group("lat_lon") == "Lat":
                        if lat is not None:
                            val = lat
                    if lat_lon_matches.group("lat_lon") == "Lon":
                        if lon is not None:
                            val = lon

                temp = "{}Reference_{}F: {}".format(
                    s, lat_lon_matches.group("lat_lon"), val
                )
                new_lines.append(temp)
                disp.append(temp)

                i += 1

            last_ref = len(new_lines)

            if not is_first:
                print()
            is_first = False

            for s in disp:
                if is_disabled:
                    print(s)
                else:
                    print(f"\x1b[36m{s}\x1b[0m")

    if args.name is not None:
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
                        f"Reference_LatF: {lat}",
                        f"Reference_LonF: {lon}",
                    ]
                    print("\n".join(add))
                    new_lines.extend(add)

        print("\n\x1b[32;1mUpdating config file\x1b[0m")
        with config_path.open("w") as fh:
            fh.write("\n".join(new_lines) + "\n")
    else:
        print("\n\x1b[31;1mSkipping config file\x1b[0m")


if __name__ == "__main__":
    main(sys.argv[1:])
