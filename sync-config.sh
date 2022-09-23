#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

set -euo pipefail

dest="/mnt/temp1"
device="/dev/sdb1"
function print_help() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -d, --device=DEV    flysight device ($device)"
    echo "      --dest=PATH     destination directory ($dest)"
    echo "  -m, --mount         skip mount/umount"
    echo "  -n, --dry-run       dry run"
    echo "  -h, --help          display this help info"
}

TEMP=$( \
    getopt \
        -n $(basename "$0") \
        -o hnd:m \
        --long help,dry-run,device:,mount \
        -- "$@"
    )

if [ $? != 0 ]; then echo "Terminating..." >&2; exit 1; fi

eval set -- "$TEMP"

dry_run=
mount=true
while true; do
    case "$1" in
        -d|--device)    device="$2"             ; shift 2   ;;
        -n|--dry-run)   dry_run="--dry-run"     ; shift     ;;
        -m|--mount)     mount=false             ; shift     ;;
        -h|--help)      print_help              ; exit 0    ;;
        --)             shift                   ; break     ;;
        *)              echo "Internal error!"  ; exit 1    ;;
    esac
done

num_req=0
if [[ $# -ne $num_req ]]; then
    print_help
    echo "ERROR: Script requires $num_req arguments, but got $#"
    exit 1
fi

set -x

cd "${DIR}"

if $mount; then
    sudo mount -o umask=000 "$device" "$dest"
fi
rsync -iva $dry_run --progress --stats --no-o --no-g --no-p CONFIG.TXT config "$dest/"
if $mount; then
    sudo umount "$dest"
fi
