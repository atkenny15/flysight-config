import getpass
import pathlib
import re
import shlex
import subprocess

from typing import List


def run_command(cmd: List[str]) -> None:
    print(shlex.join(cmd))
    subprocess.run(cmd, check=True)


def mount_device(device: pathlib.Path) -> pathlib.Path:
    cmd = ["udisksctl", "mount", "-b", str(device)]
    print(shlex.join(cmd))
    proc = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, encoding="utf-8")

    rx = re.compile("^Mounted (.+?) at (.+?)\s*$", re.M)
    matches = rx.search(proc.stdout)
    if not matches:
        print(f"STDOUT >>>>>>>\n{proc.stdout}<<<<<<<")
        raise Exception("Could not parse command output")

    return pathlib.Path(matches.group(2))


def unmount_device(device: pathlib.Path) -> None:
    run_command(["udisksctl", "unmount", "-b", str(device)])


def get_mount_destination() -> pathlib.Path:
    media_path = pathlib.Path(f"/media/{getpass.getuser()}")
    paths = [p for p in media_path.iterdir() if p.is_dir()]

    if len(paths) == 0:
        raise Exception(f"No directories found in: {media_path}")
    elif len(paths) != 1:
        raise Exception(f"Multiple directories found in: {media_path}: {paths}")

    return paths[0]
