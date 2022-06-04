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
    echo "  -h, --help          display this help info"
}

TEMP=$( \
    getopt \
        -n $(basename "$0") \
        -o hd: \
        --long help,device: \
        -- "$@"
    )

if [ $? != 0 ]; then echo "Terminating..." >&2; exit 1; fi

eval set -- "$TEMP"

while true; do
    case "$1" in
        -d|--device)    device="$2"             ; shift 2   ;;
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

sudo mount "$device" "$dest"
for fn in CONFIG.TXT config/*; do
    git diff --no-index "$dest/$fn" "$fn"
done
sudo umount "$dest"
